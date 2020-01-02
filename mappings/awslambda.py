# Note: File naming altered to not conflict with Python's built-in `lambda()`
from mappings.base import BasePermissions

class AWSLambdaFunctionPermissions(BasePermissions):
    def get_permissions(self, resname, res):
        functionname = self._get_property_or_default(res, "*", "FunctionName")
        role = self._get_property_or_default(res, "*", "Role")
        s3bucket = self._get_property_or_default(res, None, "Code", "S3Bucket")
        s3key = self._get_property_or_default(res, None, "Code", "S3Key")
        kmskeyarn = self._get_property_or_default(res, None, "KmsKeyArn")
        reservedconcurrentexecutions = self._get_property_or_default(res, None, "ReservedConcurrentExecutions")
        layers = self._get_property_or_default(res, None, "Layers")
        securitygroupids = self._get_property_or_default(res, None, "VpcConfig", "SecurityGroupIds")
        subnetids = self._get_property_or_default(res, None, "VpcConfig", "SubnetIds")

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
