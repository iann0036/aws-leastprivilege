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

        create_permission_1 = {
            'Sid': '{}-create1'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'iam:CreateRole'
            ],
            'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
        }
        if permissionsboundary and permissionsboundary != "*":
            create_permission_1['Condition'] = {
                'StringEquals': {
                    'iam:PermissionsBoundary': permissionsboundary
                }
            }
        self.permissions.append(create_permission_1)
        if rolename != "*":
            self.permissions.append({
                'Sid': '{}-create2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:GetRole'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            })
        if managedpolicyarns:
            create_permission_3 = {
                'Sid': '{}-create3'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:AttachRolePolicy'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            }
            delete_permission_1 = {
                'Sid': '{}-delete1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:DetachRolePolicy'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            }
            create_permission_3_condition = {
                'StringEquals': {}
            }
            delete_permission_1_condition = {
                'StringEquals': {}
            }
            if permissionsboundary and permissionsboundary != "*":
                create_permission_3_condition['StringEquals']['iam:PermissionsBoundary'] = permissionsboundary
                delete_permission_1_condition['StringEquals']['iam:PermissionsBoundary'] = permissionsboundary
            if managedpolicyarns != "*":
                create_permission_3_condition['StringEquals']['iam:PolicyARN'] = managedpolicyarns
                delete_permission_1_condition['StringEquals']['iam:PolicyARN'] = managedpolicyarns
            if create_permission_3_condition['StringEquals']:
                create_permission_3['Condition'] = create_permission_3_condition
                delete_permission_1['Condition'] = delete_permission_1_condition
            
            self.permissions.append(create_permission_3)
            if self.include_update_actions:
                self.permissions.append(delete_permission_1)
        if policies_len:
            create_permission_4 = {
                'Sid': '{}-create4'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:PutRolePolicy'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            }
            self.permissions.append({
                'Sid': '{}-createnm1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:GetRolePolicy'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            })
            delete_permission_2 = {
                'Sid': '{}-delete2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:DeleteRolePolicy'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            }
            if permissionsboundary and permissionsboundary != "*":
                create_permission_4['Condition'] = {
                    'StringEquals': {
                        'iam:PermissionsBoundary': permissionsboundary
                    }
                }
                delete_permission_2['Condition'] = {
                    'StringEquals': {
                        'iam:PermissionsBoundary': permissionsboundary
                    }
                }
            self.permissions.append(create_permission_4)
            self.permissions.append(delete_permission_2)
        if tags_len:
            self.permissions.append({
                'Sid': '{}-createnm2'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:TagRole'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            })
            if self.include_update_actions:
                self.permissions.append({
                    'Sid': '{}-updatenm1'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'iam:UntagRole'
                    ],
                    'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                })
        if self.include_update_actions:
            self.permissions.append({
                'Sid': '{}-update1'.format(resname),
                'Effect': 'Allow',
                'Action': [
                    'iam:UpdateAssumeRolePolicy'
                ],
                'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
            })
            if description:
                self.permissions.append({
                    'Sid': '{}-update2'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'iam:UpdateRoleDescription'
                    ],
                    'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                })
            if maxsessionduration:
                self.permissions.append({
                    'Sid': '{}-update3'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'iam:UpdateRole'
                    ],
                    'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                })
            if permissionsboundary:
                self.permissions.append({ # TODO: Dangerous?
                    'Sid': '{}-update4'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'iam:PutRolePermissionsBoundary'
                    ],
                    'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                })
            if managedpolicyarns:
                self.permissions.append({
                    'Sid': '{}-update5'.format(resname),
                    'Effect': 'Allow',
                    'Action': [
                        'iam:DetachRolePolicy'
                    ],
                    'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
                })
        self.permissions.append({
            'Sid': '{}-delete3'.format(resname),
            'Effect': 'Allow',
            'Action': [
                'iam:DeleteRole'
            ],
            'Resource': 'arn:aws:iam::{}:role{}{}'.format(self.accountid, path, rolename)
        })
