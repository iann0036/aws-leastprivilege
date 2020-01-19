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
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
            if vpcid and vpcid != "*":
                condition['StringEquals']['ec2:Vpc'] = vpcid
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:AuthorizeSecurityGroupEgress',
                    'ec2:RevokeSecurityGroupEgress'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )
        # Explanation: will always tag with CloudFormation tags
        condition = {
            'StringEquals': {
                'ec2:Region': self.region
            }
        }
        if vpcid and vpcid != "*":
            condition['StringEquals']['ec2:Vpc'] = vpcid
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:CreateTags'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ],
            conditions=condition
        )
        if securitygroupingress_len:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
            if vpcid and vpcid != "*":
                condition['StringEquals']['ec2:Vpc'] = vpcid
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:AuthorizeSecurityGroupIngress'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:RevokeSecurityGroupIngress'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                ],
                conditions={
                    'StringEquals': {
                        'ec2:Region': self.region
                    }
                }
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
                ],
                conditions={
                    'StringEquals': {
                        'ec2:Region': self.region
                    }
                }
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'ec2:DeleteTags'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ],
            conditions={
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
        )
        condition = {
            'StringEquals': {
                'ec2:Region': self.region
            }
        }
        if vpcid and vpcid != "*":
            condition['StringEquals']['ec2:Vpc'] = vpcid
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'ec2:DeleteSecurityGroup'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ],
            conditions=condition
        )

class AWSEC2InstancePermissions:
    def get_permissions(self, resname, res):
        availabilityzone = self._get_property_or_default(res, None, "AvailabilityZone")
        ebsoptimized = self._get_property_or_default(res, False, "EbsOptimized")
        tenancy = self._get_property_or_default(res, "default", "Tenancy")
        instancetype = self._get_property_or_default(res, "m1.small", "InstanceType")
        iaminstanceprofile = self._get_property_or_default(res, None, "IamInstanceProfile")
        launchtemplate_exists = self._get_property_exists(res, "LaunchTemplate")
        launchtemplateid = self._get_property_or_default(res, None, "LaunchTemplate", "LaunchTemplateId")
        placementgroupname = self._get_property_or_default(res, None, "PlacementGroupName")

        condition = {
            'StringEquals': {
                'ec2:IsLaunchTemplateResource': False,
                'ec2:Region': self.region
                # 'ec2:RootDeviceType'
                # 'ec2:MetadataHttpEndpoint'
                # 'ec2:MetadataHttpTokens'
                # 'ec2:MetadataHttpPutResponseHopLimit'
            }
        }
        if availabilityzone and availabilityzone != '*':
            condition['StringEquals']['ec2:AvailabilityZone'] = availabilityzone
        if ebsoptimized != '*':
            if 'Bool' not in condition:
                condition['Bool'] = {}
            condition['Bool']['ec2:EbsOptimized'] = str(ebsoptimized).lower()
        if tenancy != '*':
            condition['StringEquals']['ec2:Tenancy'] = tenancy
        if instancetype != '*':
            condition['StringEquals']['ec2:InstanceType'] = instancetype
        if iaminstanceprofile and iaminstanceprofile != '*':
            condition['StringEquals']['ec2:InstanceProfile'] = iaminstanceprofile
        if launchtemplate_exists:
            if 'Bool' not in condition:
                condition['Bool'] = {}
            condition['Bool']['ec2:IsLaunchTemplateResource'] = "true"
        if launchtemplateid and launchtemplateid != '*':
            condition['StringEquals']['ec2:LaunchTemplate'] = 'arn:aws:ec2:{}:{}:launch-template/{}'.format(self.region, self.accountid, launchtemplateid)
        if placementgroupname and placementgroupname != '*':
            condition['StringEquals']['ec2:PlacementGroup'] = 'arn:aws:ec2:{}:{}:placement-group/{}'.format(self.region, self.accountid, placementgroupname)
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:RunInstances'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid)
            ],
            conditions=condition
        )
        