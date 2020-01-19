import boto3
import json
import sys
from cfn_flip import to_json

from .mappings.awslambda import *
from .mappings.cloudwatch import *
from .mappings.ec2 import *
from .mappings.iam import *
from .mappings.s3 import *
from .mappings.sns import *
from .mappings.sqs import *


class InvalidArguments(Exception):
    pass


class InvalidTemplate(Exception):
    pass


class PermissionsManager:
    def __init__(self, include_update_actions):
        self.include_update_actions = include_update_actions
        self.tracked_permissions = []
        self.tracked_lifecycle_count = {}

    def add(self, resname, lifecycle, actions, resources, conditions=None, nonmandatory=False, registry=False):
        if not resname in self.tracked_lifecycle_count:
            self.tracked_lifecycle_count[resname] = {
                'Create': 0,
                'Update': 0,
                'Delete': 0
            }

        self.tracked_lifecycle_count[resname][lifecycle]+=1

        non_mandatory_str = ''
        if nonmandatory:
            non_mandatory_str = '-nm'
        registry_str = ''
        if registry:
            registry_str = '-reg'
        
        if lifecycle != "Update" or not self.include_update_actions:
            tracked_permission = {
                'Sid': '{}-{}{}{}{}'.format(resname, lifecycle, self.tracked_lifecycle_count[resname][lifecycle], non_mandatory_str, registry_str),
                'Effect': 'Allow',
                'Action': actions,
                'Resource': resources
            }
            if conditions:
                tracked_permission['Condition'] = conditions

            self.tracked_permissions.append(tracked_permission)

    def generate(self, consolidate_permissions):
        output_permissions = self.tracked_permissions 

        if consolidate_permissions:
            output_permissions = self.consolidate_permissions(self.tracked_permissions)

        for i, permission in enumerate(output_permissions):
            if len(permission['Action']) == 1:
                output_permissions[i]['Action'] = permission['Action'][0]
            if len(permission['Resource']) == 1:
                output_permissions[i]['Resource'] = permission['Resource'][0]

        return {
            "PolicyName": "root",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": output_permissions
            }
        }

    def consolidate_permissions(self, permissions):
        # TODO: Consolidate for same action, different resource and for combining wildcard w/ specific
        new_permissions = []

        while len(permissions):
            permission = permissions.pop(0)
            permission.pop('Sid', None)

            i = 0
            while i < len(permissions):
                if (
                    permissions[i]['Resource'] == permission['Resource'] and
                    permissions[i]['Effect'] == permission['Effect'] and
                    (
                        ('Condition' not in permissions[i] and 'Condition' not in permission) or
                        ('Condition' in permissions[i] and 'Condition' in permission and
                         permissions[i]['Condition'] == permission['Condition'])
                    )
                ):
                    permission['Action'] += permissions[i]['Action']
                    permissions.pop(i)
                else:
                    i += 1

            permission['Action'] = sorted(set(permission['Action']))  # remove duplicates
            new_permissions.append(permission)

        return new_permissions


class RoleGen:
    def __init__(self, args):
        self.input_file = args.input_file
        self.stack_name = args.stack_name
        self.profile = args.profile
        self.include_update_actions = args.include_update_actions
        self.consolidate_policy = args.consolidate_policy
        self.region = args.region or boto3.session.Session().region_name or 'us-east-1'
        self.template = None
        self.permissions = PermissionsManager(self.include_update_actions)
        self.skipped_types = []

        session = boto3.session.Session(
            profile_name=self.profile,
            region_name=self.region
        )

        self.cfnclient = session.client('cloudformation')
        self.accountid = session.client('sts').get_caller_identity()['Account']

    def generate(self):
        if self.input_file:
            try:
                with open(self.input_file, "r", encoding="utf-8") as f:
                    self.template = json.loads(to_json(f.read()))
            except:
                raise InvalidTemplate("Invalid template (could not parse)")
        elif self.stack_name:
            try:
                template_body = self.cfnclient.get_template(
                    StackName=self.stack_name,
                    TemplateStage='Processed'
                )['TemplateBody']
                self.template = json.loads(to_json(template_body))
            except:
                raise InvalidTemplate("Could not retrieve remote stack")
        else:
            raise InvalidArguments("No template provided")

        if "Resources" not in self.template:
            raise InvalidArguments("Resources not in template")

        for resname, res in self.template["Resources"].items():
            self.get_permissions(resname, res)

        policy = self.permissions.generate(self.consolidate_policy)

        if len(self.skipped_types) > 0:
            sys.stderr.write("WARNING: Skipped the following types: {}\n".format(
                ", ".join(sorted(set(self.skipped_types)))))

        if len(json.dumps(policy, separators=(',', ': '))) > 10240:
            sys.stderr.write(
                "WARNING: The generated policy size is greater than the maximum 10240 character limit\n")

        return json.dumps(policy, indent=4, separators=(',', ': '))

    def _forcelist(self, prop):
        if isinstance(prop, list):
            return prop
        
        return prop

    def _get_property_or_default(self, res, notfoundvalue, *propertypath):
        value = '*'

        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return notfoundvalue

            relpath = self._resolve_intrinsics(relpath)

            if isinstance(relpath, str) or isinstance(relpath, bool) or isinstance(relpath, int): # TODO: Other primitive types
                value = relpath
            elif isinstance(relpath, list):
                for listitem in relpath:
                    if not isinstance(listitem, str):
                        return value
                value = relpath

        return value

    def _resolve_intrinsics(self, prop):
        if isinstance(prop, dict):
            # TODO: is Ref possible?

            if 'Fn::ImportValue' in prop:
                importvalue = self._resolve_intrinsics(prop['Fn::ImportValue'])
                if isinstance(importvalue, str):
                    exports_paginator = self.cfnclient.get_paginator('list_exports').paginate()
                    for exports_page in exports_paginator:
                        for export in exports_page['Exports']:
                            if export['Name'] == importvalue:
                                return export['Value']

            # TODO: Other intrinsics
        
        return prop

    def _get_property_array_length(self, res, notfoundvalue, *propertypath):
        value = 0

        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return notfoundvalue

            if isinstance(relpath, list):
                value = len(relpath)

        return value

    def _get_property_exists(self, res, *propertypath):
        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return False

        return True

    def get_permissions(self, resname, res):
        mapped_classname = "{}Permissions".format(
            str(res["Type"]).replace("::", ""))
        if mapped_classname in globals():
            globals()[mapped_classname].get_permissions(self, resname, res)
        else:
            self.get_remote_permissions_for_type(resname, res["Type"])

    def get_remote_permissions_for_type(self, resname, restype):
        remote_type_def = self.cfnclient.describe_type(
            Type='RESOURCE',
            TypeName=restype
        )

        if remote_type_def['DeprecatedStatus'] != "LIVE":
            self.skipped_types.append(restype)
            return

        type_schema = json.loads(remote_type_def['Schema'])
        if "handlers" not in type_schema:
            self.skipped_types.append(restype)
            return

        handler_types = ["create"]
        if self.include_update_actions:
            handler_types.append("update")
        handler_types.append("delete")  # ordering important

        for handler in handler_types:
            if handler in type_schema["handlers"] and "permissions" in type_schema["handlers"][handler]:
                self.permissions.add(
                    resname=resname,
                    lifecycle=handler[0].upper() + handler[1:],
                    actions=sorted(set(type_schema["handlers"][handler]["permissions"])),
                    resources=['*'],
                    registry=True
                )
