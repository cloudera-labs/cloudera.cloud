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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    ActorResponse,
    AwsOptionsNonTransparentProxyResponse,
    AwsOptionsResponse,
    AzureOptionsResponse,
    CdpDwClient,
    ClusterSummary,
    DW_CLUSTER_FAILED_STATUSES,
    DW_CLUSTER_RUNNING_STATUSES,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
    to_dict,
)


CLUSTER_ID = "cluster-abc123"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-abc123"


# ========================================================================
# Dataclass tests
# ========================================================================


class TestActorResponse:
    def test_defaults_are_nullable(self):
        actor = ActorResponse()
        assert actor.crn is NULLABLE
        assert actor.email is NULLABLE
        assert actor.workloadUsername is NULLABLE
        assert actor.machineUsername is NULLABLE

    def test_from_dict(self):
        data = {"crn": "crn:user:1", "email": "test@example.com"}
        actor = from_dict(ActorResponse, data)
        assert actor.crn == "crn:user:1"
        assert actor.email == "test@example.com"
        assert actor.workloadUsername is NULLABLE

    def test_to_dict_excludes_nullable(self):
        actor = ActorResponse(email="test@example.com")
        result = to_dict(actor)
        assert result == {"email": "test@example.com"}
        assert "crn" not in result


class TestAwsOptionsNonTransparentProxyResponse:
    def test_defaults_are_nullable(self):
        proxy = AwsOptionsNonTransparentProxyResponse()
        assert proxy.use is NULLABLE
        assert proxy.bypassedDomains is NULLABLE

    def test_from_dict(self):
        data = {"use": True, "bypassedDomains": ["example.com"]}
        proxy = from_dict(AwsOptionsNonTransparentProxyResponse, data)
        assert proxy.use is True
        assert proxy.bypassedDomains == ["example.com"]

    def test_to_dict_excludes_nullable(self):
        proxy = AwsOptionsNonTransparentProxyResponse(use=False)
        result = to_dict(proxy)
        assert result == {"use": False}
        assert "bypassedDomains" not in result


class TestAwsOptionsResponse:
    def test_from_dict(self):
        data = {
            "lbSubnetIds": ["subnet-1", "subnet-2"],
            "reducedPermissionMode": True,
        }
        opts = from_dict(AwsOptionsResponse, data)
        assert opts.lbSubnetIds == ["subnet-1", "subnet-2"]
        assert opts.reducedPermissionMode is True
        assert opts.customAmiId is NULLABLE
        assert opts.nonTransparentProxy is NULLABLE

    def test_from_dict_with_non_transparent_proxy(self):
        data = {
            "lbSubnetIds": ["subnet-1"],
            "nonTransparentProxy": {
                "use": True,
                "bypassedDomains": ["internal.corp"],
            },
        }
        opts = from_dict(AwsOptionsResponse, data)
        assert isinstance(
            opts.nonTransparentProxy,
            AwsOptionsNonTransparentProxyResponse,
        )
        assert opts.nonTransparentProxy.use is True
        assert opts.nonTransparentProxy.bypassedDomains == ["internal.corp"]

    def test_to_dict_round_trip(self):
        opts = AwsOptionsResponse(
            lbSubnetIds=["subnet-1"],
            kmsKey="arn:aws:kms:key",
        )
        result = to_dict(opts)
        assert result == {
            "lbSubnetIds": ["subnet-1"],
            "kmsKey": "arn:aws:kms:key",
        }


class TestAzureOptionsResponse:
    def test_from_dict(self):
        data = {
            "subnetId": "subnet-az",
            "enableAZ": True,
            "privateDNSZoneAKS": "dns.zone",
            "aksPodCIDR": "10.0.0.0/16",
        }
        opts = from_dict(AzureOptionsResponse, data)
        assert opts.subnetId == "subnet-az"
        assert opts.enableAZ is True
        assert opts.privateDNSZoneAKS == "dns.zone"
        assert opts.aksPodCIDR == "10.0.0.0/16"
        assert opts.enablePrivateSQL is NULLABLE


