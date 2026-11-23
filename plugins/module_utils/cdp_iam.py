# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
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

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
)


@dataclass
class WorkloadPasswordDetails:
    """Information about the workload password for a user or machine user."""

    isPasswordSet: Union[bool, None, NULLABLE] = NULLABLE
    passwordExpirationDate: Union[str, None, NULLABLE] = NULLABLE
    passwordMinLifetimeDate: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class ResourceAssignment:
    """A resource role assigned on a resource."""

    resourceCrn: Union[str, None, NULLABLE] = NULLABLE
    resourceRoleCrn: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class User:
    """Information about a CDP user (as returned by listUsers/getUser/createUser/updateUser)."""

    accountAdmin: Union[bool, None, NULLABLE] = NULLABLE
    creationDate: Union[str, None, NULLABLE] = NULLABLE
    crn: Union[str, None, NULLABLE] = NULLABLE
    email: Union[str, None, NULLABLE] = NULLABLE
    firstName: Union[str, None, NULLABLE] = NULLABLE
    identityProviderCrn: Union[str, None, NULLABLE] = NULLABLE
    lastInteractiveLogin: Union[str, None, NULLABLE] = NULLABLE
    lastName: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    userId: Union[str, None, NULLABLE] = NULLABLE
    workloadPasswordDetails: Union[WorkloadPasswordDetails, None, NULLABLE] = NULLABLE
    workloadUsername: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class UserDetails(User):
    """
    A User enriched with its role, resource role and group assignments.

    The extra fields are not part of the IAM User type; they are assembled from the
    listUserAssignedRoles, listUserAssignedResourceRoles and listGroupsForUser calls.
    """

    roles: Union[List[str], None, NULLABLE] = NULLABLE
    resourceAssignments: Union[List[ResourceAssignment], None, NULLABLE] = NULLABLE
    groups: Union[List[str], None, NULLABLE] = NULLABLE


@dataclass
class DeleteUserResponse:
    """Resources that were released when a user was deleted."""

    accessKeysDeleted: Union[List[str], None, NULLABLE] = NULLABLE
    groupsModified: Union[List[str], None, NULLABLE] = NULLABLE
    resourcesUnassigned: Union[List[ResourceAssignment], None, NULLABLE] = NULLABLE
    rolesUnassigned: Union[List[str], None, NULLABLE] = NULLABLE


@dataclass
class MachineUser:
    """Information about a CDP machine user (as returned by listMachineUsers/createMachineUser)."""

    creationDate: Union[str, None, NULLABLE] = NULLABLE
    crn: Union[str, None, NULLABLE] = NULLABLE
    machineUserName: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    workloadPasswordDetails: Union[WorkloadPasswordDetails, None, NULLABLE] = NULLABLE
    workloadUsername: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class MachineUserDetails(MachineUser):
    """
    A MachineUser enriched with its role and resource role assignments.

    The extra fields are not part of the IAM MachineUser type; they are assembled from the
    listMachineUserAssignedRoles and listMachineUserAssignedResourceRoles calls.
    """

    roles: Union[List[str], None, NULLABLE] = NULLABLE
    resourceAssignments: Union[List[ResourceAssignment], None, NULLABLE] = NULLABLE


@dataclass
class DeleteMachineUserResponse:
    """Resources that were released when a machine user was deleted."""

    accessKeysDeleted: Union[List[str], None, NULLABLE] = NULLABLE
    groupsModified: Union[List[str], None, NULLABLE] = NULLABLE
    resourcesUnassigned: Union[List[ResourceAssignment], None, NULLABLE] = NULLABLE
    rolesUnassigned: Union[List[str], None, NULLABLE] = NULLABLE


