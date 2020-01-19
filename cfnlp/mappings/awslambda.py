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

        condition = None
        if layers and layers != '*':
            condition = {
                'ForAllValues:StringLike': {
                    'lambda:Layer': self._forcelist(layers)
                }
            }

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'lambda:CreateFunction'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            ],
            conditions=condition
        )
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'iam:PassRole'
            ],
            resources=[
                role
            ],
            conditions={
                'StringEquals': {
                    'iam:PassedToService': 'lambda.amazonaws.com'
                },
                'StringLike': {
                    'iam:AssociatedResourceArn': 'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
                }
            }
        )
        if s3bucket and s3key:
            if s3objectversion and s3objectversion != '*':
                self.permissions.add(
                    resname=resname,
                    lifecycle='Create',
                    actions=[
                        's3:GetObjectVersion'
                    ],
                    resources=[
                        'arn:aws:s3:::{}/{}'.format(s3bucket, s3key)
                    ],
                    conditions={
                        'StringEquals': {
                            's3:VersionId': s3objectversion
                        }
                    }
                )
            else:
                self.permissions.add(
                    resname=resname,
                    lifecycle='Create',
                    actions=[
                        's3:GetObject'
                    ],
                    resources=[
                        'arn:aws:s3:::{}/{}'.format(s3bucket, s3key)
                    ]
                )
        if kmskeyarn:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'kms:Encrypt',
                ],
                resources=[
                    kmskeyarn
                ],
                conditions={
                    'StringEquals': {
                        'kms:CallerAccount': self.accountid
                    },
                    'StringLike': {
                        'kms:ViaService': 'lambda.*.amazonaws.com'
                    }
                }
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'kms:CreateGrant'
                ],
                resources=[
                    kmskeyarn
                ],
                conditions={
                    'StringEquals': {
                        'kms:CallerAccount': self.accountid
                    },
                    'StringLike': {
                        'kms:ViaService': 'lambda.*.amazonaws.com'
                    },
                    'Bool': {
                        'kms:GrantIsForAWSResource': True
                    }
                }
            )
        if reservedconcurrentexecutions:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'lambda:PutFunctionConcurrency'
                ],
                resources=[
                    'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
                ]
            )
        if layers:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'lambda:GetLayerVersion'
                ],
                resources=self._forcelist(layers)
            )
        if securitygroupids and subnetids:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:DescribeVpcs',
                    'ec2:DescribeSubnets',
                    'ec2:DescribeSecurityGroups'
                ],
                resources=['*']
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'lambda:GetFunction'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            ],
            nonmandatory=True
        )
        self.permissions.add(
            resname=resname,
            lifecycle='Update',
            actions=[
                'lambda:UpdateFunctionConfiguration'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            ]
        )
        self.permissions.add(
            resname=resname,
            lifecycle='Update',
            actions=[
                'lambda:UpdateFunctionCode'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            ]
        )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'lambda:DeleteFunction'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            ]
        )
        if securitygroupids and subnetids:
            self.permissions.add(
                resname=resname,
                lifecycle='Delete',
                actions=[
                    'ec2:DescribeNetworkInterfaces'
                ],
                resources=['*']
            )

class AWSLambdaVersionPermissions:
    def get_permissions(self, resname, res):
        functionname = self._get_property_or_default(res, "*", "FunctionName").split(":").pop() # could be an arn or partial arn
        provisionedconcurrentexecutions = self._get_property_or_default(res, None, "ProvisionedConcurrencyConfig", "ProvisionedConcurrentExecutions")

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'lambda:ListVersionsByFunction',
                'lambda:PublishVersion'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
            ]
        )
        if provisionedconcurrentexecutions:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'lambda:GetProvisionedConcurrencyConfig', # undocumented
                    'lambda:PutProvisionedConcurrencyConfig'
                ],
                resources=[
                    'arn:aws:lambda:{}:{}:function:{}'.format(self.region, self.accountid, functionname)
                ]
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'lambda:DeleteFunction'
            ],
            resources=[
                'arn:aws:lambda:{}:{}:function:{}:*'.format(self.region, self.accountid, functionname)
            ]
        )