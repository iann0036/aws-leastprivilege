class AWSSNSTopicPermissions:
    def get_permissions(self, resname, res):
        topicname = self._get_property_or_default(res, "*", "TopicName")
        tags_len = self._get_property_array_length(res, None, "Tags")
        subscription_len = self._get_property_array_length(res, None, "Subscription")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'sns:CreateTopic',
                'sns:GetTopicAttributes'
            ],
            'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
        })
        if topicname:
            self.permissions.append({
                'Sid': '{}-create2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'sns:ListTopics'
                ],
                'Resource': '*'
            })
        if tags_len:
            self.permissions.append({
                'Sid': '{}-createnm1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'sns:TagResource'
                ],
                'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
            })
        if subscription_len:
            # TODO: Conditions here
            self.permissions.append({
                'Sid': '{}-create3'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'sns:Subscribe'
                ],
                'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
            })
        if self.include_update_actions:
            self.permissions.append({
                'Sid': '{}-update1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'sns:SetTopicAttributes'
                ],
                'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
            })
            if tags_len:
                self.permissions.append({
                    'Sid': '{}-updatenm1'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'sns:UntagResource'
                    ],
                    'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                })
            if subscription_len:
                self.permissions.append({
                    'Sid': '{}-update2'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'sns:ListSubscriptionsByTopic'
                    ],
                    'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                })
                # TODO: Conditions here
                self.permissions.append({
                    'Sid': '{}-update3'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'sns:Unsubscribe'
                    ],
                    'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
                })
        self.permissions.append({
            'Sid': '{}-delete1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'sns:DeleteTopic'
            ],
            'Resource': 'arn:aws:sns:{}:{}:{}'.format(self.region, self.accountid, topicname)
        })
