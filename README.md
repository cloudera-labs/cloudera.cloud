# cloudera.cloud - Cloudera Data Platform (CDP) for Public Cloud

[![API documentation](https://github.com/cloudera-labs/cloudera.cloud/actions/workflows/publish_docs.yml/badge.svg?branch=main&event=push)](https://github.com/cloudera-labs/cloudera.cloud/actions/workflows/publish_docs.yml)

## Quickstart

1. [Install the collection](#installation)
2. [Install the requirements](#requirements)
3. [Use the collection](#using-the-collection)

## API

See the [API documentation](https://cloudera-labs.github.io/cloudera.cloud/) for details for each plugin and role within the collection. 

## Installation

To install the `cloudera.cloud` collection, you have several options. Please
note that to date, we have not yet published this collection to the public Ansible
Galaxy server, so you cannot install it via direct namespace, rather you must
specify by Git project and (optionally) branch.

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

`cloudera.cloud` expects `ansible-core>=2.12`.

The collection also requires the following Python libraries install to operate 
its modules:

  * [`cdpy`](https://github.com/cloudera-labs/cdpy)

`ansible-galaxy` should install these dependencies automatically; you may wish to use a _virtual environment_.

## Using the Collection

Once installed, reference the collection in your playbooks and roles.

For example, here we use the
[cloudera.cloud.env_info module](https://cloudera-labs.github.io/cloudera.cloud/env_info_module.html) to list all available CDP environments:

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

## Contributing

Please create a feature branch from the `devel` branch and submit a PR against the same while referencing an issue.

Note that we require signed commits inline with [Developer Certificate of Origin](https://developercertificate.org/) best-practices for open source collaboration.

A signed commit is a simple one-liner at the end of your commit message that states that you wrote the patch or otherwise have the right to pass the change into open source.  Signing your commits means you agree to:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
660 York Street, Suite 102,
San Francisco, CA 94110 USA

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

(See [developercertificate.org](https://developercertificate.org/))

To agree, make sure to add line at the end of every git commit message, like this:

```
Signed-off-by: John Doe <jdoe@example.com>
```

TIP! Add the sign-off automatically when creating the commit via the `-s` flag, e.g. `git commit -s`.

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
