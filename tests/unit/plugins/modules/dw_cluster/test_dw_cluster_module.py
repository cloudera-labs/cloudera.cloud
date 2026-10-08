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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

# pylint: disable=redefined-outer-name,unused-argument

from ansible_collections.cloudera.cloud.plugins.modules import dw_cluster
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    ClusterSummary,
    ActorResponse,
    AwsOptionsResponse,
    AzureOptionsResponse,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "cluster-abc123"
ENV_NAME = "my-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-uuid"

CLUSTER_RUNNING = ClusterSummary(
    id=CLUSTER_ID,
    name="test-cluster",
    crn=f"crn:cdp:dw:us-west-1:tenant:cluster:{CLUSTER_ID}",
    environmentCrn=ENV_CRN,
    status="Running",
    cloudPlatform="AWS",
    creationDate="2026-01-01T00:00:00Z",
    creator=ActorResponse(
        crn="crn:cdp:iam:us-west-1:tenant:user:test-user",
        email="test@example.com",
    ),
)

CLUSTER_AZURE = ClusterSummary(
    id="cluster-azure-123",
    name="test-azure-cluster",
    crn="crn:cdp:dw:us-west-1:tenant:cluster:cluster-azure-123",
    environmentCrn=ENV_CRN,
    status="Running",
    cloudPlatform="AZURE",
    creationDate="2026-01-01T00:00:00Z",
    creator=ActorResponse(
        crn="crn:cdp:iam:us-west-1:tenant:user:test-user",
    ),
)


@pytest.fixture
def dw_cluster_module_args(module_args):
    """Fixture to pre-populate common dw_cluster module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def dw_cluster_clients(mocker):
    """Fixture that patches load_cdp_config, CdpDwClient, and CdpEnvClient."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    dw_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_cluster.CdpDwClient",
        autospec=True,
    ).return_value

    env_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_cluster.CdpEnvClient",
        autospec=True,
    ).return_value

    return dw_client, env_client


class TestDwClusterCreateAws:
    """Tests for AWS cluster creation."""

    def test_create_aws_cluster(self, dw_cluster_module_args, dw_cluster_clients):
        """Create an AWS cluster with explicit cloud_platform."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "aws": {
                    "lb_subnets": ["subnet-1", "subnet-2"],
                    "worker_subnets": ["subnet-3"],
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        assert result.value.cluster["id"] == CLUSTER_ID
        dw_client.create_aws_cluster.assert_called_once_with(
            env_crn=ENV_CRN,
            use_overlay_network=None,
            use_private_load_balancer=None,
            use_public_worker_node=None,
            lb_subnet_ids=["subnet-1", "subnet-2"],
            worker_subnet_ids=["subnet-3"],
            custom_subdomain=None,
            database_backup_retention_period=None,
            whitelist_workload_access_ip_cidrs=None,
            whitelist_k8s_cluster_access_ip_cidrs=None,
            custom_ami_id=None,
            enable_private_eks=None,
            enable_spot_instances=None,
            reduced_permission_mode=None,
            node_role_cdw_managed_policy_arn=None,
            custom_registry_options=None,
            non_transparent_proxy=None,
        )

    def test_create_aws_with_all_options(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Create an AWS cluster with all AWS-specific options."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "overlay": True,
                "private_load_balancer": True,
                "public_worker_node": True,
                "custom_subdomain": "my-subdomain",
                "database_backup_retention_period": 30,
                "whitelist_workload_access_ip_cidrs": ["10.0.0.0/8"],
                "whitelist_k8s_cluster_access_ip_cidrs": ["192.168.0.0/16"],
                "aws": {
                    "lb_subnets": ["subnet-1"],
                    "worker_subnets": ["subnet-2"],
                    "custom_ami_id": "ami-0123456789abcdef0",
                    "enable_private_eks": True,
                    "enable_spot_instances": True,
                    "reduced_permission_mode": True,
                    "node_role_cdw_managed_policy_arn": "arn:aws:iam::policy/my-policy",
                    "custom_registry_options": {
                        "registry_type": "ECR",
                        "repository_url": "https://ecr.example.com",
                    },
                    "non_transparent_proxy": {
                        "use": True,
                        "bypassed_domains": ["internal.corp"],
                    },
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.create_aws_cluster.assert_called_once_with(
            env_crn=ENV_CRN,
            use_overlay_network=True,
            use_private_load_balancer=True,
            use_public_worker_node=True,
            lb_subnet_ids=["subnet-1"],
            worker_subnet_ids=["subnet-2"],
            custom_subdomain="my-subdomain",
            database_backup_retention_period=30,
            whitelist_workload_access_ip_cidrs=["10.0.0.0/8"],
            whitelist_k8s_cluster_access_ip_cidrs=["192.168.0.0/16"],
            custom_ami_id="ami-0123456789abcdef0",
            enable_private_eks=True,
            enable_spot_instances=True,
            reduced_permission_mode=True,
            node_role_cdw_managed_policy_arn="arn:aws:iam::policy/my-policy",
            custom_registry_options={
                "registryType": "ECR",
                "repositoryUrl": "https://ecr.example.com",
            },
            non_transparent_proxy={"use": True, "bypassedDomains": ["internal.corp"]},
        )

    def test_create_with_wait(self, dw_cluster_module_args, dw_cluster_clients):
        """Create an AWS cluster with wait=True polls for Running."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "wait": True,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.wait_for_cluster_state.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        assert result.value.cluster["status"] == "Running"
        dw_client.wait_for_cluster_state.assert_called_once()


