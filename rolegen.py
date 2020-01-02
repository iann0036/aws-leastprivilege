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
        self.region = args.region

        self.cfnclient = boto3.client(
            'cloudformation', region_name=self.region)
        self.simple_permissions = []
        self.complex_permissions = []
        self.skipped_types = []
        self.accountid = boto3.client(
            'sts', region_name=self.region).get_caller_identity()['Account']

    def generate(self):
        if self.input_file:
            with open(self.input_file, "r", encoding="utf-8") as f:
                try:
                    template = json.loads(to_json(f.read()))
                except:
                    raise InvalidTemplate("Invalid template (could not parse)")
        else:
            raise InvalidArguments("No template provided")

        if "Resources" not in template:
            raise InvalidArguments("Resources not in template")

        for resname, res in template["Resources"].items():
            self.get_permissions(resname, res)

        statement = []
        if len(self.simple_permissions):
            statement.append({
                "Sid": "generic",
                "Effect": "Allow",
                "Action": list(set(self.simple_permissions)),
                "Resource": "*"
            })
        statement += self.complex_permissions

        policy = {
            "PolicyName": "root",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": statement
            }
        }

        if len(self.skipped_types) > 0:
            print("WARNING: Skipped the following types: {}\n".format(
                ", ".join(list(set(self.skipped_types)))))

        print(json.dumps(policy, indent=4, separators=(',', ': ')))

        list(set(self.simple_permissions))

    def _get_property_or_default(self, res, notfoundvalue, *propertypath):
        value = '*'

        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return notfoundvalue
            
            if isinstance(relpath, str): # TODO: Other primitive types
                value = relpath
            elif isinstance(relpath, list):
                for listitem in relpath:
                    if not isinstance(listitem, str):
                        return value
                value = relpath

        return value

    def get_permissions(self, resname, res):
        if res["Type"] == "AWS::Lambda::Function":
            functionname = self._get_property_or_default(res, "*", "FunctionName")
            role = self._get_property_or_default(res, "*", "Role")
            s3bucket = self._get_property_or_default(res, None, "Code", "S3Bucket")
            s3key = self._get_property_or_default(res, None, "Code", "S3Key")
            kmskeyarn = self._get_property_or_default(res, None, "KmsKeyArn")
            reservedconcurrentexecutions = self._get_property_or_default(res, None, "ReservedConcurrentExecutions")
            layers = self._get_property_or_default(res, None, "Layers")
            securitygroupids = self._get_property_or_default(res, None, "VpcConfig", "SecurityGroupIds")
            subnetids = self._get_property_or_default(res, None, "VpcConfig", "SubnetIds")

            self.complex_permissions.append({
                'Sid': resname + '-create1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:CreateFunction'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            self.complex_permissions.append({
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
                self.complex_permissions.append({
                    'Sid': resname + '-create3',
                    'Effect': 'Allow',
                    'Action': [
                        's3:GetObject'
                    ],
                    'Resource': 'arn:aws:s3:::{}/{}'.format(s3bucket, s3key)
                })
            if kmskeyarn:
                self.complex_permissions.append({
                    'Sid': resname + '-create4',
                    'Effect': 'Allow',
                    'Action': [
                        'kms:Encrypt',
                        'kms:CreateGrant'
                    ],
                    'Resource': kmskeyarn
                })
            if reservedconcurrentexecutions:
                self.complex_permissions.append({
                    'Sid': resname + '-create5',
                    'Effect': 'Allow',
                    'Action': [
                        'lambda:PutFunctionConcurrency'
                    ],
                    'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
                })
            if layers:
                self.complex_permissions.append({
                    'Sid': resname + '-create6',
                    'Effect': 'Allow',
                    'Action': [
                        'lambda:GetLayerVersion'
                    ],
                    'Resource': layers
                })
            if securitygroupids and subnetids:
                self.complex_permissions.append({
                    'Sid': resname + '-create7',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:DescribeVpcs',
                        'ec2:DescribeSubnets',
                        'ec2:DescribeSecurityGroups'
                    ],
                    'Resource': '*'
                })
            self.complex_permissions.append({
                'Sid': resname + '-createnm1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:GetFunction'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            self.complex_permissions.append({
                'Sid': resname + '-update1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:UpdateFunctionConfiguration'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            self.complex_permissions.append({
                'Sid': resname + '-delete1',
                'Effect': 'Allow',
                'Action': [
                    'lambda:DeleteFunction'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
            if securitygroupids and subnetids:
                self.complex_permissions.append({
                    'Sid': resname + '-delete2',
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:DescribeNetworkInterfaces'
                    ],
                    'Resource': '*'
                })
        else:
            self.get_remote_permissions_for_type(res["Type"])

    def get_remote_permissions_for_type(self, restype):
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

        for handler in ["create", "delete", "list", "read", "update"]:
            if handler in type_schema["handlers"] and "permissions" in type_schema["handlers"][handler]:
                self.simple_permissions += type_schema["handlers"][handler]["permissions"]
