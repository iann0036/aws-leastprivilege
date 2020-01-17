class AWSSQSQueuePermissions:
    def get_permissions(self, resname, res):
        queuename = self._get_property_or_default(res, "*", "QueueName")
        contentbaseddeduplication = self._get_property_exists(res, "ContentBasedDeduplication")
        delayseconds = self._get_property_exists(res, "DelaySeconds")
        fifoqueue = self._get_property_exists(res, "FifoQueue")
        maximummessagesize = self._get_property_exists(res, "MaximumMessageSize")
        messageretentionperiod = self._get_property_exists(res, "MessageRetentionPeriod")
        receivemessagewaittimeseconds = self._get_property_exists(res, "ReceiveMessageWaitTimeSeconds")
        visibilitytimeout = self._get_property_exists(res, "VisibilityTimeout")
        tags_len = self._get_property_array_length(res, None, "Tags")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'sqs:CreateQueue',
                'sqs:GetQueueAttributes'
            ],
            'Resource': 'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
        })
        if tags_len:
            self.permissions.append({
                'Sid': '{}-createnm1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'sqs:TagQueue'
                ],
                'Resource': 'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
            })
        if self.include_update_actions and (contentbaseddeduplication or delayseconds or fifoqueue or maximummessagesize or messageretentionperiod or receivemessagewaittimeseconds or visibilitytimeout):
            self.permissions.append({
                'Sid': '{}-update1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'sqs:SetQueueAttributes'
                ],
                'Resource': 'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
            })
            if tags_len:
                self.permissions.append({
                    'Sid': '{}-updatenm1'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'sqs:UntagQueue'
                    ],
                    'Resource': 'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
                })
        self.permissions.append({
            'Sid': '{}-delete1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'sqs:DeleteQueue'
            ],
            'Resource': 'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
        })