class TestDwClusterCreateAzure:
    """Tests for Azure cluster creation."""

    def test_create_azure_cluster(self, dw_cluster_module_args, dw_cluster_clients):
        """Create an Azure cluster with required Azure params."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AZURE",
                "azure": {
                    "subnet": "my-subnet",
                    "managed_identity": "my-managed-identity",
                    "enable_az": True,
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_azure_cluster.return_value = "cluster-azure-123"
        dw_client.describe_cluster.return_value = CLUSTER_AZURE

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.create_azure_cluster.assert_called_once_with(
            env_crn=ENV_CRN,
            subnet_name="my-subnet",
            user_assigned_managed_identity="my-managed-identity",
            use_overlay_networking=None,
            use_internal_load_balancer=None,
            enable_az=True,
            enable_private_aks=None,
            enable_private_sql=None,
            enable_spot_instances=None,
            log_analytics_workspace_id=None,
            outbound_type=None,
            private_dns_zone_aks=None,
            private_dns_zone_sql=None,
            private_sql_subnet_name=None,
            aks_pod_cidr=None,
            custom_subdomain=None,
            database_backup_retention_period=None,
            whitelist_workload_access_ip_cidrs=None,
            whitelist_k8s_cluster_access_ip_cidrs=None,
            custom_registry_options=None,
        )

    def test_create_azure_overlay_and_private_lb(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Azure maps overlay to useOverlayNetworking, private_load_balancer to useInternalLoadBalancer."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AZURE",
                "overlay": True,
                "private_load_balancer": True,
                "azure": {
                    "subnet": "my-subnet",
                    "managed_identity": "my-managed-identity",
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_azure_cluster.return_value = "cluster-azure-123"
        dw_client.describe_cluster.return_value = CLUSTER_AZURE

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        call_kwargs = dw_client.create_azure_cluster.call_args[1]
        assert call_kwargs["use_overlay_networking"] is True
        assert call_kwargs["use_internal_load_balancer"] is True


class TestDwClusterCreatePrivateCloud:
    """Tests for Private Cloud cluster creation."""

    def test_create_private_cluster(self, dw_cluster_module_args, dw_cluster_clients):
        """Create a Private Cloud cluster."""
        dw_client, env_client = dw_cluster_clients

        private_cluster = ClusterSummary(
            id="cluster-pvc-123",
            status="Running",
            cloudPlatform="PRIVATE",
            environmentCrn=ENV_CRN,
        )

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "PRIVATE",
                "private_cloud": {
                    "storage_class": "my-storage-class",
                    "db_client_certificate": "cert-content",
                    "db_client_key": "key-content",
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_private_cluster.return_value = "cluster-pvc-123"
        dw_client.describe_cluster.return_value = private_cluster

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.create_private_cluster.assert_called_once_with(
            env_crn=ENV_CRN,
            storage_class="my-storage-class",
            db_client_credentials={
                "certificate": "cert-content",
                "privateKey": "key-content",
            },
            custom_kerberos_principal_hostname=None,
        )

    def test_create_private_cluster_with_kerberos(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Create a Private Cloud cluster with custom Kerberos hostname."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "PRIVATE",
                "private_cloud": {
                    "custom_kerberos_principal_hostname": "kerberos.example.com",
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_private_cluster.return_value = "cluster-pvc-123"
        dw_client.describe_cluster.return_value = ClusterSummary(
            id="cluster-pvc-123",
            status="Running",
        )

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        dw_client.create_private_cluster.assert_called_once_with(
            env_crn=ENV_CRN,
            storage_class=None,
            db_client_credentials=None,
            custom_kerberos_principal_hostname="kerberos.example.com",
        )


class TestDwClusterDelete:
    """Tests for cluster deletion."""

    def test_delete_cluster_by_id(self, dw_cluster_module_args, dw_cluster_clients):
        """Delete a cluster by cluster_id."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "cluster_id": CLUSTER_ID,
                "state": "absent",
                "wait": False,
            },
        )

        dw_client.describe_cluster.side_effect = [CLUSTER_RUNNING, None]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.delete_cluster.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            force=False,
        )

    def test_delete_cluster_by_env(self, dw_cluster_module_args, dw_cluster_clients):
        """Delete a cluster by environment (single cluster)."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "state": "absent",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = [CLUSTER_RUNNING]
        dw_client.describe_cluster.side_effect = [CLUSTER_RUNNING, None]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.delete_cluster.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            force=False,
        )

    def test_delete_ambiguous_env_fails(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Delete fails when environment has multiple clusters."""
        dw_client, env_client = dw_cluster_clients

        cluster2 = ClusterSummary(id="cluster-456", status="Running")

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "state": "absent",
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = [CLUSTER_RUNNING, cluster2]

        with pytest.raises(AnsibleFailJson, match="ambiguous"):
            dw_cluster.main()

    def test_delete_with_force(self, dw_cluster_module_args, dw_cluster_clients):
        """Delete with force=True passes force to the API."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "cluster_id": CLUSTER_ID,
                "state": "absent",
                "force": True,
                "wait": False,
            },
        )

        dw_client.describe_cluster.side_effect = [CLUSTER_RUNNING, None]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.delete_cluster.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            force=True,
        )

    def test_delete_with_wait(self, dw_cluster_module_args, dw_cluster_clients):
        """Delete with wait polls until cluster disappears."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "cluster_id": CLUSTER_ID,
                "state": "absent",
                "wait": True,
            },
        )

        dw_client.describe_cluster.return_value = CLUSTER_RUNNING
        dw_client.wait_for_cluster_state.return_value = None

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.wait_for_cluster_state.assert_called_once()

    def test_absent_already_absent(self, dw_cluster_module_args, dw_cluster_clients):
        """Absent when cluster doesn't exist is a no-op."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "cluster_id": CLUSTER_ID,
                "state": "absent",
            },
        )

        dw_client.describe_cluster.return_value = None

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is False
        assert result.value.cluster == {}
        dw_client.delete_cluster.assert_not_called()


class TestDwClusterPresentExisting:
    """Tests for present state on existing cluster."""

    def test_present_existing_warns(self, dw_cluster_module_args, dw_cluster_clients):
        """Present on existing cluster warns about reconciliation."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "state": "present",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = [CLUSTER_RUNNING]
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is False
        assert result.value.cluster["id"] == CLUSTER_ID
        dw_client.create_aws_cluster.assert_not_called()
        dw_client.create_azure_cluster.assert_not_called()
        dw_client.create_private_cluster.assert_not_called()