class CdpIamClient:
    """CDP IAM API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP IAM client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    @staticmethod
    def get_group_diff_exclude_keys() -> List[str]:
        """
        Get list of group fields to exclude from diff calculations.

        Returns:
            List of field names to exclude from diffs (in snake_case format)
        """
        return [
            "crn",
            "creation_date",
        ]

    @staticmethod
    def get_machine_user_diff_exclude_keys() -> List[str]:
        """
        Get list of machine user fields to exclude from diff calculations.

        Returns:
            List of field names to exclude from diffs (in snake_case format)
        """
        return [
            "crn",
            "creation_date",
            "status",
            "workload_username",
            "workload_password_details",
        ]

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
    def _list_users_page(
        self,
        user_ids: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listUsers call; pagination across pages is handled by the decorator."""
        json_data: Dict[str, Any] = {}

        if user_ids is not None:
            json_data["userIds"] = user_ids

        # Note: IAM API uses "startingToken" for requests, but decorator uses "pageToken"
        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listUsers",
            json_data=json_data,
        )

    def list_users(self, user_ids: Optional[List[str]] = None) -> List[User]:
        """
        List IAM users with automatic pagination.

        Args:
            user_ids: Optional list of user IDs or CRNs to filter by

        Returns:
            List of basic User objects (no roles, resource roles or groups)
        """
        result = self._list_users_page(user_ids=user_ids)
        return [from_dict(User, user) for user in result.get("users", [])]

    def list_users_filtered(
        self,
        filters: Dict[str, str],
    ) -> List[User]:
        """
        List IAM users filtered by regex patterns on user fields.

        Fetches all users and returns only those where every filter key's value
        matches the corresponding regex pattern.

        Args:
            filters: Dict mapping a User field name to a regex pattern string. Field
                     names may be snake_case ("workload_username") or the API's
                     camelCase ("workloadUsername"). A user is included only when
                     all patterns match. Unknown fields never match.

        Returns:
            List of matching basic User objects.
        """

        compiled = {
            field: re.compile(pattern)
            for field, pattern in snake_dict_to_camel_dict(filters).items()
        }
        matched = []
        for user in self.list_users():
            for field, pattern in compiled.items():
                value = getattr(user, field, NULLABLE)
                if value is NULLABLE or not (value and re.search(pattern, str(value))):
                    break
            else:
                matched.append(user)
        return matched

    def get_user(self, user_id: Optional[str] = None) -> Optional[User]:
        """
        Get information about a user.

        Args:
            user_id: Optional user ID or CRN. If not provided, gets the current user.

        Returns:
            The User, or None if the user does not exist
        """
        json_data: Dict[str, Any] = {}

        if user_id is not None:
            json_data["userId"] = user_id

        response = self.api_client.post(
            "/api/v1/iam/getUser",
            json_data=json_data,
            squelch={404: {}},
        )

        user = response.get("user") if response else None
        return from_dict(User, user) if user else None

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
    def _list_groups_for_user_page(
        self,
        user_id: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listGroupsForUser call; pagination across pages is handled by the decorator."""
        json_data: Dict[str, Any] = {"userId": user_id}

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listGroupsForUser",
            json_data=json_data,
        )

    def list_groups_for_user(self, user_id: str) -> List[str]:
        """
        List the groups a user belongs to with automatic pagination.

        Args:
            user_id: User ID or CRN

        Returns:
            List of group CRNs
        """
        result = self._list_groups_for_user_page(user_id=user_id)
        return result.get("groupCrns", [])

    # ========================================================================
    # User Management Methods
    # ========================================================================

    def create_user(
        self,
        email: str,
        identity_provider_user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        saml_provider_name: Optional[str] = None,
    ) -> User:
        """
        Create a user in CDP.

        Note: This method intentionally does not support the 'groups' parameter
        to avoid the side effect of group creation. Group memberships should be
        managed separately after user creation using manage_user_groups().

        Args:
            email: The email address for the user (display purposes only)
            identity_provider_user_id: The identity provider user ID that matches the NameId in SAML response
            first_name: The user's first name
            last_name: The user's last name
            saml_provider_name: The name or CRN of the SAML provider for login.
                               If not provided, the default identity provider will be used.

        Returns:
            The created User
        """
        # If saml_provider_name not provided, use default identity provider
        if saml_provider_name is None:
            default_idp = self.get_default_identity_provider()
            saml_provider_name = default_idp.get("crn")

        json_data: Dict[str, Any] = {
            "email": email,
            "identityProviderUserId": identity_provider_user_id,
        }

        if first_name is not None:
            json_data["firstName"] = first_name
        if last_name is not None:
            json_data["lastName"] = last_name
        if saml_provider_name is not None:
            json_data["samlProviderName"] = saml_provider_name

        response = self.api_client.post(
            "/api/v1/iam/createUser",
            json_data=json_data,
        )

        return from_dict(User, response.get("user", {}))

    def delete_user(self, user_id: str) -> DeleteUserResponse:
        """
        Delete a user and all associated resources.

        This includes deleting all associated access keys, unassigning all roles and resource roles,
        and removing the user from all groups.

        Args:
            user_id: The user ID or CRN to delete

        Returns:
            The resources that were released by the deletion
        """
        json_data: Dict[str, Any] = {
            "userId": user_id,
        }

        response = self.api_client.post(
            "/api/v1/iam/deleteUser",
            json_data=json_data,
        )

        return from_dict(DeleteUserResponse, response or {})

    def update_user(
        self,
        user_id: str,
        active: Optional[bool] = None,
    ) -> User:
        """
        Update a user.

        Args:
            user_id: The user ID or CRN to update
            active: Set user active state (True to activate, False to deactivate)

        Returns:
            The updated User
        """
        json_data: Dict[str, Any] = {
            "user": user_id,
        }

        if active is not None:
            json_data["active"] = active

        response = self.api_client.post(
            "/api/v1/iam/updateUser",
            json_data=json_data,
        )

        return from_dict(User, response.get("user", {}))

    def get_user_details(self, user_id: str) -> Optional[UserDetails]:
        """
        Get complete user information including roles and resource assignments.

        This method makes multiple API calls to assemble a comprehensive user profile:
        - Basic user information (from get_user)
        - Assigned roles
        - Assigned resource roles
        - Group memberships

        Args:
            user_id: The user ID or CRN

        Returns:
            The UserDetails, or None if the user doesn't exist
        """
        user = self.get_user(user_id=user_id)
        if not user:
            return None

        return UserDetails(
            **vars(user),
            roles=self.list_user_assigned_roles(user=user_id),
            resourceAssignments=self.list_user_assigned_resource_roles(user=user_id),
            groups=self.list_groups_for_user(user_id=user_id),
        )

    def get_user_details_by_email(self, email: str) -> Optional[UserDetails]:
        """
        Get complete user information by email address.

        This method searches for a user by email and returns complete user details.
        Useful for idempotency when user_id is not available.

        Args:
            email: The email address of the user to find

        Returns:
            The UserDetails, or None if the user doesn't exist
        """
        for user in self.list_users():
            user_id = user.userId
            if user.email == email and isinstance(user_id, str) and user_id:
                return self.get_user_details(user_id=user_id)
        return None

    def get_group_names(self, group_crns: List[str]) -> List[str]:
        """
        Resolve group CRNs to group names.

        Args:
            group_crns: List of group CRNs (e.g. from list_groups_for_user)

        Returns:
            List of group names, in the order returned by the API
        """
        if not group_crns:
            return []

        groups_response = self.list_groups(group_names=group_crns)
        return [
            group["groupName"]
            for group in groups_response.get("groups", [])
            if group.get("groupName")
        ]

    def manage_user_groups(
        self,
        user_id: str,
        current_groups: List[str],
        desired_groups: List[str],
        purge: bool = False,
    ) -> bool:
        """
        Manage user group memberships.

        Note: This method will NOT create groups automatically. Groups must exist
        before adding users to them. Use the iam_group module to create groups.

        Args:
            user_id: The user ID or CRN
            current_groups: List of current group CRNs (from list_groups_for_user)
            desired_groups: List of desired group names
            purge: If True, remove user from groups not in desired list

        Returns:
            True if changes were made, False otherwise

        Raises:
            CdpError: If a desired group does not exist
        """
        changed = False

        # Fetch actual group names for current group CRNs
        current_group_names = set(self.get_group_names(current_groups))

        desired_group_names = set(desired_groups)

        if purge:
            groups_to_remove = current_group_names - desired_group_names
            for group_name in groups_to_remove:
                self.remove_user_from_group(user_id=user_id, group_name=group_name)
                changed = True

        groups_to_add = desired_group_names - current_group_names
        for group_name in groups_to_add:
            # Check if group exists, raise error if it doesn't
            if not self.get_group_details(group_name):
                raise CdpError(
                    f"Group '{group_name}' does not exist. "
                    f"Please create the group using the iam_group module before adding users to it.",
                    status=404,
                )
            self.add_user_to_group(user_id=user_id, group_name=group_name)
            changed = True

        return changed

    def manage_user_roles(
        self,
        user_id: str,
        current_roles: List[str],
        desired_roles: List[str],
        purge: bool = False,
    ) -> bool:
        """
        Manage user role assignments.

        Args:
            user_id: The user ID or CRN
            current_roles: List of current role CRNs
            desired_roles: List of desired role CRNs
            purge: If True, remove roles not in desired list

        Returns:
            True if changes were made, False otherwise
        """
        changed = False

        if purge:
            roles_to_remove = [
                role for role in current_roles if role not in desired_roles
            ]
            for role in roles_to_remove:
                self.unassign_user_role(user_id=user_id, role=role)
                changed = True

        roles_to_add = [role for role in desired_roles if role not in current_roles]
        for role in roles_to_add:
            self.assign_user_role(user_id=user_id, role=role)
            changed = True

        return changed

    def manage_user_resource_roles(
        self,
        user_id: str,
        current_assignments: List[ResourceAssignment],
        desired_assignments: List[ResourceAssignment],
        purge: bool = False,
    ) -> bool:
        """
        Manage user resource role assignments.

        Args:
            user_id: The user ID or CRN
            current_assignments: List of current resource role assignments
            desired_assignments: List of desired resource role assignments
            purge: If True, remove assignments not in desired list

        Returns:
            True if changes were made, False otherwise
        """
        changed = False

        current_set = {(a.resourceCrn, a.resourceRoleCrn) for a in current_assignments}
        desired_set = {(a.resourceCrn, a.resourceRoleCrn) for a in desired_assignments}

        if purge:
            assignments_to_remove = current_set - desired_set
            for resource_crn, resource_role_crn in assignments_to_remove:
                self.unassign_user_resource_role(
                    user_id=user_id,
                    resource_crn=resource_crn,
                    resource_role_crn=resource_role_crn,
                )
                changed = True

        assignments_to_add = desired_set - current_set
        for resource_crn, resource_role_crn in assignments_to_add:
            self.assign_user_resource_role(
                user_id=user_id,
                resource_crn=resource_crn,
                resource_role_crn=resource_role_crn,
            )
            changed = True

        return changed

    def assign_user_role(self, user_id: str, role: str) -> Dict[str, Any]:
        """
        Assign a role to a user.

        Args:
            user_id: The user ID or CRN
            role: The role CRN to assign

        Returns:
            Response from the API
        """
        json_data: Dict[str, Any] = {
            "user": user_id,
            "role": role,
        }

        return self.api_client.post(
            "/api/v1/iam/assignUserRole",
            json_data=json_data,
        )

    def assign_user_resource_role(
        self,
        user_id: str,
        resource_crn: str,
        resource_role_crn: str,
    ) -> Dict[str, Any]:
        """
        Assign a resource role to a user.

        Args:
            user_id: The user ID or CRN
            resource_crn: The resource CRN
            resource_role_crn: The resource role CRN to assign

        Returns:
            Response from the API
        """
        json_data: Dict[str, Any] = {
            "user": user_id,
            "resourceCrn": resource_crn,
            "resourceRoleCrn": resource_role_crn,
        }

        return self.api_client.post(
            "/api/v1/iam/assignUserResourceRole",
            json_data=json_data,
        )

    def unassign_user_role(self, user_id: str, role: str) -> Dict[str, Any]:
        """
        Unassign a role from a user.

        Args:
            user_id: The user ID or CRN
            role: The role CRN to unassign

        Returns:
            Response from the API
        """
        json_data: Dict[str, Any] = {
            "user": user_id,
            "role": role,
        }

        return self.api_client.post(
            "/api/v1/iam/unassignUserRole",
            json_data=json_data,
        )

    def unassign_user_resource_role(
        self,
        user_id: str,
        resource_crn: str,
        resource_role_crn: str,
    ) -> Dict[str, Any]:
        """
        Unassign a resource role from a user.

        Args:
            user_id: The user ID or CRN
            resource_crn: The resource CRN
            resource_role_crn: The resource role CRN to unassign

        Returns:
            Response from the API
        """
        json_data: Dict[str, Any] = {
            "user": user_id,
            "resourceCrn": resource_crn,
            "resourceRoleCrn": resource_role_crn,
        }

        return self.api_client.post(
            "/api/v1/iam/unassignUserResourceRole",
            json_data=json_data,
        )

    def set_workload_password(
        self,
        password: str,
        actor_crn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set the workload password for an actor.

        This will be the actor's password in all Environments they have access to,
        including Environments they are given access to after setting the password.
        The password plaintext is not kept.

        Args:
            password: The password value to set
            actor_crn: The CRN of the user or machine user for whom the password will be set.
                      If not provided, it defaults to the user making the request.

        Returns:
            Response from the API
        """
        json_data: Dict[str, Any] = {
            "password": password,
        }

        if actor_crn is not None:
            json_data["actorCrn"] = actor_crn

        return self.api_client.post(
            "/api/v1/iam/setWorkloadPassword",
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
            squelch={404: {}},
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
            squelch={404: {}},
        )

    @CdpClient.paginated()
    def _list_user_assigned_resource_roles_page(
        self,
        user: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listUserAssignedResourceRoles call; pagination is handled by the decorator."""
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

    def list_user_assigned_resource_roles(
        self,
        user: Optional[str] = None,
    ) -> List[ResourceAssignment]:
        """
        List resource roles assigned to a user with automatic pagination.

        Args:
            user: Optional user CRN or ID. If not provided, defaults to the user making the request.

        Returns:
            List of ResourceAssignment objects
        """
        result = self._list_user_assigned_resource_roles_page(user=user)
        return [
            from_dict(ResourceAssignment, assignment)
            for assignment in result.get("resourceAssignments", [])
        ]

    @CdpClient.paginated()
    def _list_user_assigned_roles_page(
        self,
        user: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listUserAssignedRoles call; pagination is handled by the decorator."""
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

    def list_user_assigned_roles(self, user: Optional[str] = None) -> List[str]:
        """
        List roles assigned to a user with automatic pagination.

        Args:
            user: Optional user CRN or ID. If not provided, defaults to the user making the request.

        Returns:
            List of role CRNs
        """
        result = self._list_user_assigned_roles_page(user=user)
        return result.get("roleCrns", [])

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

    @CdpClient.paginated()
    def _list_machine_users_page(
        self,
        machine_user_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listMachineUsers call; pagination is handled by the decorator."""
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
            squelch={404: {}},
        )

    def list_machine_users(
        self,
        machine_user_names: Optional[List[str]] = None,
    ) -> List[MachineUser]:
        """
        List IAM machine users with automatic pagination.

        Args:
            machine_user_names: Optional list of machine user names or CRNs to filter by

        Returns:
            List of machine users
        """
        result = self._list_machine_users_page(machine_user_names=machine_user_names)
        return [
            from_dict(MachineUser, machine_user)
            for machine_user in result.get("machineUsers", [])
        ]

    def get_machine_user_details(
        self,
        machine_user_name: str,
    ) -> Optional[MachineUserDetails]:
        """
        Get complete machine user information including roles and resource assignments.

        This method makes multiple API calls to assemble a comprehensive machine user profile:
        - Basic machine user information (from list_machine_users)
        - Assigned roles
        - Assigned resource roles

        Returns:
            The machine user with its assignments, or None if the machine user doesn't exist
        """
        machine_users = self.list_machine_users(
            machine_user_names=[machine_user_name],
        )

        if not machine_users:
            return None

        return MachineUserDetails(
            **vars(machine_users[0]),
            roles=self.list_machine_user_assigned_roles(
                machine_user_name=machine_user_name,
            ),
            resourceAssignments=self.list_machine_user_assigned_resource_roles(
                machine_user_name=machine_user_name,
            ),
        )

    def manage_machine_user_roles(
        self,
        machine_user_name: str,
        current_roles: List[str],
        desired_roles: List[str],
        purge: bool = False,
    ) -> bool:
        """
        Manage machine user role assignments.

        Args:
            machine_user_name: The name of the machine user
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
                self.unassign_machine_user_role(
                    machine_user_name=machine_user_name,
                    role=role_crn,
                )
                changed = True

        # Add missing roles
        roles_to_add = [role for role in desired_roles if role not in current_roles]
        for role_crn in roles_to_add:
            self.assign_machine_user_role(
                machine_user_name=machine_user_name,
                role=role_crn,
            )
            changed = True

        return changed

    def manage_machine_user_resource_roles(
        self,
        machine_user_name: str,
        current_assignments: List[ResourceAssignment],
        desired_assignments: List[ResourceAssignment],
        purge: bool = False,
    ) -> bool:
        """
        Manage machine user resource role assignments.

        Args:
            machine_user_name: The name of the machine user
            current_assignments: List of current resource role assignments
            desired_assignments: List of desired resource role assignments
            purge: If True, remove assignments not in desired list

        Returns:
            True if changes were made, False otherwise
        """
        changed = False

        current_set = {(a.resourceCrn, a.resourceRoleCrn) for a in current_assignments}
        desired_set = {(a.resourceCrn, a.resourceRoleCrn) for a in desired_assignments}

        if purge:
            for resource_crn, resource_role_crn in current_set - desired_set:
                self.unassign_machine_user_resource_role(
                    machine_user_name=machine_user_name,
                    resource_crn=resource_crn,
                    resource_role_crn=resource_role_crn,
                )
                changed = True

        for resource_crn, resource_role_crn in desired_set - current_set:
            self.assign_machine_user_resource_role(
                machine_user_name=machine_user_name,
                resource_crn=resource_crn,
                resource_role_crn=resource_role_crn,
            )
            changed = True

        return changed

    def create_machine_user(self, machine_user_name: str) -> MachineUser:
        """
        Create a new machine user.

        Args:
            machine_user_name: The name of the machine user to create

        Returns:
            The created machine user
        """
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
        }

        response = self.api_client.post(
            "/api/v1/iam/createMachineUser",
            json_data=json_data,
        )
        return from_dict(MachineUser, response.get("machineUser", {}))

    def delete_machine_user(self, machine_user_name: str) -> DeleteMachineUserResponse:
        """
        Delete a machine user.

        Args:
            machine_user_name: The name or CRN of the machine user to delete

        Returns:
            The resources that were released by the deletion
        """
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
        }

        response = self.api_client.post(
            "/api/v1/iam/deleteMachineUser",
            json_data=json_data,
        )
        return from_dict(DeleteMachineUserResponse, response or {})

    # Machine User Role Assignment Methods

    def assign_machine_user_role(
        self,
        machine_user_name: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Assign a role to a machine user.

        Args:
            machine_user_name: The machine user name or CRN
            role: The role name or CRN to assign

        Returns:
            Response confirming the role was assigned to the machine user
        """
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
            "role": role,
        }

        return self.api_client.post(
            "/api/v1/iam/assignMachineUserRole",
            json_data=json_data,
        )

    def assign_machine_user_resource_role(
        self,
        machine_user_name: str,
        resource_crn: str,
        resource_role_crn: str,
    ) -> Dict[str, Any]:
        """
        Assign a resource role to a machine user.

        Args:
            machine_user_name: The machine user name or CRN
            resource_crn: The resource CRN for which the resource role rights are granted
            resource_role_crn: The CRN of the resource role being assigned

        Returns:
            Response confirming the resource role was assigned to the machine user
        """
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
            "resourceCrn": resource_crn,
            "resourceRoleCrn": resource_role_crn,
        }

        return self.api_client.post(
            "/api/v1/iam/assignMachineUserResourceRole",
            json_data=json_data,
        )

    def unassign_machine_user_role(
        self,
        machine_user_name: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Unassign a role from a machine user.

        Args:
            machine_user_name: The machine user name or CRN
            role: The role name or CRN to unassign

        Returns:
            Response confirming the role was unassigned from the machine user
        """
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
            "role": role,
        }

        return self.api_client.post(
            "/api/v1/iam/unassignMachineUserRole",
            json_data=json_data,
        )

    def unassign_machine_user_resource_role(
        self,
        machine_user_name: str,
        resource_crn: str,
        resource_role_crn: str,
    ) -> Dict[str, Any]:
        """
        Unassign a resource role from a machine user.

        Args:
            machine_user_name: The machine user name or CRN
            resource_crn: The CRN of the resource for which the resource role rights will be unassigned
            resource_role_crn: The CRN of the resource role to unassign

        Returns:
            Response confirming the resource role was unassigned from the machine user
        """
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
            "resourceCrn": resource_crn,
            "resourceRoleCrn": resource_role_crn,
        }

        return self.api_client.post(
            "/api/v1/iam/unassignMachineUserResourceRole",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def _list_machine_user_assigned_roles_page(
        self,
        machine_user_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listMachineUserAssignedRoles call; pagination is handled by the decorator."""
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
        }

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listMachineUserAssignedRoles",
            json_data=json_data,
        )

    def list_machine_user_assigned_roles(self, machine_user_name: str) -> List[str]:
        """
        List roles assigned to a machine user with automatic pagination.

        Args:
            machine_user_name: The machine user name or CRN

        Returns:
            List of role CRNs
        """
        result = self._list_machine_user_assigned_roles_page(
            machine_user_name=machine_user_name,
        )
        return result.get("roleCrns", [])

    @CdpClient.paginated()
    def _list_machine_user_assigned_resource_roles_page(
        self,
        machine_user_name: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Raw listMachineUserAssignedResourceRoles call; pagination is handled by the decorator."""
        json_data: Dict[str, Any] = {
            "machineUserName": machine_user_name,
        }

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listMachineUserAssignedResourceRoles",
            json_data=json_data,
        )

    def list_machine_user_assigned_resource_roles(
        self,
        machine_user_name: str,
    ) -> List[ResourceAssignment]:
        """
        List resource roles assigned to a machine user with automatic pagination.

        Args:
            machine_user_name: The machine user name or CRN

        Returns:
            List of resource role assignments
        """
        result = self._list_machine_user_assigned_resource_roles_page(
            machine_user_name=machine_user_name,
        )
        return [
            from_dict(ResourceAssignment, assignment)
            for assignment in result.get("resourceAssignments", [])
        ]

    def generate_workload_auth_token(
        self,
        workload_name: str,
        environment_crn: Optional[str] = None,
        exclude_groups: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Generate an authentication token for workload APIs.

        Args:
            workload_name: The workload name (DE, DF, OPDB)
            environment_crn: The environment CRN, required by DF
            exclude_groups: Whether to exclude 'groups' claim from the token

        Returns:
            Response containing token, endpoint URL, and expiration
        """
        json_data: Dict[str, Any] = {
            "workloadName": workload_name,
        }

        if environment_crn is not None:
            json_data["environmentCrn"] = environment_crn

        if exclude_groups is not None:
            json_data["excludeGroups"] = exclude_groups

        return self.api_client.post(
            "/api/v1/iam/generateWorkloadAuthToken",
            json_data=json_data,
        )

    @CdpClient.paginated()
    def list_saml_providers(
        self,
        saml_provider_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List SAML providers with automatic pagination.

        Args:
            saml_provider_names: Optional list of SAML provider names or CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing SAML providers list
        """
        json_data: Dict[str, Any] = {}

        if saml_provider_names is not None:
            json_data["samlProviderNames"] = saml_provider_names

        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/iam/listSamlProviders",
            json_data=json_data,
        )

    def get_default_identity_provider(self) -> Dict[str, Any]:
        """
        Get the default identity provider for the account.

        Returns:
            Response containing the default identity provider information
        """
        return self.api_client.post(
            "/api/v1/iam/getDefaultIdentityProvider",
            json_data={},
        )