class TestClusterSummary:
    def test_from_dict_with_nested_dataclasses(self):
        data = {
            "id": CLUSTER_ID,
            "name": "test-cluster",
            "status": "Running",
            "cloudPlatform": "AWS",
            "environmentCrn": ENV_CRN,
            "creator": {"crn": "crn:user:1", "email": "test@example.com"},
            "awsOptions": {
                "lbSubnetIds": ["subnet-1"],
                "reducedPermissionMode": True,
            },
        }
        cluster = from_dict(ClusterSummary, data)
        assert cluster.id == CLUSTER_ID
        assert cluster.status == "Running"
        assert isinstance(cluster.creator, ActorResponse)
        assert cluster.creator.email == "test@example.com"
        assert isinstance(cluster.awsOptions, AwsOptionsResponse)
        assert cluster.awsOptions.lbSubnetIds == ["subnet-1"]
        assert cluster.azureOptions is NULLABLE

    def test_from_dict_with_azure_options(self):
        data = {
            "id": "cluster-az",
            "cloudPlatform": "AZURE",
            "azureOptions": {
                "subnetId": "subnet-az",
                "enablePrivateAKS": True,
                "privateDNSZoneSQL": "sql.dns.zone",
            },
        }
        cluster = from_dict(ClusterSummary, data)
        assert isinstance(cluster.azureOptions, AzureOptionsResponse)
        assert cluster.azureOptions.enablePrivateAKS is True
        assert cluster.azureOptions.privateDNSZoneSQL == "sql.dns.zone"
        assert cluster.awsOptions is NULLABLE

    def test_to_dict_round_trip(self):
        cluster = ClusterSummary(
            id=CLUSTER_ID,
            status="Running",
            creator=ActorResponse(email="test@example.com"),
        )
        result = to_dict(cluster)
        assert result["id"] == CLUSTER_ID
        assert result["status"] == "Running"
        assert result["creator"] == {"email": "test@example.com"}
        assert "awsOptions" not in result


# ========================================================================
# Client method tests
# ========================================================================


