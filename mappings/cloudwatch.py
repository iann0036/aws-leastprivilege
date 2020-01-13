class AWSCloudWatchAlarmPermissions:
    def get_permissions(self, resname, res):
        alarmname = self._get_property_or_default(res, "*", "AlarmName")
        alarmactions = self._get_property_or_default(res, None, "AlarmActions")
        insufficientdataactions = self._get_property_or_default(res, None, "InsufficientDataActions")
        okactions = self._get_property_or_default(res, None, "OKActions")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'cloudwatch:PutMetricAlarm'
            ],
            'Resource': 'arn:aws:cloudwatch:{}:{}:alarm:{}'.format(self.region, self.accountid, alarmname)
        })
        if alarmname != "*":
            self.permissions.append({
                'Sid': '{}-create2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'cloudwatch:DescribeAlarms'
                ],
                'Resource': 'arn:aws:cloudwatch:{}:{}:alarm:{}'.format(self.region, self.accountid, alarmname)
            })
        
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
            self.permissions.append({
                'Sid': '{}-create3'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:CreateServiceLinkedRole'
                ],
                'Resource': 'arn:aws:iam::{}:role/aws-service-role/events.amazonaws.com/AWSServiceRoleForCloudWatchEvents'.format(self.accountid),
                'Condition': {
                    'StringEquals': {
                        'iam:AWSServiceName': 'events.amazonaws.com'
                    }
                }
            })
        self.permissions.append({
            'Sid': '{}-delete1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'cloudwatch:DeleteAlarms'
            ],
            'Resource': 'arn:aws:cloudwatch:{}:{}:alarm:{}'.format(self.region, self.accountid, alarmname)
        })
