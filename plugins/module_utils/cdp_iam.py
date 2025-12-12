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

"""
A REST client for the Cloudera on Cloud Platform (CDP) IAM API
"""

from typing import Any, Dict, List, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)


class CdpIamClient:
    """CDP IAM API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP IAM client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    def _is_machine_user(self, user_crn: str) -> bool:
        """Check if a user CRN represents a machine user."""
        return ":machineUser:" in user_crn

    def get_group_details(self, group_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete group information including members, roles, and resource assignments.

        This method makes multiple API calls to assemble a comprehensive group profile:
        - Basic group information (from list_groups)
        - Group members (users and machine users)
        - Assigned roles
        - Assigned resource roles

        Returns:
            Complete group information dict, or None if group doesn't exist
        """
        groups = self.list_groups(group_names=[group_name]).get("groups", [])
        # all_groups_response = self.list_groups()
        # all_groups = all_groups_response.get("groups", [])
        # groups = [g for g in all_groups if g.get("groupName") == group_name]

        if not groups:
            return None

        group_info = groups[0]

        # Get group members (users and machine users)
        members_response = self.list_group_members(group_name=group_name)
        members = members_response.get("memberCrns", [])

        # Get assigned roles
        roles_response = self.list_group_assigned_roles(group_name=group_name)
        roles = roles_response.get("roleCrns", [])

        # Get assigned resource roles
        resource_roles_response = self.list_group_assigned_resource_roles(
            group_name=group_name,
        )
        resource_assignments = resource_roles_response.get("resourceAssignments", [])

        # Build complete group object
        return {
            "groupName": group_info.get("groupName"),
            "crn": group_info.get("crn"),
            "creationDate": group_info.get("creationDate"),
            "syncMembershipOnUserLogin": group_info.get("syncMembershipOnUserLogin"),
            "members": members,
            "roles": roles,
            "resourceAssignments": resource_assignments,
        }

    def manage_group_users(
        self,
        group_name: str,
        current_members: List[str],
        desired_users: List[str],
        purge: bool = False,
    ) -> bool:
        """
        Manage group membership (add/remove users and machine users).

        Args:
            group_name: The name of the group
            current_members: List of current member CRNs
            desired_users: List of desired user CRNs
            purge: If True, remove users not in desired list

        Returns:
            True if changes were made, False otherwise
        """
        changed = False

        if purge:
            # Remove all users not in desired list
            users_to_remove = [
                user for user in current_members if user not in desired_users
            ]
            for user_crn in users_to_remove:
                if self._is_machine_user(user_crn):
                    self.remove_machine_user_from_group(
                        machine_user_name=user_crn,
                        group_name=group_name,
                    )
                else:
                    self.remove_user_from_group(user_id=user_crn, group_name=group_name)
                changed = True

        # Add missing users
        users_to_add = [user for user in desired_users if user not in current_members]
        for user_crn in users_to_add:
            if self._is_machine_user(user_crn):
                self.add_machine_user_to_group(
                    machine_user_name=user_crn,
                    group_name=group_name,
                )
            else:
                self.add_user_to_group(user_id=user_crn, group_name=group_name)
            changed = True

        return changed

    def manage_group_roles(
        self,
        group_name: str,
        current_roles: List[str],
        desired_roles: List[str],
        purge: bool = False,
    ) -> bool:
        """
        Manage group role assignments.

        Args:
            group_name: The name of the group
            current_roles: List of current role CRNs
            desired_roles: List of desired role CRNs
            purge: If True, remove roles not in desired list

        Returns:
            True if changes were made, False otherwise
        """
        changed = False

        if purge:
            # Remove all roles not in desired list
            roles_to_remove = [
                role for role in current_roles if role not in desired_roles
            ]
            for role_crn in roles_to_remove:
                self.unassign_group_role(group_name=group_name, role=role_crn)
                changed = True

        # Add missing roles
        roles_to_add = [role for role in desired_roles if role not in current_roles]
        for role_crn in roles_to_add:
            self.assign_group_role(group_name=group_name, role=role_crn)
            changed = True

        return changed

    def manage_group_resource_roles(
        self,
        group_name: str,
        current_assignments: List[Dict[str, str]],
        desired_assignments: List[Dict[str, str]],
        purge: bool = False,
    ) -> bool:
        """
        Manage group resource role assignments.

        Args:
            group_name: The name of the group
            current_assignments: List of current resource role assignments
            desired_assignments: List of desired resource role assignments
            purge: If True, remove assignments not in desired list

        Returns:
            True if changes were made, False otherwise
        """
        changed = False

        # Normalize current assignments for comparison
        current_normalized = [
            {
                "resource": a.get("resourceCrn"),
                "role": a.get("resourceRoleCrn"),
            }
            for a in current_assignments
        ]

        # Normalize desired assignments
        desired_normalized = [
            {
                "resource": a.get("resource") or a.get("resourceCrn"),
                "role": a.get("role") or a.get("resourceRoleCrn"),
            }
            for a in desired_assignments
        ]

        if purge:
            # Remove all assignments not in desired list
            assignments_to_remove = [
                a for a in current_normalized if a not in desired_normalized
            ]
            for assignment in assignments_to_remove:
                self.unassign_group_resource_role(
                    group_name=group_name,
                    resource_crn=assignment[
                        "resource"
                    ],  # pyright: ignore[reportArgumentType]
                    resource_role_crn=assignment[
                        "role"
                    ],  # pyright: ignore[reportArgumentType]
                )
                changed = True

        # Add missing assignments
        assignments_to_add = [
            a for a in desired_normalized if a not in current_normalized
        ]
        for assignment in assignments_to_add:
            self.assign_group_resource_role(
                group_name=group_name,
                resource_crn=assignment[
                    "resource"
                ],  # pyright: ignore[reportArgumentType]
                resource_role_crn=assignment[
                    "role"
                ],  # pyright: ignore[reportArgumentType]
            )
            changed = True

        return changed

    @CdpClient.paginated()
    def list_groups(
        self,
        group_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List IAM groups with automatic pagination.

        Args:
            group_names: Optional list of group names or CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing groups list
        """
        json_data: Dict[str, Any] = {}

        # Add group names filter if provided
        if group_names is not None:
            json_data["groupNames"] = group_names

        # Add pagination parameters if provided
        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroups",
            json_data=json_data,
            squelch={404: {}},
        )

    @CdpClient.paginated()
    def list_users(
        self,
        user_ids: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List IAM users with automatic pagination.

        Args:
            user_ids: Optional list of user IDs or CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing users list
        """
        json_data: Dict[str, Any] = {}

        # Add user IDs filter if provided
        if user_ids is not None:
            json_data["userIds"] = user_ids

        # Add pagination parameters if provided
        # Note: IAM API uses "startingToken" for requests, but decorator uses "pageToken"
        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listUsers",
            json_data=json_data,
        )

    def get_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a user.

        Args:
            user_id: Optional user ID or CRN. If not provided, gets the current user.

        Returns:
            Response containing user information
        """
        json_data: Dict[str, Any] = {}

        # Add user ID if provided
        if user_id is not None:
            json_data["userId"] = user_id

        response = self.api_client.post(
            "/api/v1/iam/getUser",
            json_data=json_data,
        )

        return response.get("user", {})

    @CdpClient.paginated()
    def list_group_assigned_resource_roles(
        self,
        group_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List resource roles assigned to a group with automatic pagination.

        Args:
            group_name: Group name or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing resource assignments
        """
        json_data: Dict[str, Any] = {"groupName": group_name}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroupAssignedResourceRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_group_assigned_roles(
        self,
        group_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List roles assigned to a group with automatic pagination.

        Args:
            group_name: Group name or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing role CRNs
        """
        json_data: Dict[str, Any] = {"groupName": group_name}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroupAssignedRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_group_members(
        self,
        group_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List members of a group with automatic pagination.

        Args:
            group_name: Group name or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing member CRNs
        """
        json_data: Dict[str, Any] = {"groupName": group_name}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroupMembers",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_groups_for_machine_user(
        self,
        machine_user_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List groups for a machine user with automatic pagination.

        Args:
            machine_user_name: Machine user name or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing group CRNs
        """
        json_data: Dict[str, Any] = {"machineUserName": machine_user_name}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroupsForMachineUser",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_groups_for_user(
        self,
        user_id: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List groups for a user with automatic pagination.

        Args:
            user_id: User ID or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing group CRNs
        """
        json_data: Dict[str, Any] = {"userId": user_id}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroupsForUser",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_machine_user_assigned_resource_roles(
        self,
        machine_user_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List resource roles assigned to a machine user with automatic pagination.

        Args:
            machine_user_name: Machine user name or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing resource assignments
        """
        json_data: Dict[str, Any] = {"machineUserName": machine_user_name}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listMachineUserAssignedResourceRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_machine_user_assigned_roles(
        self,
        machine_user_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List roles assigned to a machine user with automatic pagination.

        Args:
            machine_user_name: Machine user name or CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing role CRNs
        """
        json_data: Dict[str, Any] = {"machineUserName": machine_user_name}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listMachineUserAssignedRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_machine_users(
        self,
        machine_user_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List machine users with automatic pagination.

        Args:
            machine_user_names: Optional list of machine user names or CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing machine users list
        """
        json_data: Dict[str, Any] = {}

        if machine_user_names is not None:
            json_data["machineUserNames"] = machine_user_names

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listMachineUsers",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_resource_assignees(
        self,
        resource_crn: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List resource assignees and their resource roles with automatic pagination.

        Args:
            resource_crn: Resource CRN
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing resource assignees
        """
        json_data: Dict[str, Any] = {"resourceCrn": resource_crn}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listResourceAssignees",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_resource_roles(
        self,
        resource_role_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List resource roles with automatic pagination.

        Args:
            resource_role_names: Optional list of resource role CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing resource roles list
        """
        json_data: Dict[str, Any] = {}

        if resource_role_names is not None:
            json_data["resourceRoleNames"] = resource_role_names

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listResourceRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_roles(
        self,
        role_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List roles with automatic pagination.

        Args:
            role_names: Optional list of role names or CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing roles list
        """
        json_data: Dict[str, Any] = {}

        if role_names is not None:
            json_data["roleNames"] = role_names

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_user_assigned_resource_roles(
        self,
        user: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List resource roles assigned to a user with automatic pagination.

        Args:
            user: Optional user CRN or ID. If not provided, defaults to the user making the request.
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing resource assignments
        """
        json_data: Dict[str, Any] = {}

        if user is not None:
            json_data["user"] = user

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listUserAssignedResourceRoles",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_user_assigned_roles(
        self,
        user: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List roles assigned to a user with automatic pagination.

        Args:
            user: Optional user CRN or ID. If not provided, defaults to the user making the request.
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing role CRNs
        """
        json_data: Dict[str, Any] = {}

        if user is not None:
            json_data["user"] = user

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listUserAssignedRoles",
            json_data=json_data,
        )

    # Group Lifecycle Management Methods

    def create_group(
        self,
        group_name: str,
        sync_membership_on_user_login: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create a new IAM group.

        Args:
            group_name: The name of the group. Must be unique.
            sync_membership_on_user_login: Whether group membership is synced when a user logs in.
                                          Defaults to True if not specified.

        Returns:
            Response containing the created group information
        """
        json_data: Dict[str, Any] = {"groupName": group_name}

        if sync_membership_on_user_login is not None:
            json_data["syncMembershipOnUserLogin"] = sync_membership_on_user_login

        return self.api_client.post(
            "/api/v1/iam/createGroup",
            json_data=json_data,
        )

    def delete_group(self, group_name: str) -> Dict[str, Any]:
        """
        Delete an IAM group.

        Args:
            group_name: The name or CRN of the group to delete

        Returns:
            Response confirming deletion
        """
        json_data: Dict[str, Any] = {"groupName": group_name}

        return self.api_client.post(
            "/api/v1/iam/deleteGroup",
            json_data=json_data,
            squelch={404: {}},
        )

    def update_group(
        self,
        group_name: str,
        sync_membership_on_user_login: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update an IAM group.

        Args:
            group_name: The name or CRN of the group to update
            sync_membership_on_user_login: Whether group membership is synced when a user logs in.
                                          Can be omitted if no update is required.

        Returns:
            Response containing the updated group information
        """
        json_data: Dict[str, Any] = {"groupName": group_name}

        if sync_membership_on_user_login is not None:
            json_data["syncMembershipOnUserLogin"] = sync_membership_on_user_login

        return self.api_client.post(
            "/api/v1/iam/updateGroup",
            json_data=json_data,
        )

    # Group Membership Management Methods

    def add_user_to_group(self, group_name: str, user_id: str) -> Dict[str, Any]:
        """
        Add a user to a group.

        Args:
            group_name: The name or CRN of the group
            user_id: The ID or CRN of the user to add to the group

        Returns:
            Response confirming the user was added to the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "userId": user_id,
        }

        return self.api_client.post(
            "/api/v1/iam/addUserToGroup",
            json_data=json_data,
        )

    def add_machine_user_to_group(
        self,
        group_name: str,
        machine_user_name: str,
    ) -> Dict[str, Any]:
        """
        Add a machine user to a group.

        Args:
            group_name: The name or CRN of the group
            machine_user_name: The name or CRN of the machine user to add to the group

        Returns:
            Response confirming the machine user was added to the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "machineUserName": machine_user_name,
        }

        return self.api_client.post(
            "/api/v1/iam/addMachineUserToGroup",
            json_data=json_data,
        )

    def remove_user_from_group(self, group_name: str, user_id: str) -> Dict[str, Any]:
        """
        Remove a user from a group.

        Args:
            group_name: The name or CRN of the group
            user_id: The ID or CRN of the user to remove from the group

        Returns:
            Response confirming the user was removed from the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "userId": user_id,
        }

        return self.api_client.post(
            "/api/v1/iam/removeUserFromGroup",
            json_data=json_data,
        )

    def remove_machine_user_from_group(
        self,
        group_name: str,
        machine_user_name: str,
    ) -> Dict[str, Any]:
        """
        Remove a machine user from a group.

        Args:
            group_name: The name or CRN of the group
            machine_user_name: The name or CRN of the machine user to remove from the group

        Returns:
            Response confirming the machine user was removed from the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "machineUserName": machine_user_name,
        }

        return self.api_client.post(
            "/api/v1/iam/removeMachineUserFromGroup",
            json_data=json_data,
        )

    # Group Role Assignment Methods

    def assign_group_role(self, group_name: str, role: str) -> Dict[str, Any]:
        """
        Assign a role to a group.

        Args:
            group_name: The group name or CRN
            role: The role name or CRN to assign

        Returns:
            Response confirming the role was assigned to the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "role": role,
        }

        return self.api_client.post(
            "/api/v1/iam/assignGroupRole",
            json_data=json_data,
        )

    def assign_group_resource_role(
        self,
        group_name: str,
        resource_crn: str,
        resource_role_crn: str,
    ) -> Dict[str, Any]:
        """
        Assign a resource role to a group.

        Args:
            group_name: The group name or CRN
            resource_crn: The resource CRN for which the resource role rights are granted
            resource_role_crn: The CRN of the resource role being assigned

        Returns:
            Response confirming the resource role was assigned to the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "resourceCrn": resource_crn,
            "resourceRoleCrn": resource_role_crn,
        }

        return self.api_client.post(
            "/api/v1/iam/assignGroupResourceRole",
            json_data=json_data,
        )

    def unassign_group_role(self, group_name: str, role: str) -> Dict[str, Any]:
        """
        Unassign a role from a group.

        Args:
            group_name: The group name or CRN
            role: The role name or CRN to unassign

        Returns:
            Response confirming the role was unassigned from the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "role": role,
        }

        return self.api_client.post(
            "/api/v1/iam/unassignGroupRole",
            json_data=json_data,
        )

    def unassign_group_resource_role(
        self,
        group_name: str,
        resource_crn: str,
        resource_role_crn: str,
    ) -> Dict[str, Any]:
        """
        Unassign a resource role from a group.

        Args:
            group_name: The group name or CRN
            resource_crn: The CRN of the resource for which the resource role rights will be unassigned
            resource_role_crn: The CRN of the resource role to unassign

        Returns:
            Response confirming the resource role was unassigned from the group
        """
        json_data: Dict[str, Any] = {
            "groupName": group_name,
            "resourceCrn": resource_crn,
            "resourceRoleCrn": resource_role_crn,
        }

        return self.api_client.post(
            "/api/v1/iam/unassignGroupResourceRole",
            json_data=json_data,
        )
