class AWSS3BucketPermissions:
    def get_permissions(self, resname, res):
        bucketname = self._get_property_or_default(res, "*", "BucketName")
        accesscontrol = self._get_property_or_default(res, None, "AccessControl")
        analyticsconfigurations_len = self._get_property_array_length(res, None, "AnalyticsConfigurations")
        bucketencryption_len = self._get_property_array_length(res, None, "BucketEncryption", "ServerSideEncryptionConfiguration")
        corsconfiguration_len = self._get_property_array_length(res, None, "CorsConfiguration", "CorsRules")
        accelerateconfiguration = self._get_property_or_default(res, None, "AccelerateConfiguration", "AccelerationStatus")
        inventoryconfigurations_len = self._get_property_array_length(res, None, "InventoryConfigurations")
        lifecycleconfiguration_len = self._get_property_array_length(res, None, "LifecycleConfiguration", "Rules")
        loggingconfiguration_exists = self._get_property_exists(res, "LoggingConfiguration")
        metricsconfigurations_len = self._get_property_array_length(res, None, "MetricsConfigurations")
        notificationconfiguration_exists = self._get_property_exists(res, "NotificationConfiguration")
        objectlockconfiguration_exists = self._get_property_exists(res, "ObjectLockConfiguration")
        objectlockenabled = self._get_property_or_default(res, False, "ObjectLockEnabled")
        publicaccessblockonfiguration_exists = self._get_property_exists(res, "PublicAccessBlockConfiguration")
        versioningconfiguration = self._get_property_or_default(res, None, "VersioningConfiguration", "Status")
        websiteconfiguration_exists = self._get_property_exists(res, "WebsiteConfiguration")
        replicationconfigurationrole = self._get_property_or_default(res, None, "ReplicationConfiguration", "Role")

        self.permissions.append({
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                's3:CreateBucket'
            ],
            'Resource': 'arn:aws:s3:::{}'.format(bucketname)
        })
        if accesscontrol:
            self.permissions.append({
                'Sid': '{}-create2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketAcl'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketAcl'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if analyticsconfigurations_len:
            self.permissions.append({
                'Sid': '{}-create3'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutAnalyticsConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutAnalyticsConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if bucketencryption_len:
            self.permissions.append({
                'Sid': '{}-create4'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutEncryptionConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update3'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutEncryptionConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if corsconfiguration_len:
            self.permissions.append({
                'Sid': '{}-create5'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketCORS'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update4'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketCORS'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if accelerateconfiguration:
            self.permissions.append({
                'Sid': '{}-create6'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutAccelerateConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update5'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutAccelerateConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if inventoryconfigurations_len:
            self.permissions.append({
                'Sid': '{}-create7'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutInventoryConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update6'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutInventoryConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if lifecycleconfiguration_len:
            self.permissions.append({
                'Sid': '{}-create8'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutLifecycleConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update7'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutLifecycleConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if loggingconfiguration_exists:
            self.permissions.append({
                'Sid': '{}-create9'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketLogging'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update8'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketLogging'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if metricsconfigurations_len:
            self.permissions.append({
                'Sid': '{}-create10'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutMetricsConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update9'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutMetricsConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if notificationconfiguration_exists:
            self.permissions.append({
                'Sid': '{}-create11'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketNotification'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update10'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketNotification'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if objectlockconfiguration_exists or objectlockenabled:
            self.permissions.append({
                'Sid': '{}-create12'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketObjectLockConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if publicaccessblockonfiguration_exists:
            self.permissions.append({
                'Sid': '{}-create13'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketPublicAccessBlock'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update11'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketPublicAccessBlock'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if versioningconfiguration:
            self.permissions.append({
                'Sid': '{}-create14'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketVersioning'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update12'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketVersioning'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if websiteconfiguration_exists:
            self.permissions.append({
                'Sid': '{}-create15'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketWebsite'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update13'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutBucketWebsite'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
        if replicationconfigurationrole:
            self.permissions.append({
                'Sid': '{}-create16'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutReplicationConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
            self.permissions.append({
                'Sid': '{}-create17'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:PassRole'
                ],
                'Resource': replicationconfigurationrole,
                'Condition': {
                    'StringEquals': {
                        'iam:PassedToService': 's3.amazonaws.com'
                    }
                }
            })
        elif not self.skip_update_policy:
            self.permissions.append({
                'Sid': '{}-update14'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    's3:PutReplicationConfiguration'
                ],
                'Resource': 'arn:aws:s3:::{}'.format(bucketname)
            })
            # iam:PassRole too insecure for generic?
            '''
            self.permissions.append({
                'Sid': '{}-update15'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:PassRole'
                ],
                'Resource': '*',
                'Condition': {
                    'StringEquals': {
                        'iam:PassedToService': 's3.amazonaws.com'
                    }
                }
            })
            '''
        self.permissions.append({
            'Sid': '{}-delete1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                's3:DeleteBucket'
            ],
            'Resource': 'arn:aws:s3:::{}'.format(bucketname)
        })