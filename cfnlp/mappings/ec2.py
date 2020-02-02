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
        subnetid = self._get_property_or_default(res, None, "SubnetId")
        imageid = self._get_property_or_default(res, "*", "ImageId")
        networkinterfaces_len = self._get_property_array_length(res, None, "NetworkInterfaces")
        securitygroupids_len = self._get_property_array_length(res, None, "SecurityGroupIds")
        securitygroups_len = self._get_property_array_length(res, None, "SecurityGroups")
        blockdevicemappings_len = self._get_property_array_length(res, None, "BlockDeviceMappings")
        volumes_len = self._get_property_array_length(res, None, "Volumes")
        keyname = self._get_property_or_default(res, None, "KeyName")
        tags_len = self._get_property_array_length(res, None, "Tags")
        userdata_exists = self._get_property_exists(res, "UserData")
        disableapitermination_exists = self._get_property_exists(res, "DisableApiTermination")
        ebsoptimized_exists = self._get_property_exists(res, "EbsOptimized")
        elasticgpuspecifications_len = self._get_property_array_length(res, None, "ElasticGpuSpecifications")
        elasticinferenceaccelerators_len = self._get_property_array_length(res, None, "ElasticInferenceAccelerators")
        monitoring_exists = self._get_property_exists(res, "Monitoring")
        monitoring = self._get_property_or_default(res, None, "Monitoring")

        condition = {
            'StringEquals': {
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
        
        condition = {
            'StringEquals': {
                'ec2:Region': self.region
            }
        }
        if availabilityzone and availabilityzone != '*':
            condition['StringEquals']['ec2:AvailabilityZone'] = availabilityzone
        if subnetid and subnetid != '*':
            condition['StringEquals']['ec2:Subnet'] = 'arn:aws:ec2:{}:{}:subnet/{}'.format(self.region, self.accountid, subnetid)
        networkinterface_resources = [
            'arn:aws:ec2:{}:{}:network-interface/*'.format(self.region, self.accountid)
        ]
        subnet_resources = [
            'arn:aws:ec2:{}:{}:subnet/*'.format(self.region, self.accountid)
        ]
        securitygroup_resources = [
            'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
        ]
        subnet_permissions_required = True
        if networkinterfaces_len and not launchtemplate_exists: # a launch template may have any subnet, nic, sg
            subnet_permissions_required = False
            networkinterface_resources = []
            for networkinterface in res['Properties']['NetworkInterfaces']:
                if 'NetworkInterfaceId' in networkinterface and isinstance(networkinterface['NetworkInterfaceId'], str):
                    networkinterface_resources.append('arn:aws:ec2:{}:{}:network-interface/{}'.format(self.region, self.accountid, networkinterface['NetworkInterfaceId']))
                else:
                    subnet_permissions_required = True
                    networkinterface_resources = [
                        'arn:aws:ec2:{}:{}:network-interface/*'.format(self.region, self.accountid)
                    ]
                    break
            for networkinterface in res['Properties']['NetworkInterfaces']:
                if 'SubnetId' in networkinterface and isinstance(networkinterface['SubnetId'], str):
                    subnet_resources.append('arn:aws:ec2:{}:{}:subnet/{}'.format(self.region, self.accountid, networkinterface['SubnetId']))
                else:
                    subnet_resources = [
                        'arn:aws:ec2:{}:{}:subnet/*'.format(self.region, self.accountid)
                    ]
                    break
            for networkinterface in res['Properties']['NetworkInterfaces']:
                if 'GroupSet' in networkinterface and isinstance(networkinterface['GroupSet'], list):
                    for securitygroupid in networkinterface['GroupSet']:
                        if isinstance(securitygroupid, str):
                            securitygroup_resources.append('arn:aws:ec2:{}:{}:security-group/{}'.format(self.region, self.accountid, securitygroupid))
                        else:
                            securitygroup_resources = [
                                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                            ]
                            break
                else:
                    securitygroup_resources = [
                        'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                    ]
                    break
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:RunInstances'
            ],
            resources=networkinterface_resources,
            conditions=condition
        )
        
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:RunInstances'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:image/{}'.format(self.region, self.accountid, imageid)
            ],
            conditions={
                'StringEquals': {
                    'ec2:Region': self.region
                }
                # ec2:RootDeviceType
                # ec2:ImageType
            }
        )

        if securitygroups_len:
            securitygroup_resources = [
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
            ]
        elif securitygroupids_len:
            for securitygroupid in res['Properties']['SecurityGroupIds']:
                if isinstance(securitygroupid, str):
                    securitygroup_resources.append('arn:aws:ec2:{}:{}:security-group/{}'.format(self.region, self.accountid, securitygroupid))
                else:
                    securitygroup_resources = [
                        'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid)
                    ]
                    break
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:RunInstances'
            ],
            resources=securitygroup_resources,
            conditions={
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
        )

        if subnet_permissions_required:
            if subnetid and subnetid != '*':
                subnet_resources = [
                    'arn:aws:ec2:{}:{}:subnet/{}'.format(self.region, self.accountid, subnetid)
                ]
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
            if availabilityzone and availabilityzone != '*':
                condition['StringEquals']['ec2:AvailabilityZone'] = availabilityzone
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=subnet_resources,
                conditions=condition
            )

        condition = {
            'StringEquals': {
                # ec2:AvailabilityZone
                'ec2:Region': self.region
            }
        }
        volume_resources = [
            'arn:aws:ec2:{}:{}:volume/*'.format(self.region, self.accountid)
        ]
        snapshot_resources = [
            'arn:aws:ec2:{}:{}:snapshot/*'.format(self.region, self.accountid)
        ]
        volume_permissions_required = True
        snapshot_permissions_required = False
        if blockdevicemappings_len:
            volume_permissions_required = False
            for blockdevicemapping in res['Properties']['BlockDeviceMappings']:
                if 'DeviceName' not in blockdevicemapping:
                    volume_permissions_required = True
                    break
                if 'Ebs' in blockdevicemapping:
                    volume_permissions_required = True
                    if 'VolumeType' in blockdevicemapping['Ebs'] and isinstance(blockdevicemapping['Ebs']['VolumeType'], str):
                        if 'ec2:VolumeType' not in condition['StringEquals']:
                            condition['StringEquals']['ec2:VolumeType'] = []
                        condition['StringEquals']['ec2:VolumeType'].append(blockdevicemapping['Ebs']['VolumeType'])
                        condition['StringEquals']['ec2:VolumeType'] = sorted(set(condition['StringEquals']['ec2:VolumeType'])) # remove duplicates
                    if 'VolumeSize' in blockdevicemapping['Ebs'] and isinstance(blockdevicemapping['Ebs']['VolumeSize'], str):
                        if 'ec2:VolumeSize' not in condition['StringEquals']:
                            condition['StringEquals']['ec2:VolumeSize'] = []
                        condition['StringEquals']['ec2:VolumeSize'].append(blockdevicemapping['Ebs']['VolumeSize'])
                        condition['StringEquals']['ec2:VolumeSize'] = sorted(set(condition['StringEquals']['ec2:VolumeSize'])) # remove duplicates
                    if 'Iops' in blockdevicemapping['Ebs'] and isinstance(blockdevicemapping['Ebs']['Iops'], str):
                        if 'ec2:VolumeIops' not in condition['StringEquals']:
                            condition['StringEquals']['ec2:VolumeIops'] = []
                        condition['StringEquals']['ec2:VolumeIops'].append(blockdevicemapping['Ebs']['Iops'])
                        condition['StringEquals']['ec2:VolumeIops'] = sorted(set(condition['StringEquals']['ec2:VolumeIops'])) # remove duplicates
                    if 'Encrypted' in blockdevicemapping['Ebs'] and (isinstance(blockdevicemapping['Ebs']['Encrypted'], bool) or isinstance(blockdevicemapping['Ebs']['Encrypted'], str)):
                        if 'Bool' not in condition:
                            condition['Bool'] = {}
                        if 'ec2:Encrypted' not in condition['Bool']:
                            condition['Bool']['ec2:Encrypted'] = []
                        condition['Bool']['ec2:Encrypted'].append(str(blockdevicemapping['Ebs']['Encrypted']).lower())
                        condition['Bool']['ec2:Encrypted'] = sorted(set(condition['Bool']['ec2:Encrypted'])) # remove duplicates
                    if 'SnapshotId' in blockdevicemapping['Ebs'] and isinstance(blockdevicemapping['Ebs']['SnapshotId'], str):
                        if 'ec2:ParentSnapshot' not in condition['StringEquals']:
                            condition['StringEquals']['ec2:ParentSnapshot'] = []
                        condition['StringEquals']['ec2:ParentSnapshot'].append(blockdevicemapping['Ebs']['SnapshotId'])
                        condition['StringEquals']['ec2:ParentSnapshot'] = sorted(set(condition['StringEquals']['ec2:ParentSnapshot'])) # remove duplicates
                        if not snapshot_permissions_required:
                            snapshot_resources = []
                            snapshot_permissions_required = True
                        snapshot_resources.append('arn:aws:ec2:{}:{}:snapshot/{}'.format(self.region, self.accountid, blockdevicemapping['Ebs']['SnapshotId']))
                    elif 'SnapshotId' in blockdevicemapping['Ebs'] and not isinstance(blockdevicemapping['Ebs']['SnapshotId'], str):
                        snapshot_resources = [
                            'arn:aws:ec2:{}:{}:snapshot/*'.format(self.region, self.accountid)
                        ]
                        snapshot_permissions_required = True
        if volume_permissions_required:
            if volumes_len:
                volume_resources = []
                for volume in res['Properties']['Volumes']:
                    if 'VolumeId' not in volume:
                        volume_resources = [
                            'arn:aws:ec2:{}:{}:volume/*'.format(self.region, self.accountid)
                        ]
                        break
                    else:
                        volume_resources.append('arn:aws:ec2:{}:{}:volume/{}'.format(self.region, self.accountid, volume['VolumeId']))
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=volume_resources,
                conditions=condition
            )
        if snapshot_permissions_required:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=snapshot_resources,
                conditions={
                    'StringEquals': {
                        'ec2:Region': self.region
                    }
                }
            )

        if keyname:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:key-pair/{}'.format(self.region, self.accountid, keyname)
                ],
                conditions={
                    'StringEquals': {
                        'ec2:Region': self.region
                    }
                }
            )

        if launchtemplate_exists:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
            if 'Bool' not in condition:
                condition['Bool'] = {}
            condition['Bool']['ec2:IsLaunchTemplateResource'] = "true"
            if launchtemplateid and launchtemplateid != "*":
                condition['StringEquals']['ec2:LaunchTemplate'] = 'arn:aws:ec2:{}:{}:launch-template/{}'.format(self.region, self.accountid, launchtemplateid)
            launchtemplate_resources = [
                'arn:aws:ec2:{}:{}:launch-template/{}'.format(self.region, self.accountid, launchtemplateid or '*'),
                'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid), # TODO: ?
                'arn:aws:ec2:{}:{}:image/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:network-interface/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:security-group/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:subnet/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:volume/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:key-pair/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:placement-group/*'.format(self.region, self.accountid),
                'arn:aws:ec2:{}:{}:snapshot/*'.format(self.region, self.accountid)
            ]

            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=launchtemplate_resources,
                conditions=condition
            )

        if placementgroupname and placementgroupname != "*":
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:placement-group/{}'.format(self.region, self.accountid, placementgroupname)
                ],
                conditions={
                    'StringEquals': {
                        'ec2:Region': self.region
                        # ec2:PlacementGroupStrategy
                    }
                }
            )

        if iaminstanceprofile:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:PassRole'
                ],
                resources=[
                    '*'
                ],
                conditions={
                    'StringEquals': {
                        'iam:PassedToService': 'ec2.amazonaws.com'
                    }
                }
            )

        if elasticgpuspecifications_len:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region,
                    'ec2:ElasticGpuType': []
                }
            }
            for elasticgpuspecification in res['Properties']['ElasticGpuSpecifications']:
                if 'Type' in elasticgpuspecification and isinstance(elasticgpuspecification['Type'], str):
                    condition['StringEquals']['ec2:ElasticGpuType'].append(elasticgpuspecification['Type'])
                else:
                    condition = None
                    break
            
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:elastic-gpu/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )

        if elasticinferenceaccelerators_len:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region,
                    'elastic-inference:ElasticInferenceAcceleratorType': []
                }
            }
            for elasticinferenceaccelerator in res['Properties']['ElasticInferenceAccelerators']:
                if 'Type' in elasticinferenceaccelerator and isinstance(elasticinferenceaccelerator['Type'], str):
                    condition['StringEquals']['elastic-inference:ElasticInferenceAcceleratorType'].append(elasticinferenceaccelerator['Type'])
                else:
                    condition = None
                    break
            
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:RunInstances'
                ],
                resources=[
                    'arn:aws:elastic-inference:{}:{}:elastic-inference-accelerator/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )

        if tags_len:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                    # 'ec2:RootDeviceType'
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
            if placementgroupname and placementgroupname != '*':
                condition['StringEquals']['ec2:PlacementGroup'] = 'arn:aws:ec2:{}:{}:placement-group/{}'.format(self.region, self.accountid, placementgroupname)
            
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:CreateTags'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:DeleteTags'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )

        if volumes_len:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                    # 'ec2:RootDeviceType'
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
            if placementgroupname and placementgroupname != '*':
                condition['StringEquals']['ec2:PlacementGroup'] = 'arn:aws:ec2:{}:{}:placement-group/{}'.format(self.region, self.accountid, placementgroupname)

            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:AttachVolume',
                    'ec2:DetachVolume'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )

            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                }
            }
            if availabilityzone and availabilityzone != '*':
                condition['StringEquals']['ec2:AvailabilityZone'] = availabilityzone
            
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:AttachVolume',
                    'ec2:DetachVolume'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:volume/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )

        if monitoring_exists:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:MonitorInstances',
                    'ec2:UnmonitorInstances'
                ],
                resources=[
                    '*'
                ]
            )

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ec2:DescribeInstances'
            ],
            resources=[
                '*'
            ]
        )

        # Update
        if userdata_exists or ebsoptimized_exists:
            condition = {
                'StringEquals': {
                    'ec2:Region': self.region
                    # ec2:RootDeviceType
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
            if placementgroupname and placementgroupname != '*':
                condition['StringEquals']['ec2:PlacementGroup'] = 'arn:aws:ec2:{}:{}:placement-group/{}'.format(self.region, self.accountid, placementgroupname)
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:StartInstances',
                    'ec2:StopInstances'
                ],
                resources=[
                    'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid)
                ],
                conditions=condition
            )
        if userdata_exists or disableapitermination_exists or ebsoptimized_exists:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'ec2:ModifyInstanceAttribute'
                ],
                resources=['*']
            )

        # Delete
        condition = {
            'StringEquals': {
                'ec2:Region': self.region
                # 'ec2:RootDeviceType'
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
        if placementgroupname and placementgroupname != '*':
            condition['StringEquals']['ec2:PlacementGroup'] = 'arn:aws:ec2:{}:{}:placement-group/{}'.format(self.region, self.accountid, placementgroupname)
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'ec2:TerminateInstances'
            ],
            resources=[
                'arn:aws:ec2:{}:{}:instance/*'.format(self.region, self.accountid)
            ],
            conditions=condition
        )
