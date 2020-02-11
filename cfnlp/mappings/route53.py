class AWSRoute53HostedZonePermissions:
    def get_permissions(self, resname, res):
        name = self._get_property_or_default(res, "*", "Name")
        comment = self._get_property_or_default(res, None, "HostedZoneConfig", "Comment")
        cwloggrouparn = self._get_property_or_default(res, None, "QueryLoggingConfig", "CloudWatchLogsLogGroupArn")
        hostedzonetags_len = self._get_property_array_length(res, None, "HostedZoneTags")
        vpcs_len = self._get_property_array_length(res, None, "VPCs")

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'route53:CreateHostedZone'
            ],
            resources=[
                '*'
            ]
        )
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'route53:GetChange'
            ],
            resources=[
                'arn:aws:route53:::change/*'
            ]
        )
        if hostedzonetags_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'route53:ChangeTagsForResource'
                ],
                resources=[
                    'arn:aws:route53:::hostedzone/*'
                ]
            )
        if cwloggrouparn:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'route53:CreateQueryLoggingConfig'
                ],
                resources=[
                    'arn:aws:route53:::hostedzone/*'
                ]
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'route53:DeleteQueryLoggingConfig'
                ],
                resources=[
                    'arn:aws:route53:::queryloggingconfig/*'
                ]
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Delete',
                actions=[
                    'route53:DeleteQueryLoggingConfig'
                ],
                resources=[
                    'arn:aws:route53:::queryloggingconfig/*'
                ]
            )
        if vpcs_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'ec2:DescribeVpcs'
                ],
                resources=[
                    '*'
                ]
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'route53:AssociateVPCWithHostedZone'
                ],
                resources=[
                    'arn:aws:route53:::hostedzone/*'
                ]
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'route53:DisassociateVPCFromHostedZone'
                ],
                resources=[
                    'arn:aws:route53:::hostedzone/*'
                ],
                nonmandatory=True
            )
        if comment:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'route53:UpdateHostedZoneComment'
                ],
                resources=[
                    'arn:aws:route53:::hostedzone/*'
                ]
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'route53:DeleteHostedZone',
                'route53:ListQueryLoggingConfigs'
            ],
            resources=[
                'arn:aws:route53:::hostedzone/*'
            ]
        )
