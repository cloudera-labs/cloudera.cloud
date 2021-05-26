# cloudera.cloud - Cloudera Data Platform (CDP) for Public and Private Cloud

Readme last updated: 2021-05-25

# Quickstart

1. [Install the collection](#installation)
2. [Install the requirements](#requirements)
3. [Use the collection](#using-the-collection)

# API

See the [API documentation](https://cloudera-labs.github.io/cloudera.cloud/) for details for each module within the collection. 

# Installation

To install the `cloudera.cloud` collection, you have several options. Please
note that to date, we have not yet published this collection to the public 
Galaxy server, so you cannot install it via direct namespace, rather you must
specify a Git project and (optionally) branch.

## Option #1: Install from GitHub

Create or edit the `collections/requirements.yml` file in your project with the
following:

```yaml
collections:
  - name: https://github.com/cloudera-labs/cloudera.cloud.git
    type: git
    version: main
```

And then run in your project:

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

## Option #2: Install the tarball

Periodically, the collection is packaged into a distribution which you can
install directly:

```bash
ansible-galaxy collection install <collection-tarball> -p collections/
```

# Requirements

`cloudera.cloud` expects Ansible Base/Core `2.10.0` or higher.

The collection also requires the following Python libraries install to operate 
its modules:

```pip
cdpy      # Located on Cloudera Labs
```

The [`requirements.txt`](./requirements.txt) file declares these libraries. You
can install them via `pip`:

```bash
pip install -r requirements.txt
```

# Using the Collection

Once installed, reference the collection in your playbooks and roles.

For example, here we use the
[cloudera.cloud.env_info module](./plugins/modules/env_info.py) to list all 
available CDP environments:

```yaml
---

- hosts: localhost
  connection: local
  gather_facts: no

  collections:
    - cloudera.cloud

  tasks:
    - name: List all CDP environments
      env_info:
      register: output

    - name: Display the resulting JSON
      debug:
        var: output
```

> **NOTE:** The CDP modules expect standard CDP authentication configurations,
e.g. `CDP_PROFILE`, as described by the *Configuring* section of 
[CDP CLI/SDK](https://github.com/cloudera/cdpcli#configuring).

## Available Modules

See the [README](./plugins/README.md) in the `plugins` directory.

# Building the Collection

To create a local collection tarball, run:

```bash
ansible-galaxy collection build 
```

For the site documentation, please see the 
[BUILDING DOCS](./site/BUILDING_DOCS.md) instructions.

# Getting Involved

Contribution instructions are coming soon!

# License and Copyright

Copyright 2021, Cloudera, Inc.

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
