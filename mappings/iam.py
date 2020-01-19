import json
import sys

class AWSIAMRolePermissions:
    def get_permissions(self, resname, res):
        rolename = self._get_property_or_default(res, "*", "RoleName")
        permissionsboundary = self._get_property_or_default(res, None, "PermissionsBoundary")
        description = self._get_property_or_default(res, None, "Description")
        maxsessionduration = self._get_property_or_default(res, None, "MaxSessionDuration")
        policies_len = self._get_property_array_length(res, None, "Policies")
        managedpolicyarns = self._get_property_or_default(res, None, "ManagedPolicyArns")
        tags_len = self._get_property_array_length(res, None, "Tags")
        path = self._get_property_or_default(res, "/", "Path")
        if path == "*":
            path = "/"

        condition = None
        if permissionsboundary and permissionsboundary != "*":
            condition = {
                'StringEquals': {
                    'iam:PermissionsBoundary': permissionsboundary
                }
            }
        self.permissions.add(
            resname=resname,
            lifecycle='Create',
            actions=[
                'iam:CreateRole'
            ],
            resources=[
                'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            ],
            conditions=condition
        )
        if rolename != "*":
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:GetRole'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ]
            )
        if managedpolicyarns:
            condition = {
                'StringEquals': {}
            }
            if permissionsboundary and permissionsboundary != "*":
                condition['StringEquals']['iam:PermissionsBoundary'] = permissionsboundary
            if managedpolicyarns != "*":
                condition['StringEquals']['iam:PolicyARN'] = managedpolicyarns
            if not condition['StringEquals']:
                condition = None
            
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:AttachRolePolicy'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                conditions=condition
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'iam:DetachRolePolicy'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ]
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Delete',
                actions=[
                    'iam:DetachRolePolicy'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                conditions=condition
            )
        if policies_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:GetRolePolicy'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                nonmandatory=True
            )
            condition = None
            if permissionsboundary and permissionsboundary != "*":
                condition = {
                    'StringEquals': {
                        'iam:PermissionsBoundary': permissionsboundary
                    }
                }
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:PutRolePolicy'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                conditions=condition
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Delete',
                actions=[
                    'iam:DeleteRolePolicy'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                conditions=condition
            )
        if tags_len:
            self.permissions.add(
                resname=resname,
                lifecycle='Create',
                actions=[
                    'iam:TagRole'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                nonmandatory=True
            )
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'iam:UntagRole'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ],
                nonmandatory=True
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Update',
            actions=[
                'iam:UpdateAssumeRolePolicy'
            ],
            resources=[
                'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            ]
        )
        if description:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'iam:UpdateRoleDescription'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ]
            )
        if maxsessionduration:
            self.permissions.add(
                resname=resname,
                lifecycle='Update',
                actions=[
                    'iam:UpdateRole'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ]
            )
        if permissionsboundary:
            self.permissions.add( # TODO: Dangerous?
                resname=resname,
                lifecycle='Update',
                actions=[
                    'iam:PutRolePermissionsBoundary'
                ],
                resources=[
                    'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                ]
            )
        self.permissions.add(
            resname=resname,
            lifecycle='Delete',
            actions=[
                'iam:DeleteRole'
            ],
            resources=[
                'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            ]
        )