class TestDescribeCluster:
    def test_returns_cluster_summary(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {
            "cluster": {
                "id": CLUSTER_ID,
                "name": "test-cluster",
                "status": "Running",
                "cloudPlatform": "AWS",
                "environmentCrn": ENV_CRN,
            },
        }

        client = CdpDwClient(api_client=api_client)
        result = client.describe_cluster(CLUSTER_ID)

        assert isinstance(result, ClusterSummary)
        assert result.id == CLUSTER_ID
        assert result.status == "Running"

        api_client.post.assert_called_once_with(
            "/api/v1/dw/describeCluster",
            data={"clusterId": CLUSTER_ID},
            squelch={404: None},
        )

    def test_returns_none_on_404(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = None

        client = CdpDwClient(api_client=api_client)
        result = client.describe_cluster(CLUSTER_ID)

        assert result is None

    def test_returns_none_when_cluster_key_absent(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDwClient(api_client=api_client)
        result = client.describe_cluster(CLUSTER_ID)

        assert result is None


class TestListClusters:
    def test_returns_cluster_list(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {
            "clusters": [
                {"id": "cluster-1", "status": "Running"},
                {"id": "cluster-2", "status": "Running"},
            ],
        }

        client = CdpDwClient(api_client=api_client)
        result = client.list_clusters()

        assert len(result) == 2
        assert all(isinstance(c, ClusterSummary) for c in result)
        assert result[0].id == "cluster-1"

        api_client.post.assert_called_once_with(
            "/api/v1/dw/listClusters",
            data={},
            squelch={404: {"clusters": []}},
        )

    def test_filters_by_env_crn(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {
            "clusters": [{"id": "cluster-1", "environmentCrn": ENV_CRN}],
        }

        client = CdpDwClient(api_client=api_client)
        result = client.list_clusters(env_crn=ENV_CRN)

        assert len(result) == 1

        api_client.post.assert_called_once_with(
            "/api/v1/dw/listClusters",
            data={"environmentCrn": ENV_CRN},
            squelch={404: {"clusters": []}},
        )

    def test_returns_empty_on_404(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusters": []}

        client = CdpDwClient(api_client=api_client)
        result = client.list_clusters()

        assert result == []


class TestGetClusterByName:
    def test_returns_matching_cluster(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {
            "clusters": [
                {"id": "cluster-1", "name": "other-cluster", "environmentCrn": ENV_CRN},
                {"id": CLUSTER_ID, "name": "target-cluster", "environmentCrn": ENV_CRN},
            ],
        }

        client = CdpDwClient(api_client=api_client)
        result = client.get_cluster_by_name("target-cluster")

        assert result is not None
        assert isinstance(result, ClusterSummary)
        assert result.id == CLUSTER_ID
        assert result.name == "target-cluster"

    def test_returns_none_when_not_found(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {
            "clusters": [
                {"id": "cluster-1", "name": "other-cluster"},
            ],
        }

        client = CdpDwClient(api_client=api_client)
        result = client.get_cluster_by_name("nonexistent")

        assert result is None

    def test_filters_by_env_crn(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {
            "clusters": [
                {"id": CLUSTER_ID, "name": "target-cluster", "environmentCrn": ENV_CRN},
            ],
        }

        client = CdpDwClient(api_client=api_client)
        result = client.get_cluster_by_name("target-cluster", env_crn=ENV_CRN)

        assert result is not None
        assert result.id == CLUSTER_ID

        api_client.post.assert_called_once_with(
            "/api/v1/dw/listClusters",
            data={"environmentCrn": ENV_CRN},
            squelch={404: {"clusters": []}},
        )

    def test_returns_none_on_empty_list(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusters": []}

        client = CdpDwClient(api_client=api_client)
        result = client.get_cluster_by_name("any-name")

        assert result is None


class TestCreateAwsCluster:
    def test_minimal_payload(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        client = CdpDwClient(api_client=api_client)
        result = client.create_aws_cluster(env_crn=ENV_CRN)

        assert result == CLUSTER_ID

        api_client.post.assert_called_once_with(
            "/api/v1/dw/createAwsCluster",
            data={"environmentCrn": ENV_CRN},
        )

    def test_all_optional_fields(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        client = CdpDwClient(api_client=api_client)
        client.create_aws_cluster(
            env_crn=ENV_CRN,
            use_overlay_network=True,
            use_private_load_balancer=True,
            use_public_worker_node=False,
            lb_subnet_ids=["subnet-lb-1", "subnet-lb-2"],
            worker_subnet_ids=["subnet-w-1"],
            custom_subdomain="my-domain",
            database_backup_retention_period=30,
            whitelist_workload_access_ip_cidrs=["10.0.0.0/8"],
            whitelist_k8s_cluster_access_ip_cidrs=["10.1.0.0/16"],
            custom_ami_id="ami-12345",
            enable_private_eks=True,
            enable_spot_instances=True,
            reduced_permission_mode=True,
            node_role_cdw_managed_policy_arn="arn:aws:iam::policy/cdw",
            custom_registry_options={
                "registryType": "ECR",
                "repositoryUrl": "https://ecr.example.com",
            },
            non_transparent_proxy={"use": True, "bypassedDomains": ["internal.corp"]},
        )

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["environmentCrn"] == ENV_CRN
        assert call_data["useOverlayNetwork"] is True
        assert call_data["usePrivateLoadBalancer"] is True
        assert call_data["usePublicWorkerNode"] is False
        assert call_data["lbSubnetIds"] == ["subnet-lb-1", "subnet-lb-2"]
        assert call_data["workerSubnetIds"] == ["subnet-w-1"]
        assert call_data["customSubdomain"] == "my-domain"
        assert call_data["databaseBackupRetentionPeriod"] == 30
        assert call_data["whitelistWorkloadAccessIpCIDRs"] == ["10.0.0.0/8"]
        assert call_data["whitelistK8sClusterAccessIpCIDRs"] == ["10.1.0.0/16"]
        assert call_data["customAmiId"] == "ami-12345"
        assert call_data["enablePrivateEKS"] is True
        assert call_data["enableSpotInstances"] is True
        assert call_data["reducedPermissionMode"] is True
        assert call_data["nodeRoleCDWManagedPolicyArn"] == "arn:aws:iam::policy/cdw"
        assert call_data["customRegistryOptions"] == {
            "registryType": "ECR",
            "repositoryUrl": "https://ecr.example.com",
        }
        assert call_data["nonTransparentProxy"] == {
            "use": True,
            "bypassedDomains": ["internal.corp"],
        }

    def test_none_optionals_omitted(self, mocker):
        """Optional fields set to None must not appear in the request body."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        client = CdpDwClient(api_client=api_client)
        client.create_aws_cluster(
            env_crn=ENV_CRN,
            use_overlay_network=None,
            custom_ami_id=None,
            custom_registry_options=None,
            non_transparent_proxy=None,
        )

        call_data = api_client.post.call_args[1]["data"]
        assert "useOverlayNetwork" not in call_data
        assert "customAmiId" not in call_data
        assert "customRegistryOptions" not in call_data
        assert "nonTransparentProxy" not in call_data


class TestCreateAzureCluster:
    def test_required_fields(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        client = CdpDwClient(api_client=api_client)
        result = client.create_azure_cluster(
            env_crn=ENV_CRN,
            subnet_name="my-subnet",
            user_assigned_managed_identity="/sub/123/identity/my-id",
        )

        assert result == CLUSTER_ID

        api_client.post.assert_called_once_with(
            "/api/v1/dw/createAzureCluster",
            data={
                "environmentCrn": ENV_CRN,
                "subnetName": "my-subnet",
                "userAssignedManagedIdentity": "/sub/123/identity/my-id",
            },
        )

    def test_azure_specific_field_names(self, mocker):
        """Verify the Azure-specific field naming gotchas from the ADR."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        client = CdpDwClient(api_client=api_client)
        client.create_azure_cluster(
            env_crn=ENV_CRN,
            subnet_name="my-subnet",
            user_assigned_managed_identity="my-id",
            use_overlay_networking=True,
            use_internal_load_balancer=True,
            enable_private_aks=True,
            enable_private_sql=True,
            private_dns_zone_aks="aks.dns.zone",
            private_dns_zone_sql="sql.dns.zone",
            private_sql_subnet_name="sql-subnet",
            aks_pod_cidr="10.0.0.0/16",
            outbound_type="udr",
            custom_registry_options={
                "registryType": "ACR",
                "repositoryUrl": "https://acr.example.com",
            },
        )

        call_data = api_client.post.call_args[1]["data"]
        # Azure uses "Networking" not "Network"
        assert call_data["useOverlayNetworking"] is True
        # Azure uses "Internal" not "Private"
        assert call_data["useInternalLoadBalancer"] is True
        # Azure lowercase "ks" in Aks
        assert call_data["enablePrivateAks"] is True
        # Azure uppercase SQL
        assert call_data["enablePrivateSQL"] is True
        assert call_data["privateDNSZoneAKS"] == "aks.dns.zone"
        assert call_data["privateDNSZoneSQL"] == "sql.dns.zone"
        assert call_data["privateSQLSubnetName"] == "sql-subnet"
        assert call_data["aksPodCIDR"] == "10.0.0.0/16"
        assert call_data["outboundType"] == "udr"
        assert call_data["customRegistryOptions"] == {
            "registryType": "ACR",
            "repositoryUrl": "https://acr.example.com",
        }


class TestCreatePrivateCluster:
    def test_minimal_payload(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        client = CdpDwClient(api_client=api_client)
        result = client.create_private_cluster(env_crn=ENV_CRN)

        assert result == CLUSTER_ID

        api_client.post.assert_called_once_with(
            "/api/v1/dw/createPrivateCluster",
            data={"environmentCrn": ENV_CRN},
        )

    def test_with_db_client_credentials(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"clusterId": CLUSTER_ID}

        creds = {
            "certificate": "-----BEGIN CERT-----",
            "privateKey": "-----BEGIN KEY-----",
        }
        client = CdpDwClient(api_client=api_client)
        client.create_private_cluster(
            env_crn=ENV_CRN,
            storage_class="default",
            db_client_credentials=creds,
            custom_kerberos_principal_hostname="kerberos.host",
        )

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["storageClass"] == "default"
        assert call_data["dbClientCredentials"] == creds
        assert call_data["customKerberosPrincipalHostname"] == "kerberos.host"


class TestDeleteCluster:
    def test_delete_without_force(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDwClient(api_client=api_client)
        client.delete_cluster(CLUSTER_ID)

        api_client.post.assert_called_once_with(
            "/api/v1/dw/deleteCluster",
            data={"clusterId": CLUSTER_ID},
            squelch={404: {}},
        )

    def test_delete_with_force(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDwClient(api_client=api_client)
        client.delete_cluster(CLUSTER_ID, force=True)

        api_client.post.assert_called_once_with(
            "/api/v1/dw/deleteCluster",
            data={"clusterId": CLUSTER_ID, "force": True},
            squelch={404: {}},
        )

    def test_force_false_omits_key(self, mocker):
        """When force=False (default), the 'force' key is not in the payload."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDwClient(api_client=api_client)
        client.delete_cluster(CLUSTER_ID, force=False)

        call_data = api_client.post.call_args[1]["data"]
        assert "force" not in call_data


class TestWaitForClusterState:
    def test_already_at_target(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        described = ClusterSummary(id=CLUSTER_ID, status="Running")
        mocker.patch.object(client, "describe_cluster", return_value=described)

        result = client.wait_for_cluster_state(
            cluster_id=CLUSTER_ID,
            target_statuses=DW_CLUSTER_RUNNING_STATUSES,
        )

        assert isinstance(result, ClusterSummary)
        assert result.id == CLUSTER_ID
        assert result.status == "Running"

    def test_gone_returns_none(self, mocker):
        """Returns None when the cluster is no longer visible (fully deleted)."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        mocker.patch.object(client, "describe_cluster", return_value=None)

        result = client.wait_for_cluster_state(
            cluster_id=CLUSTER_ID,
            target_statuses=DW_CLUSTER_RUNNING_STATUSES,
        )

        assert result is None

    def test_raises_on_error_status(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        described = ClusterSummary(id=CLUSTER_ID, status="Error")
        mocker.patch.object(client, "describe_cluster", return_value=described)

        with pytest.raises(CdpError, match="Error"):
            client.wait_for_cluster_state(
                cluster_id=CLUSTER_ID,
                target_statuses=DW_CLUSTER_RUNNING_STATUSES,
            )

    def test_raises_on_failed_status(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        described = ClusterSummary(id=CLUSTER_ID, status="Failed")
        mocker.patch.object(client, "describe_cluster", return_value=described)

        with pytest.raises(CdpError, match="Failed"):
            client.wait_for_cluster_state(
                cluster_id=CLUSTER_ID,
                target_statuses=DW_CLUSTER_RUNNING_STATUSES,
            )

    def test_raises_on_timeout(self, mocker):
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        described = ClusterSummary(id=CLUSTER_ID, status="Starting")
        mocker.patch.object(client, "describe_cluster", return_value=described)
        mocker.patch("time.sleep")

        # Simulate elapsed time exceeding timeout on the second call
        call_count = 0
        start = 1000.0

        def fake_time():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return start
            return start + 9999

        mocker.patch("time.time", side_effect=fake_time)

        with pytest.raises(CdpError, match="Timeout"):
            client.wait_for_cluster_state(
                cluster_id=CLUSTER_ID,
                target_statuses=DW_CLUSTER_RUNNING_STATUSES,
                timeout=3600,
                delay=15,
            )

    def test_polls_until_target_reached(self, mocker):
        """Polls through intermediate statuses until reaching the target."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        starting = ClusterSummary(id=CLUSTER_ID, status="Starting")
        running = ClusterSummary(id=CLUSTER_ID, status="Running")
        mocker.patch.object(
            client,
            "describe_cluster",
            side_effect=[starting, starting, running],
        )
        mocker.patch("time.sleep")
        mocker.patch("time.time", return_value=1000.0)

        result = client.wait_for_cluster_state(
            cluster_id=CLUSTER_ID,
            target_statuses=DW_CLUSTER_RUNNING_STATUSES,
        )

        assert result.status == "Running"
        assert client.describe_cluster.call_count == 3

    def test_does_not_initiate_actions(self, mocker):
        """The waiter only polls — it never calls create or delete."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        described = ClusterSummary(id=CLUSTER_ID, status="Running")
        mocker.patch.object(client, "describe_cluster", return_value=described)
        create_aws = mocker.patch.object(client, "create_aws_cluster")
        delete = mocker.patch.object(client, "delete_cluster")

        client.wait_for_cluster_state(
            cluster_id=CLUSTER_ID,
            target_statuses=DW_CLUSTER_RUNNING_STATUSES,
        )

        create_aws.assert_not_called()
        delete.assert_not_called()

    def test_delete_wait_returns_none_when_cluster_disappears(self, mocker):
        """Waiting for deletion: cluster disappears (describe returns None)."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDwClient(api_client=api_client)

        deleting = ClusterSummary(id=CLUSTER_ID, status="Deleting")
        mocker.patch.object(
            client,
            "describe_cluster",
            side_effect=[deleting, None],
        )
        mocker.patch("time.sleep")
        mocker.patch("time.time", return_value=1000.0)

        result = client.wait_for_cluster_state(
            cluster_id=CLUSTER_ID,
            target_statuses=set(),
        )

        assert result is None
