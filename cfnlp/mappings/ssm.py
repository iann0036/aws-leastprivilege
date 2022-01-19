class AWSSSMParameterPermissions:
    def get_permissions(self, resname, res):
        name = self._get_property_or_default(res, "*", "Name")

        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'ssm:PutParameter',
                'ssm:AddTagsToResource',
            ],
            resources=[
                'arn:aws:ssm:{}:{}:parameter/{}'.format(self.region, self.accountid, name.lstrip("/"))
            ]
        )

        self.permissions.add(
            resname=resname,
            lifecycle='Update',
            actions=[
                'ssm:RemoveTagsFromResource',
                'ssm:GetParameter*'
            ],
            resources=[
                'arn:aws:ssm:{}:{}:parameter/{}'.format(self.region, self.accountid, name.lstrip("/"))
            ]
        )

        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'ssm:RemoveTagsFromResource',
                'ssm:DeleteParameter*'
            ],
            resources=[
                'arn:aws:ssm:{}:{}:parameter/{}'.format(self.region, self.accountid, name.lstrip("/"))
            ]
        )
