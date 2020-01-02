import boto3
import json
from cfn_flip import to_json


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
            print("WARNING: Skipped the following types: {}\n".format(
                ", ".join(list(set(self.skipped_types)))))
        
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
        if res["Type"] == "AWS::Lambda::Function":
            functionname = self._get_property_or_default(
                res, "*", "FunctionName")
            role = self._get_property_or_default(res, "*", "Role")
            s3bucket = self._get_property_or_default(
                res, None, "Code", "S3Bucket")
            s3key = self._get_property_or_default(res, None, "Code", "S3Key")
            kmskeyarn = self._get_property_or_default(res, None, "KmsKeyArn")
            reservedconcurrentexecutions = self._get_property_or_default(
                res, None, "ReservedConcurrentExecutions")
            layers = self._get_property_or_default(res, None, "Layers")
            securitygroupids = self._get_property_or_default(
                res, None, "VpcConfig", "SecurityGroupIds")
            subnetids = self._get_property_or_default(
                res, None, "VpcConfig", "SubnetIds")

            self.permissions.append({
                'Sid': resname + '-create1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:CreateFunction'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            self.permissions.append({
                'Sid': resname + '-create2',
                'Effect': 'Allow',
                'Action': [
                    'iam:PassRole'
                ],
                'Resource': role,
                'Condition': {
                    'StringEquals': {
                        'iam:PassedToService': 'lambda.amazonaws.com'
                    }
                }
            })
            if s3bucket and s3key:
                self.permissions.append({
                    'Sid': resname + '-create3',
                    'Effect': 'Allow',
                    'Action': [
                        's3:GetObject'
                    ],
                    'Resource': 'arn:aws:s3:::{}/{}'.format(s3bucket, s3key)
                })
            if kmskeyarn:
                self.permissions.append({
                    'Sid': resname + '-create4',
                    'Effect': 'Allow',
                    'Action': [
                        'kms:Encrypt',
                        'kms:CreateGrant'
                    ],
                    'Resource': kmskeyarn
                })
            if reservedconcurrentexecutions:
                self.permissions.append({
                    'Sid': resname + '-create5',
                    'Effect': 'Allow',
                    'Action': [
                        'lambda:PutFunctionConcurrency'
                    ],
                    'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
                })
            if layers:
                self.permissions.append({
                    'Sid': resname + '-create6',
                    'Effect': 'Allow',
                    'Action': [
                        'lambda:GetLayerVersion'
                    ],
                    'Resource': layers
                })
            if securitygroupids and subnetids:
                self.permissions.append({
                    'Sid': resname + '-create7',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:DescribeVpcs',
                        'ec2:DescribeSubnets',
                        'ec2:DescribeSecurityGroups'
                    ],
                    'Resource': '*'
                })
            self.permissions.append({
                'Sid': resname + '-createnm1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:GetFunction'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            if not self.skip_update_policy:
                self.permissions.append({
                    'Sid': resname + '-update1',
                    'Effect': 'Allow',
                    'Action': [
                        'lambda:UpdateFunctionConfiguration'
                    ],
                    'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
                })
            self.permissions.append({
                'Sid': resname + '-delete1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:DeleteFunction'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            if securitygroupids and subnetids:
                self.permissions.append({
                    'Sid': resname + '-delete2',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:DescribeNetworkInterfaces'
                    ],
                    'Resource': '*'
                })
        elif res["Type"] == "AWS::EC2::SecurityGroup":
            vpcid = self._get_property_or_default(res, None, "VpcId")
            securitygroupingress_len = self._get_property_array_length(res, None, "SecurityGroupIngress")
            securitygroupegress_len = self._get_property_array_length(res, None, "SecurityGroupEgress")
            tags_len = self._get_property_array_length(res, None, "Tags")

            self.permissions.append({
                'Sid': resname + '-create1',
                'Effect': 'Allow',
                'Action': [
                    'ec2:DescribeSecurityGroups',
                    'ec2:CreateSecurityGroup'
                ],
                'Resource': '*'
            })
            if securitygroupegress_len:
                # Explanation: when a security group is created in a VPC, the default Egress is 0.0.0.0/0 Allow
                # so cfn will perform a RevokeSecurityGroupEgress immediately after create
                self.permissions.append({
                    'Sid': resname + '-create2',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:AuthorizeSecurityGroupEgress',
                        'ec2:RevokeSecurityGroupEgress'
                    ],
                    'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                })
            # Explanation: will always tag with CloudFormation tags
            self.permissions.append({
                'Sid': resname + '-create3',
                'Effect': 'Allow',
                'Action': [
                    'ec2:CreateTags'
                ],
                'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            })
            if securitygroupingress_len:
                self.permissions.append({
                    'Sid': resname + '-create4',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:AuthorizeSecurityGroupIngress'
                    ],
                    'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                })
                if not self.skip_update_policy:
                    self.permissions.append({
                        'Sid': resname + '-update1',
                        'Effect': 'Allow',
                        'Action': [
                            'ec2:RevokeSecurityGroupIngress'
                        ],
                        'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                    })
            if tags_len and not self.skip_update_policy:
                self.permissions.append({
                    'Sid': resname + '-update2',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:DeleteTags'
                    ],
                    'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                })
            else:
                self.permissions.append({
                    'Sid': resname + '-delete1',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:DeleteTags'
                    ],
                    'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                })
            self.permissions.append({
                'Sid': resname + '-delete2',
                'Effect': 'Allow',
                'Action': [
                    'ec2:DeleteSecurityGroup'
                ],
                'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            })
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
