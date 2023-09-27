# cloudera.cloud - Cloudera Data Platform (CDP) for Public Cloud

[![API documentation](https://github.com/cloudera-labs/cloudera.cloud/actions/workflows/publish_docs.yml/badge.svg?branch=main&event=push)](https://github.com/cloudera-labs/cloudera.cloud/actions/workflows/publish_docs.yml)

`cloudera.cloud` is an Ansible collection that lets you manage your **[Cloudera Data Platform (CDP)](https://www.cloudera.com/products/cloudera-data-platform.html) Public Cloud** resources. With this collection, you can:

* Create and manage [Datalakes](https://www.cloudera.com/products/open-data-lakehouse.html) and Environments.
* Manage Users and Groups.
* Create and manage [Data Hubs](https://www.cloudera.com/products/data-hub.html) and Data Services, such as:
  * [Cloudera Data Flow (CDF)](https://www.cloudera.com/products/dataflow.html)
  * [Cloudera Data Engineering (CDE)](https://www.cloudera.com/products/data-engineering.html)
  * [Cloudera Data Warehouse (CDW)](https://www.cloudera.com/products/data-warehouse.html)
  * [Cloudera Machine Learning (CML)](https://www.cloudera.com/products/machine-learning.html)
  * [Cloudera Operational Database](https://www.cloudera.com/products/operational-db.html)
  * [Cloudera Stream Processing (CSP)](https://www.cloudera.com/products/stream-processing.html)

If you have any questions, want to chat about the collection's capabilities and usage, need help using the collection, or just want to stay updated, join us at our [Discussions](https://github.com/cloudera-labs/cloudera.cloud/discussions).

## Quickstart

1. [Install the collection](#installation)
2. [Install the requirements](#requirements)
3. [Use the collection](#using-the-collection)

## API

See the [API documentation](https://cloudera-labs.github.io/cloudera.cloud/) for details for each plugin and role within the collection. 

## Roadmap

If you want to see what we are working on or have pending, check out:

*  the [Milestones](https://github.com/cloudera-labs/cloudera.cloud/milestones) and [active issues](https://github.com/cloudera-labs/cloudera.cloud/issues?q=is%3Aissue+is%3Aopen+milestone%3A*) to see our current activity,
* the [issue backlog](https://github.com/cloudera-labs/cloudera.cloud/issues?q=is%3Aopen+is%3Aissue+no%3Amilestone) to see what work is pending or under consideration, and
* read up on the [Ideas](https://github.com/cloudera-labs/cloudera.cloud/discussions/categories/ideas) we have in mind.

Are we missing something? Let us know by [creating a new issue](https://github.com/cloudera-labs/cloudera.cloud/issues/new) or [posting a new idea](https://github.com/cloudera-labs/cloudera.cloud/discussions/new?category=ideas)!

## Contribute

For more information on how to get involved with the `cloudera.cloud` Ansible collection, head over to [CONTRIBUTING.md](CONTRIBUTING.md).

## Installation

To install the `cloudera.cloud` collection, you have several options. Please note that we have not yet published this collection to the public Ansible Galaxy server, so you cannot install it via direct namespace, rather you must specify by Git project and (optionally) branch.

### Option #1: Install from GitHub

Create or edit your `requirements.yml` file in your project with the
following:

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
ansible-galaxy collection install git+https://github.com/cloudera-labs/cloudera.cloud.git@main
```

### Option #2: Install the tarball

Periodically, the collection is packaged into a distribution which you can
install directly:

```bash
ansible-galaxy collection install <collection-tarball>
```

See [Building the Collection](#building-the-collection) for details on creating a local tarball.

## Requirements

`cloudera.cloud` expects `ansible-core>=2.10`.

The collection also requires the following Python libraries install to operate 
its modules:

  * [`cdpy`](https://github.com/cloudera-labs/cdpy)

`ansible-galaxy` should install these dependencies automatically; you may wish to use a _virtual environment_. `ansible-builder` will install the Python dependencies if you wish to use that application to construct your environment.

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

> **NOTE:** The CDP modules expect standard CDP authentication configurations,
e.g. `CDP_PROFILE`, as described by the *Configuring* section of 
[CDP CLI/SDK](https://github.com/cloudera/cdpcli#configuring).

## Building the Collection

To create a local collection tarball, run:

```bash
ansible-galaxy collection build 
```

## Building the API Documentation

To create a local copy of the API documentation, first make sure the collection is in your `ANSIBLE_COLLECTIONS_PATHS`. Then run the following:

```bash
# change into the /docsbuild directory
cd docsbuild

# install the build requirements (antsibull-docs); you may want to set up a
# dedicated virtual environment
pip install ansible-core https://github.com/cloudera-labs/antsibull-docs/archive/cldr-docsite.tar.gz

# Install the collection's build dependencies
pip install requirements.txt

# Then run the build script
./build.sh
```

Your local documentation will be found at `docsbuild/build/html`.

## License and Copyright

Copyright 2023, Cloudera, Inc.

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