class TestDwClusterCheckMode:
    """Tests for check_mode behavior."""

    def test_check_mode_create(self, dw_cluster_module_args, dw_cluster_clients):
        """Check mode create reports changed without making API calls."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "_ansible_check_mode": True,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        assert result.value.cluster == {}
        dw_client.create_aws_cluster.assert_not_called()

    def test_check_mode_delete(self, dw_cluster_module_args, dw_cluster_clients):
        """Check mode delete reports changed without making API calls."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "cluster_id": CLUSTER_ID,
                "state": "absent",
                "_ansible_check_mode": True,
            },
        )

        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.delete_cluster.assert_not_called()


class TestDwClusterCloudPlatformDetection:
    """Tests for cloud platform auto-detection."""

    def test_auto_detect_aws(self, dw_cluster_module_args, dw_cluster_clients):
        """Auto-detect AWS platform from environment."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "auto",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        env_client.describe_environment.return_value = {"cloudPlatform": "AWS"}
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        dw_client.create_aws_cluster.assert_called_once()
        dw_client.create_azure_cluster.assert_not_called()

    def test_auto_detect_azure(self, dw_cluster_module_args, dw_cluster_clients):
        """Auto-detect Azure platform from environment."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "auto",
                "azure": {
                    "subnet": "my-subnet",
                    "managed_identity": "my-managed-identity",
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        env_client.describe_environment.return_value = {"cloudPlatform": "AZURE"}
        dw_client.list_clusters.return_value = []
        dw_client.create_azure_cluster.return_value = "cluster-azure-123"
        dw_client.describe_cluster.return_value = CLUSTER_AZURE

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        dw_client.create_azure_cluster.assert_called_once()
        dw_client.create_aws_cluster.assert_not_called()

    def test_auto_detect_private(self, dw_cluster_module_args, dw_cluster_clients):
        """Auto-detect Private platform from environment (non-AWS/AZURE)."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "auto",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        env_client.describe_environment.return_value = {
            "cloudPlatform": "PRIVATE_CLOUD",
        }
        dw_client.list_clusters.return_value = []
        dw_client.create_private_cluster.return_value = "cluster-pvc-123"
        dw_client.describe_cluster.return_value = ClusterSummary(
            id="cluster-pvc-123",
            status="Running",
        )

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        dw_client.create_private_cluster.assert_called_once()

    def test_auto_detect_env_not_found_fails(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Auto-detect fails with clear message when env can't be described."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "auto",
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        env_client.describe_environment.return_value = None
        dw_client.list_clusters.return_value = []

        with pytest.raises(AnsibleFailJson, match="cloud_platform"):
            dw_cluster.main()

    def test_explicit_platform_skips_env_describe(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Explicit cloud_platform skips environment describe."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        env_client.describe_environment.assert_not_called()


class TestDwClusterAwsParamDeprecation:
    """Tests for deprecated AWS parameter handling."""

    def test_top_level_aws_subnets_used(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Top-level aws_lb_subnets maps to lb_subnet_ids."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "aws_lb_subnets": ["subnet-1"],
                "aws_worker_subnets": ["subnet-2"],
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        call_kwargs = dw_client.create_aws_cluster.call_args[1]
        assert call_kwargs["lb_subnet_ids"] == ["subnet-1"]
        assert call_kwargs["worker_subnet_ids"] == ["subnet-2"]

    def test_nested_aws_takes_precedence(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Nested aws.lb_subnets takes precedence over top-level when identical."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "aws": {
                    "lb_subnets": ["subnet-1"],
                    "worker_subnets": ["subnet-2"],
                },
                "aws_lb_subnets": ["subnet-1"],
                "aws_worker_subnets": ["subnet-2"],
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        call_kwargs = dw_client.create_aws_cluster.call_args[1]
        assert call_kwargs["lb_subnet_ids"] == ["subnet-1"]

    def test_conflicting_aws_params_fails(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Conflicting top-level and nested AWS params fail."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "aws": {
                    "lb_subnets": ["subnet-A"],
                },
                "aws_lb_subnets": ["subnet-B"],
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []

        with pytest.raises(AnsibleFailJson, match="Conflicting"):
            dw_cluster.main()


class TestDwClusterDiff:
    """Tests for diff output."""

    def test_diff_on_create(self, dw_cluster_module_args, dw_cluster_clients):
        """Diff output on create includes after with environmentCrn and cloudPlatform."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "_ansible_diff": True,
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.diff["after"]["environmentCrn"] == ENV_CRN
        assert result.value.diff["after"]["cloudPlatform"] == "AWS"

    def test_diff_on_delete(self, dw_cluster_module_args, dw_cluster_clients):
        """Diff output on delete includes before with existing cluster data."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "cluster_id": CLUSTER_ID,
                "state": "absent",
                "_ansible_diff": True,
                "wait": False,
            },
        )

        dw_client.describe_cluster.side_effect = [CLUSTER_RUNNING, None]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.diff["before"]["id"] == CLUSTER_ID
        assert result.value.diff["before"]["status"] == "Running"


class TestDwClusterDeprecatedParams:
    """Tests for deprecated parameters with no API equivalent."""

    def test_reserved_params_ignored_on_create(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """reserved_compute_nodes, reserved_shared_services_nodes, and
        resource_pool are accepted but silently ignored during cluster creation."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "reserved_compute_nodes": 3,
                "reserved_shared_services_nodes": 2,
                "resource_pool": "my-pool",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        assert result.value.cluster["id"] == CLUSTER_ID
        dw_client.create_aws_cluster.assert_called_once()

    def test_azure_compute_instance_types_ignored(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """azure.compute_instance_types is accepted but not passed to the create API."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AZURE",
                "azure": {
                    "subnet": "my-subnet",
                    "managed_identity": "my-managed-identity",
                    "compute_instance_types": ["Standard_D4s_v3"],
                },
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_azure_cluster.return_value = "cluster-azure-123"
        dw_client.describe_cluster.return_value = CLUSTER_AZURE

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster.main()

        assert result.value.changed is True
        dw_client.create_azure_cluster.assert_called_once()
        call_kwargs = dw_client.create_azure_cluster.call_args[1]
        assert "compute_instance_types" not in call_kwargs


class TestDwClusterEnvCrnResolution:
    """Tests for environment CRN resolution."""

    def test_env_crn_passed_directly(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """A CRN value for env is used directly without calling get_environment_crn."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_CRN,
                "cloud_platform": "AWS",
                "wait": False,
            },
        )

        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        env_client.get_environment_crn.assert_not_called()
        dw_client.create_aws_cluster.assert_called_once()
        assert dw_client.create_aws_cluster.call_args[1]["env_crn"] == ENV_CRN

    def test_env_name_resolved_to_crn(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """A non-CRN env value resolves via CdpEnvClient."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": ENV_NAME,
                "cloud_platform": "AWS",
                "wait": False,
            },
        )

        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []
        dw_client.create_aws_cluster.return_value = CLUSTER_ID
        dw_client.describe_cluster.return_value = CLUSTER_RUNNING

        with pytest.raises(AnsibleExitJson):
            dw_cluster.main()

        env_client.get_environment_crn.assert_called_once_with(ENV_NAME)

    def test_env_crn_resolution_fails(
        self,
        dw_cluster_module_args,
        dw_cluster_clients,
    ):
        """Fail when environment CRN cannot be resolved for create."""
        dw_client, env_client = dw_cluster_clients

        dw_cluster_module_args(
            {
                "env": "nonexistent-env",
                "cloud_platform": "AWS",
            },
        )

        env_client.get_environment_crn.return_value = None
        dw_client.list_clusters.return_value = []

        with pytest.raises(AnsibleFailJson, match="Could not retrieve CRN"):
            dw_cluster.main()
