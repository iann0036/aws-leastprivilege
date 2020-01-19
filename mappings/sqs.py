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

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'sqs:CreateQueue',
                'sqs:GetQueueAttributes'
            ],
            resources=[
                'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
            ]
        )
        if tags_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'sqs:TagQueue'
                ],
                resources=[
                    'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
                ],
                nonmandatory=True
            )
        if contentbaseddeduplication or delayseconds or fifoqueue or maximummessagesize or messageretentionperiod or receivemessagewaittimeseconds or visibilitytimeout:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'sqs:SetQueueAttributes'
                ],
                resources=[
                    'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
                ]
            )
            if tags_len:
                self.permissions.add(
                    resname=resname,
                    lifecycle='Update',
                    actions=[
                        'sqs:UntagQueue'
                    ],
                    resources=[
                        'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
                    ],
                    nonmandatory=True
                )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'sqs:DeleteQueue'
            ],
            resources=[
                'arn:aws:sqs:{}:{}:{}'.format(self.region, self.accountid, queuename)
            ]
        )
