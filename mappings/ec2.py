class AWSEC2SecurityGroupPermissions:
    def get_permissions(self, resname, res):
        vpcid = self._get_property_or_default(res, None, "VpcId")
        securitygroupingress_len = self._get_property_array_length(res, None, "SecurityGroupIngress")
        securitygroupegress_len = self._get_property_array_length(res, None, "SecurityGroupEgress")
        tags_len = self._get_property_array_length(res, None, "Tags")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
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
                'Sid': '{}-create2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'ec2:AuthorizeSecurityGroupEgress',
                    'ec2:RevokeSecurityGroupEgress'
                ],
                'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            })
        # Explanation: will always tag with CloudFormation tags
        self.permissions.append({
            'Sid': '{}-create3'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'ec2:CreateTags'
            ],
            'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
        })
        if securitygroupingress_len:
            self.permissions.append({
                'Sid': '{}-create4'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'ec2:AuthorizeSecurityGroupIngress'
                ],
                'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            })
            if self.include_update_actions:
                self.permissions.append({
                    'Sid': '{}-update1'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'ec2:RevokeSecurityGroupIngress'
                    ],
                    'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                })
        if tags_len and self.include_update_actions:
            self.permissions.append({
                'Sid': '{}-update2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'ec2:DeleteTags'
                ],
                'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            })
        else:
            self.permissions.append({
                'Sid': '{}-delete1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'ec2:DeleteTags'
                ],
                'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            })
        self.permissions.append({
            'Sid': '{}-delete2'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'ec2:DeleteSecurityGroup'
            ],
            'Resource': 'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
        })
