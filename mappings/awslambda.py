# Note: File naming altered to not conflict with Python's built-in `lambda()`
class AWSLambdaFunctionPermissions:
    def get_permissions(self, resname, res):
        functionname = self._get_property_or_default(res, "*", "FunctionName")
        role = self._get_property_or_default(res, "*", "Role")
        s3bucket = self._get_property_or_default(res, None, "Code", "S3Bucket")
        s3key = self._get_property_or_default(res, None, "Code", "S3Key")
        s3objectversion = self._get_property_or_default(res, None, "Code", "S3ObjectVersion")
        kmskeyarn = self._get_property_or_default(res, None, "KmsKeyArn")
        reservedconcurrentexecutions = self._get_property_or_default(res, None, "ReservedConcurrentExecutions")
        layers = self._get_property_or_default(res, None, "Layers")
        securitygroupids = self._get_property_or_default(res, None, "VpcConfig", "SecurityGroupIds")
        subnetids = self._get_property_or_default(res, None, "VpcConfig", "SubnetIds")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'lambda:CreateFunction'
            ],
            'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
        })
        self.permissions.append({
            'Sid': '{}-create2'.format(resname),
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
            if s3objectversion:
                self.permissions.append({
                    'Sid': '{}-create3'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        's3:GetObjectVersion'
                    ],
                    'Resource': 'arn:aws:s3:::{}/{}'.format(s3bucket, s3key),
                    'Condition': {
                        'StringEquals': {
                            's3:VersionId': s3objectversion
                        }
                    }
                })
            else:
                self.permissions.append({
                    'Sid': '{}-create4'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        's3:GetObject'
                    ],
                    'Resource': 'arn:aws:s3:::{}/{}'.format(s3bucket, s3key)
                })
        if kmskeyarn:
            self.permissions.append({
                'Sid': '{}-create5'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'kms:Encrypt',
                    'kms:CreateGrant'
                ],
                'Resource': kmskeyarn
            })
        if reservedconcurrentexecutions:
            self.permissions.append({
                'Sid': '{}-create6'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'lambda:PutFunctionConcurrency'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
        if layers:
            self.permissions.append({
                'Sid': '{}-create7'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'lambda:GetLayerVersion'
                ],
                'Resource': layers
            })
        if securitygroupids and subnetids:
            self.permissions.append({
                'Sid': '{}-create8'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'ec2:DescribeVpcs',
                    'ec2:DescribeSubnets',
                    'ec2:DescribeSecurityGroups'
                ],
                'Resource': '*'
            })
        self.permissions.append({
            'Sid': '{}-createnm1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'lambda:GetFunction'
            ],
            'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
        })
        if not self.skip_update_actions:
            self.permissions.append({
                'Sid': '{}-update1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'lambda:UpdateFunctionConfiguration',
                    'lambda:UpdateFunctionCode'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
        self.permissions.append({
            'Sid': '{}-delete1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'lambda:DeleteFunction'
            ],
            'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
        })
        if securitygroupids and subnetids:
            self.permissions.append({
                'Sid': '{}-delete2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'ec2:DescribeNetworkInterfaces'
                ],
                'Resource': '*'
            })

class AWSLambdaVersionPermissions:
    def get_permissions(self, resname, res):
        functionname = self._get_property_or_default(res, "*", "FunctionName").split(":").pop() # could be an arn or partial arn
        provisionedconcurrentexecutions = self._get_property_or_default(res, None, "ProvisionedConcurrencyConfig", "ProvisionedConcurrentExecutions")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'lambda:ListVersionsByFunction',
                'lambda:PublishVersion'
            ],
            'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
        })
        if provisionedconcurrentexecutions:
            self.permissions.append({
                'Sid': '{}-create2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'lambda:GetProvisionedConcurrencyConfig',
                    'lambda:PutProvisionedConcurrencyConfig'
                ],
                'Resource': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            })
        self.permissions.append({
            'Sid': '{}-delete1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'lambda:DeleteFunction'
            ],
            'Resource': 'arn:aws:lambda:{}:{}:function:{}:*'.format(self.region, self.accountid, functionname)
        })
