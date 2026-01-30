# cloudera.cloud - Cloudera on cloud and Data Services

[![Collection Docs](https://img.shields.io/badge/collection-documentation-ff550D?logo=ansible&logoColor=white)](https://cloudera-labs.github.io/cloudera.cloud/)
[![Publishing](https://img.shields.io/badge/Publishing-passing-5555F9?logo=github)](https://github.com/cloudera-labs/cloudera.cloud/actions/workflows/publish_docs.yml)

`cloudera.cloud` is an Ansible collection that lets you manage your **[Cloudera Platform](https://www.cloudera.com/products/cloudera-data-platform.html) on cloud (Public Cloud)** resources. This collection enables you to:

* Create and manage [Datalakes](https://www.cloudera.com/products/open-data-lakehouse.html) and Environments.
* Manage Users and Groups.
* Create and manage [Data Hubs](https://www.cloudera.com/products/data-hub.html) and [Data Services](https://www.cloudera.com/products/data-services.html):
  * [Cloudera Data Flow (CDF)](https://www.cloudera.com/products/dataflow.html)
  * [Cloudera Data Engineering (CDE)](https://www.cloudera.com/products/data-engineering.html)
  * [Cloudera Data Warehouse (CDW)](https://www.cloudera.com/products/data-warehouse.html)
  * [Cloudera AI (CAI)](https://www.cloudera.com/products/machine-learning.html)
  * [Cloudera Operational Database](https://www.cloudera.com/products/operational-db.html)
  * [Cloudera Stream Processing (CSP)](https://www.cloudera.com/products/stream-processing.html)

If you have any questions, want to chat about the collection's capabilities and usage, need help using the collection, or just want to stay updated, join us at our [Discussions](https://github.com/cloudera-labs/cloudera.cloud/discussions).

## Quickstart

See the [API documentation](https://cloudera-labs.github.io/cloudera.cloud/) for details for each plugin and role within the collection.

1. [Install the collection](#installation)
2. [Install the requirements](#requirements)
3. [Use the collection](#using-the-collection)

## Roadmap

If you want to see what we are working on or have pending, check out:

*  the [Milestones](https://github.com/cloudera-labs/cloudera.cloud/milestones) and [active issues](https://github.com/cloudera-labs/cloudera.cloud/issues?q=is%3Aissue+is%3Aopen+milestone%3A*) to see our current activity,
* the [issue backlog](https://github.com/cloudera-labs/cloudera.cloud/issues?q=is%3Aopen+is%3Aissue+no%3Amilestone) to see what work is pending or under consideration, and
* read up on the [Ideas](https://github.com/cloudera-labs/cloudera.cloud/discussions/categories/ideas) we have in mind.

Are we missing something? Let us know by [creating a new issue](https://github.com/cloudera-labs/cloudera.cloud/issues/new) or [posting a new idea](https://github.com/cloudera-labs/cloudera.cloud/discussions/new?category=ideas)!

## Contribute

For more information on how to get involved with the `cloudera.cloud` Ansible collection, head over to [CONTRIBUTING.md](CONTRIBUTING.md).

## Installation

To install the `cloudera.cloud` collection, you have several options.

The preferred method is to install via Ansible Galaxy; in your `requirements.yml` file, add the following:

```yaml
collections:
  - name: cloudera.cloud
```

If you want to install from GitHub, add to your `requirements.yml` file the following:

```yaml
collections:
  - name: https://github.com/cloudera-labs/cloudera.cloud.git
    type: git
    version: main
```

And then run in your project:

```bash
ansible-galaxy collection install -r requirements.yml
```

You can also install the collection directly:

```bash
# From Ansible Galaxy
ansible-galaxy collection install cloudera.cloud
```
> **Note:** We are actively working to remove the dependency on `cdpy` in upcoming releases. Please stay tuned to our changelog for updates.

```bash
# From GitHub
ansible-galaxy collection install git+https://github.com/cloudera-labs/cloudera.cloud.git@main
```

`ansible-builder` can discover and install all Python dependencies - current collection and dependencies - if you wish to use that application to construct your environment. Otherwise, you will need to read each collection and role dependency and follow its installation instructions.

See the [Collection Metadata](https://ansible.readthedocs.io/projects/builder/en/latest/collection_metadata/) section for further details on how to install (and manage) collection dependencies.

You may wish to use a _virtual environment_ to manage the Python dependencies.

## Using the Collection

Once installed, reference the collection in your playbooks and roles.

For example, here we use the
[`cloudera.cloud.env_info` module](https://cloudera-labs.github.io/cloudera.cloud/env_info_module.html) to list all available CDP environments:

```yaml
- hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - name: List all CDP environments
      cloudera.cloud.env_info:
      register: output

    - name: Display the resulting JSON
      ansible.builtin.debug:
        var: output
```
> [!IMPORTANT]
> The collection expects standard Cloudera Platform authentication configurations, e.g. `CDP_PROFILE`, as described by the *Configuring* section of [CDP CLI/SDK](https://github.com/cloudera/cdpcli#configuring).

## Building the API Documentation

To create a local copy of the API documentation, first make sure the collection is in your `ANSIBLE_COLLECTIONS_PATH`.

```bash
hatch run docs:build
```

Your local documentation will be found at `docsbuild/build/html`.

You can also lint the documentation with the following command:

```bash
hatch run docs:lint
```

## Preparing a New Version

To prepare a version release, first set the following variables for `antsichaut`:

```bash
export GITHUB_TOKEN=some_gh_token_value # Read-only scope
```

Update the collection version using [`hatch version`](https://hatch.pypa.io/latest/version/). For example, to increment to the next _minor_ release:

```bash
hatch version minor
```

Then update the changelog to query the pull requests since the last release.

```bash
hatch run docs:changelog
```

You can then examine (and update if needed) the resulting `changelog.yaml` and `CHANGELOG.rst` files before committing to the release branch.

## License and Copyright

Copyright 2026, Cloudera, Inc.

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
