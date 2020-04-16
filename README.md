# cloudera.cloud - Cloudera Data Platform (CDP) for Public and Private Cloud

## Quickstart

1. [Install the collection](#installation)
2. [Install the requirements](#required-libraries)
3. [Use the collection](#using-the-collection)

## Installation

To install the `cloudera.cloud` collection, you have several options. Please note that to date, we have not yet
published this collection to the public Galaxy server, so you cannot install it via direct namespace, rather you must
specify a Git project and (optionally) branch.

The collection has two dependencies that should resolve automatically via the `ansible-galaxy` command:
 
- [community.general](https://galaxy.ansible.com/community/general)
- [community.aws](https://galaxy.ansible.com/community/aws)

### Option #1: Install from GitHub

Create or edit the `collections/requirements.yml` file in your project with the following:

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

### Option #2: Install the tarball

Periodically, the collection is packaged into a distribution which you can install directly:

```bash
ansible-galaxy collection install TKTKTK -p collections/
```

## Required Libraries

The collection requires the following Python libraries install to operate its modules:

```pip
cdpy      # Located on Cloudera Labs
boto
botocore
boto3
```

The [`requirements.txt`](./requirements.txt) file declares these libraries. You can install them via `pip`:

```bash
pip install -r requirements.txt
```

## Using the Collection

Once installed, reference the collection in your playbooks and roles.

For example, here we use the [cloudera.cloud.env_info module](./plugins/modules/env_info.py) to list all available CDP
environments:

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

> The CDP modules expect standard CDP authentication configurations, e.g. `CDP_PROFILE`, as described by the 
[CDP CLI/SDK](https://github.com/cloudera/cdpcli).

### Available Modules

See the [README](./plugins/README.md) in the `plugins` directory.

## Building the Collection

To create a local collection tarball, run:

```bash
ansible-galaxy collection build 
```

For the site documentation, please see the [BUILDING DOCS](./site/BUILDING_DOCS.md) instructions.
