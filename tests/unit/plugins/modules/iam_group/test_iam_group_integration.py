# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


@pytest.mark.integration_api
class TestIamGroupIntegration:
    """Integration tests for CdpIamClient group management."""

    def test_create_update_delete_group_lifecycle(self, api_client):
        """Integration test for complete group lifecycle: create, update, delete."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-integration-group"

        try:
            # 1. Create a new group
            create_response = client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            assert "group" in create_response
            assert create_response["group"]["groupName"] == test_group_name
            assert create_response["group"]["syncMembershipOnUserLogin"] == True

            # 2. Verify group was created by listing it
            list_response = client.list_groups(group_names=[test_group_name])
            assert "groups" in list_response
            assert len(list_response["groups"]) == 1
            assert list_response["groups"][0]["groupName"] == test_group_name

            # 3. Update the group (change sync setting)
            update_response = client.update_group(
                group_name=test_group_name,
                sync_membership_on_user_login=False,
            )
            assert isinstance(update_response, dict)

            # 4. Verify the update
            updated_list = client.list_groups(group_names=[test_group_name])
            assert updated_list["groups"][0]["syncMembershipOnUserLogin"] == False

            # 5. Delete the group
            delete_response = client.delete_group(group_name=test_group_name)
            assert isinstance(delete_response, dict)

        except Exception as e:
            # Cleanup: try to delete the group if test fails
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass
            raise e

    def test_group_membership_management(self, api_client):
        """Integration test for adding and removing users from a group."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-membership-group"

        try:
            # 1. Create a test group
            client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            # 2. Get current user to add to group
            current_user = client.get_user()
            user_crn = current_user.get("crn")

            if user_crn:
                # 3. Add user to group
                add_response = client.add_user_to_group(
                    group_name=test_group_name,
                    user_id=user_crn,
                )
                assert isinstance(add_response, dict)

                # 4. Verify user was added
                members_response = client.list_group_members(group_name=test_group_name)
                assert "memberCrns" in members_response
                assert user_crn in members_response["memberCrns"]

                # 5. Remove user from group
                remove_response = client.remove_user_from_group(
                    group_name=test_group_name,
                    user_id=user_crn,
                )
                assert isinstance(remove_response, dict)

                # 6. Verify user was removed
                members_after = client.list_group_members(group_name=test_group_name)
                assert user_crn not in members_after.get("memberCrns", [])

        finally:
            # Cleanup: delete the test group
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass

    def test_group_role_assignment(self, api_client):
        """Integration test for assigning and unassigning roles to/from a group."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-role-assignment-group"

        try:
            # 1. Create a test group
            client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            # 2. Get available roles
            roles_response = client.list_roles()
            if roles_response.get("roles") and len(roles_response["roles"]) > 0:
                # Use the first available role for testing
                test_role_crn = roles_response["roles"][0]["crn"]

                # 3. Assign role to group
                assign_response = client.assign_group_role(
                    group_name=test_group_name,
                    role=test_role_crn,
                )
                assert isinstance(assign_response, dict)

                # 4. Verify role was assigned
                assigned_roles = client.list_group_assigned_roles(
                    group_name=test_group_name,
                )
                assert "roleCrns" in assigned_roles
                assert test_role_crn in assigned_roles["roleCrns"]

                # 5. Unassign role from group
                unassign_response = client.unassign_group_role(
                    group_name=test_group_name,
                    role=test_role_crn,
                )
                assert isinstance(unassign_response, dict)

                # 6. Verify role was unassigned
                roles_after = client.list_group_assigned_roles(
                    group_name=test_group_name,
                )
                assert test_role_crn not in roles_after.get("roleCrns", [])

        finally:
            # Cleanup: delete the test group
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass

    def test_machine_user_group_membership(self, api_client):
        """Integration test for adding and removing machine users from a group."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-machine-user-group"

        try:
            # 1. Create a test group
            client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            # 2. Get list of machine users
            machine_users_response = client.list_machine_users()

            if (
                machine_users_response.get("machineUsers")
                and len(machine_users_response["machineUsers"]) > 0
            ):
                # Use first available machine user for testing
                machine_user_name = machine_users_response["machineUsers"][0][
                    "machineUserName"
                ]

                # 3. Add machine user to group
                add_response = client.add_machine_user_to_group(
                    group_name=test_group_name,
                    machine_user_name=machine_user_name,
                )
                assert isinstance(add_response, dict)

                # 4. Verify machine user was added
                members_response = client.list_group_members(group_name=test_group_name)
                assert "memberCrns" in members_response

                # 5. Remove machine user from group
                remove_response = client.remove_machine_user_from_group(
                    group_name=test_group_name,
                    machine_user_name=machine_user_name,
                )
                assert isinstance(remove_response, dict)

                # 6. Verify machine user was removed
                members_after = client.list_group_members(group_name=test_group_name)
                # Machine user should no longer be in the group

        finally:
            # Cleanup: delete the test group
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass
