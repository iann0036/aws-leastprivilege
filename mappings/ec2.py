class AWSEC2SecurityGroupPermissions:
    def get_permissions(self, resname, res):
        vpcid = self._get_property_or_default(res, None, "VpcId")
        securitygroupingress_len = self._get_property_array_length(res, None, "SecurityGroupIngress")
        securitygroupegress_len = self._get_property_array_length(res, None, "SecurityGroupEgress")
        tags_len = self._get_property_array_length(res, None, "Tags")

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:DescribeSecurityGroups',
                'ec2:CreateSecurityGroup'
            ],
            resources=['*']
        )
        if securitygroupegress_len:
            # Explanation: when a security group is created in a VPC, the default Egress is 0.0.0.0/0 Allow
            # so cfn will perform a RevokeSecurityGroupEgress immediately after create
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:AuthorizeSecurityGroupEgress',
                    'ec2:RevokeSecurityGroupEgress'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ]
            )
        # Explanation: will always tag with CloudFormation tags
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:CreateTags'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ]
        )
        if securitygroupingress_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:AuthorizeSecurityGroupIngress'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ]
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:RevokeSecurityGroupIngress'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ]
            )
        if tags_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:DeleteTags'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ]
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'ec2:DeleteTags'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ]
        )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'ec2:DeleteSecurityGroup'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ]
        )
