#!/usr/bin/env bash

# Copyright 2023 Cloudera, Inc. All Rights Reserved.
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

set -e

pushd "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
trap "{ popd; }" EXIT

# Create collection documentation into temporary directory
rm -rf temp-rst
mkdir -p temp-rst
chmod og-w temp-rst  # antsibull-docs wants that directory only readable by itself
antsibull-docs \
    --config-file antsibull-docs.cfg \
    collection \
    --use-current \
    --squash-hierarchy \
    --dest-dir temp-rst \
    cloudera.cloud

# Copy collection documentation into source directory
rsync -cprv --delete-after temp-rst/ rst/

# Build Sphinx site
sphinx-build -M html rst build -c . -W --keep-going

# Copy Cloudera CSS overrides into source directory
cp cloudera.css build/html/_static/css
