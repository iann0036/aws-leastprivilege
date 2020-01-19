class AWSCloudWatchAlarmPermissions:
    def get_permissions(self, resname, res):
        alarmname = self._get_property_or_default(res, "*", "AlarmName")
        alarmactions = self._get_property_or_default(res, None, "AlarmActions")
        insufficientdataactions = self._get_property_or_default(res, None, "InsufficientDataActions")
        okactions = self._get_property_or_default(res, None, "OKActions")

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'cloudwatch:PutMetricAlarm'
            ],
            resources=[
                'arn:aws:cloudwatch:{}:{}:alarm:{}'.format(self.region, self.accountid, alarmname)
            ]
        )
        if alarmname != "*":
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'cloudwatch:DescribeAlarms'
                ],
                resources=[
                    'arn:aws:cloudwatch:{}:{}:alarm:{}'.format(self.region, self.accountid, alarmname)
                ]
            )
        
        createslr = False
        if alarmactions:
            for alarmaction in self._forcelist(alarmactions):
                if alarmaction.startswith("arn:aws:automate"):
                    createslr = True
        if insufficientdataactions:
            for insufficientdataaction in self._forcelist(insufficientdataactions):
                if insufficientdataaction.startswith("arn:aws:automate"):
                    createslr = True
        if okactions:
            for okaction in self._forcelist(okactions):
                if okaction.startswith("arn:aws:automate"):
                    createslr = True

        if createslr:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:CreateServiceLinkedRole'
                ],
                resources=[
                    'arn:aws:iam::{}:role/aws-service-role/events.amazonaws.com/AWSServiceRoleForCloudWatchEvents'.format(self.accountid)
                ],
                conditions={
                    'StringEquals': {
                        'iam:AWSServiceName': 'events.amazonaws.com'
                    }
                }
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'cloudwatch:DeleteAlarms'
            ],
            resources=[
                'arn:aws:cloudwatch:{}:{}:alarm:{}'.format(self.region, self.accountid, alarmname)
            ]
        )