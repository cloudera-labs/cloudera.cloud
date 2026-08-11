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

from ansible_collections.cloudera.cloud.plugins.modules import dw_secret
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    DwSecret,
    DwSecretProperties,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "example-cluster-id"
SECRET_NAME = "mytestsecret"
PROVIDER_KEY = "my-provider-key"


@pytest.fixture
def dw_secret_module_args(module_args):
    """Fixture to pre-populate common dw_secret module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        args.update(
            {
                "endpoint": BASE_URL,
                "access_key": ACCESS_KEY,
                "private_key": PRIVATE_KEY,
                "cluster_id": CLUSTER_ID,
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def dw_secret_client(mocker):
    """Patch load_cdp_config and CdpDwClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_secret.CdpDwClient",
        autospec=True,
    ).return_value


def test_present_create_k8s(dw_secret_module_args, dw_secret_client):
    """state=present with secret_value creates a Kubernetes secret."""
    created = DwSecret(secretName=SECRET_NAME, createdBy="crn:user")
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_value": "s3cr3t",
            "state": "present",
        },
    )

    dw_secret_client.get_secret.return_value = None
    dw_secret_client.create_secret.return_value = created

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    assert result.value.secret["secretName"] == SECRET_NAME
    dw_secret_client.create_secret.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        secret_name=SECRET_NAME,
        secret_value="s3cr3t",
    )
    dw_secret_client.register_secret.assert_not_called()


def test_present_register_azure(dw_secret_module_args, dw_secret_client):
    """state=present with secret_provider_key + azure_vault_name registers a secret."""
    registered = DwSecret(
        secretName=SECRET_NAME,
        secretProviderKey=PROVIDER_KEY,
        properties=DwSecretProperties(azureVaultName="my-vault", cloudProvider="AZURE"),
    )
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_provider_key": PROVIDER_KEY,
            "azure_vault_name": "my-vault",
            "state": "present",
        },
    )

    dw_secret_client.get_secret.return_value = None
    dw_secret_client.register_secret.return_value = registered

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    assert result.value.secret["secretProviderKey"] == PROVIDER_KEY
    dw_secret_client.register_secret.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        secret_name=SECRET_NAME,
        secret_provider_key=PROVIDER_KEY,
        azure_vault_name="my-vault",
    )
    dw_secret_client.create_secret.assert_not_called()


def test_present_register_without_azure(dw_secret_module_args, dw_secret_client):
    """Registration without azure_vault_name passes azure_vault_name=None."""
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_provider_key": PROVIDER_KEY,
            "state": "present",
        },
    )

    dw_secret_client.get_secret.return_value = None
    dw_secret_client.register_secret.return_value = DwSecret(
        secretName=SECRET_NAME,
        secretProviderKey=PROVIDER_KEY,
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    dw_secret_client.register_secret.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        secret_name=SECRET_NAME,
        secret_provider_key=PROVIDER_KEY,
        azure_vault_name=None,
    )


def test_present_idempotent(dw_secret_module_args, dw_secret_client):
    """An existing secret is left unchanged (secrets are immutable)."""
    existing = DwSecret(secretName=SECRET_NAME, secretProviderKey=PROVIDER_KEY)
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_value": "s3cr3t",
            "state": "present",
        },
    )

    dw_secret_client.get_secret.return_value = existing

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is False
    assert result.value.secret["secretName"] == SECRET_NAME
    dw_secret_client.create_secret.assert_not_called()
    dw_secret_client.register_secret.assert_not_called()


def test_absent_deletes(dw_secret_module_args, dw_secret_client):
    """state=absent deletes an existing secret."""
    existing = DwSecret(secretName=SECRET_NAME)
    dw_secret_module_args({"name": SECRET_NAME, "state": "absent"})

    dw_secret_client.get_secret.return_value = existing

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    dw_secret_client.delete_secret.assert_called_once_with(CLUSTER_ID, SECRET_NAME)


def test_absent_noop(dw_secret_module_args, dw_secret_client):
    """state=absent is a no-op when the secret does not exist."""
    dw_secret_module_args({"name": SECRET_NAME, "state": "absent"})

    dw_secret_client.get_secret.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is False
    dw_secret_client.delete_secret.assert_not_called()


def test_check_mode_create_does_not_call_api(dw_secret_module_args, dw_secret_client):
    """check_mode reports changed without calling create_secret."""
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_value": "s3cr3t",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    dw_secret_client.get_secret.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    assert result.value.secret["secretName"] == SECRET_NAME
    dw_secret_client.create_secret.assert_not_called()


def test_present_create_reports_diff(dw_secret_module_args, dw_secret_client):
    """Creating a secret populates diff.after (never the secret value) under --diff."""
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_value": "s3cr3t",
            "state": "present",
            "_ansible_diff": True,
        },
    )

    dw_secret_client.get_secret.return_value = None
    dw_secret_client.create_secret.return_value = DwSecret(secretName=SECRET_NAME)

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    assert result.value.diff == {
        "before": {},
        "after": {"secretName": SECRET_NAME},
    }


def test_absent_reports_diff(dw_secret_module_args, dw_secret_client):
    """Deleting a secret populates diff.before under --diff."""
    existing = DwSecret(secretName=SECRET_NAME, secretProviderKey=PROVIDER_KEY)
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    dw_secret_client.get_secret.return_value = existing

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret.main()

    assert result.value.changed is True
    assert result.value.diff == {
        "before": {"secretName": SECRET_NAME, "secretProviderKey": PROVIDER_KEY},
        "after": {},
    }


def test_mutually_exclusive_value_and_provider_key(
    dw_secret_module_args,
    dw_secret_client,
):
    """secret_value and secret_provider_key are mutually exclusive."""
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_value": "s3cr3t",
            "secret_provider_key": PROVIDER_KEY,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson):
        dw_secret.main()


def test_present_requires_a_provisioning_approach(
    dw_secret_module_args,
    dw_secret_client,
):
    """state=present without secret_value or secret_provider_key fails."""
    dw_secret_module_args({"name": SECRET_NAME, "state": "present"})

    with pytest.raises(AnsibleFailJson):
        dw_secret.main()


def test_azure_vault_requires_provider_key(dw_secret_module_args, dw_secret_client):
    """azure_vault_name requires secret_provider_key."""
    dw_secret_module_args(
        {
            "name": SECRET_NAME,
            "secret_value": "s3cr3t",
            "azure_vault_name": "my-vault",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson):
        dw_secret.main()
