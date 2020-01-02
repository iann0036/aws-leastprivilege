import boto3
import json
import sys
from cfn_flip import to_json

from mappings.ec2 import *
from mappings.awslambda import *


class InvalidArguments(Exception):
    pass


class InvalidTemplate(Exception):
    pass


class RoleGen:
    def __init__(self, args):
        self.input_file = args.input_file
        self.stack_name = args.stack_name
        self.skip_update_policy = args.skip_update_policy
        self.region = args.region or boto3.session.Session().region_name or 'us-east-1'

        self.cfnclient = boto3.client(
            'cloudformation', region_name=self.region)
        self.permissions = []
        self.skipped_types = []
        self.accountid = boto3.client(
            'sts', region_name=self.region).get_caller_identity()['Account']

    def generate(self):
        if self.input_file:
            try:
                with open(self.input_file, "r", encoding="utf-8") as f:
                    template = json.loads(to_json(f.read()))
            except:
                raise InvalidTemplate("Invalid template (could not parse)")
        elif self.stack_name:
            try:
                template_body = self.cfnclient.get_template(
                    StackName=self.stack_name,
                    TemplateStage='Processed'
                )['TemplateBody']
                template = json.loads(to_json(template_body))
            except:
                raise InvalidTemplate("Could not retrieve remote stack")
        else:
            raise InvalidArguments("No template provided")

        if "Resources" not in template:
            raise InvalidArguments("Resources not in template")

        for resname, res in template["Resources"].items():
            self.get_permissions(resname, res)

        policy = {
            "PolicyName": "root",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": self.permissions
            }
        }

        if len(self.skipped_types) > 0:
            sys.stderr.write("WARNING: Skipped the following types: {}\n".format(
                ", ".join(list(set(self.skipped_types)))))

        if len(json.dumps(policy, separators=(',', ': '))) > 10240:
            sys.stderr.write("WARNING: The generated policy size is greater than the maximum 10240 character limit\n")
        
        print(json.dumps(policy, indent=4, separators=(',', ': ')))

    def _get_property_or_default(self, res, notfoundvalue, *propertypath):
        value = '*'

        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return notfoundvalue

            if isinstance(relpath, str):  # TODO: Other primitive types
                value = relpath
            elif isinstance(relpath, list):
                for listitem in relpath:
                    if not isinstance(listitem, str):
                        return value
                value = relpath

        return value

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

    def get_permissions(self, resname, res):
        mapped_classname = "{}Permissions".format(str(res["Type"]).replace("::",""))
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
        if not self.skip_update_policy:
            handler_types.append("update")
        handler_types.append("delete") # ordering important

        for handler in handler_types:
            if handler in type_schema["handlers"] and "permissions" in type_schema["handlers"][handler]:
                self.permissions.append({
                    'Sid': '{}-{}1-reg'.format(resname, handler),
                    'Effect': 'Allow',
                    'Action': list(set(type_schema["handlers"][handler]["permissions"])),
                    'Resource': '*'
                })
