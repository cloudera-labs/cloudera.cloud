# Testing

The [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_testing.html#testing-collections) tool can run a number of testing strategies, notably `sanity`, `units`, and `integration` tests.

## Set up ansible-test

To prepare `ansible-test`, you will need to tackle the following steps:

- Install the collection (and its dependencies) and set the `ANSIBLE_COLLECTIONS_PATHS` accordingly.
- Create a virtual environment

  `ansible-test` currently requires Python<=3.10.

  You can "go basic":
  ```bash
  python3.10 -m venv ~/.venv/cloud-test
  ```

  Or use your favorite wrapper
  ```bash
  mkvirtualenv -p py310 cloud-test
  ```
- Install Ansible and testing requirements.

  Typically, this should be the latest stable Ansible.
  ```bash
  pip install 'ansible-core>=2.14,<2.15' mock pytest pytest-xdist pytest-mock pytest-forked
  ```
  If you need to test with <2.14, you will need to adjust the `pip` libraries accordingly.
  ```bash
  pip install 'ansible-core>=2.12,<2.13' mock pytest 'pytest-xdist==2.5.0' pytest-mock pytest-forked
  ```
- Install the collection's Python requirements.
  ```bash
  pip install -r requirements.txt
  ```
  NOTE: if you are also testing changes with `cdpy`, you will want to install that package locally, i.e. `pip install -e <directory to cdpy>`.

## Run the unit tests

Unit tests are implemented in `pytest`.

```bash
ansible-test units --python 3.10
```

## Run the integration tests

The collection integration tests require preexisting infrastructure, e.g. IAM roles.

See the `integration_config.yml.template` for the infrastructure details available and used by the tests. Your infrastructure setup process should produce an `integration_config.yml` file according to these values.

- To see all of the integration tests aka targets:
  ```bash
  ansible-test integration --list-targets
  ```
- To run all of the integration tests:
  ```bash
  ansible-test integration --local
  ```

Once done with the integration tests, you will need to clean up any remaining CDP assets before tearing down the infrastructure (if required by your testing setup).
```bash
ansible-test integration --local --allow-disabled teardown
```
