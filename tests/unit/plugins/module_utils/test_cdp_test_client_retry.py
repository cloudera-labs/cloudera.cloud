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

"""Unit tests for the CdpTestClient with_retry decorator."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from urllib.error import HTTPError, URLError

import pytest

from ansible_collections.cloudera.cloud.tests.unit import with_retry


class _Client:
    """Minimal stand-in exposing the max_retries attribute with_retry reads."""

    def __init__(self, max_retries=3):
        self.max_retries = max_retries


@pytest.fixture(autouse=True)
def _no_sleep(mocker):
    """Keep backoff instantaneous."""
    return mocker.patch(
        "ansible_collections.cloudera.cloud.tests.unit.time.sleep",
    )


def test_returns_immediately_on_success(_no_sleep):
    """A call that succeeds first try is not retried and does not sleep."""
    calls = {"n": 0}

    @with_retry
    def op(self):
        calls["n"] += 1
        return "ok"

    assert op(_Client(3)) == "ok"
    assert calls["n"] == 1
    _no_sleep.assert_not_called()


def test_retries_transient_then_succeeds(_no_sleep):
    """Transient errors are retried with backoff until the call succeeds."""
    calls = {"n": 0}

    @with_retry
    def op(self):
        calls["n"] += 1
        if calls["n"] < 3:
            raise URLError("connection reset")
        return "ok"

    with pytest.warns(UserWarning):
        assert op(_Client(3)) == "ok"

    assert calls["n"] == 3
    assert _no_sleep.call_count == 2  # slept before each of the two retries


def test_exhausts_retries_and_reraises(_no_sleep):
    """When every attempt fails transiently, the last exception propagates."""
    calls = {"n": 0}

    @with_retry
    def op(self):
        calls["n"] += 1
        raise OSError("network down")

    with pytest.warns(UserWarning):
        with pytest.raises(OSError, match="network down"):
            op(_Client(2))

    assert calls["n"] == 2  # max_retries attempts, no more


def test_http_error_is_not_retried(_no_sleep):
    """HTTPError is semantic, not transient: re-raised immediately, no sleep."""
    calls = {"n": 0}

    @with_retry
    def op(self):
        calls["n"] += 1
        raise HTTPError(url="u", code=404, msg="nf", hdrs=None, fp=None)

    with pytest.raises(HTTPError):
        op(_Client(3))

    assert calls["n"] == 1
    _no_sleep.assert_not_called()
