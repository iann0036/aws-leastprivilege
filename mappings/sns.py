class AWSSNSTopicPermissions:
    def get_permissions(self, resname, res):
        topicname = self._get_property_or_default(res, "*", "TopicName")
        tags_len = self._get_property_array_length(res, None, "Tags")
        subscription_len = self._get_property_array_length(res, None, "Subscription")

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'sns:CreateTopic',
                'sns:GetTopicAttributes'
            ],
            resources=[
                'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
            ]
        )
        if topicname:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'sns:ListTopics'
                ],
                resources=['*']
            )
        if tags_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'sns:TagResource'
                ],
                resources=[
                    'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                ],
                nonmandatory=True
            )
        if subscription_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'sns:Subscribe'
                ],
                resources=[
                    'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                ]
                # TODO: Conditions here
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Update',
            actions=[
                'sns:SetTopicAttributes'
            ],
            resources=[
                'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
            ]
        )
        if tags_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'sns:UntagResource'
                ],
                resources=[
                    'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                ],
                nonmandatory=True
            )
        if subscription_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'sns:ListSubscriptionsByTopic'
                ],
                resources=[
                    'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                ]
                # TODO: Conditions here
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'sns:Unsubscribe'
                ],
                resources=[
                    'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                ]
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'sns:DeleteTopic'
            ],
            resources=[
                'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
            ]
        )
