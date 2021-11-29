# Building Site Documentation

The collection's documentation can be easily generated via manual and automated processes. We use the Sphinx document
engine and thus the site content is written in reST.

# Requirements

You will need to install the following Python libraries (note the Ansible 2.10 requirement!):

- ansible-base >== 2.10.0
- Sphinx >== 3.2.1
- sphinx-rtd-theme
- ansible-doc-extractor

To install the `ansible-doc-extractor`, grab from the forked repository's `native_2_10` branch on GitHub, which has an 
updated template and Ansible 2.10 support.

```bash
pip install git+https://github.com/wmudge/ansible-doc-extractor.git@native_2_10
```

# Preparing a Release

To release a new version of the collection, first update the following files:

* `galaxy.yml` - version number
* `site/conf.py` - version number
* `plugins/README.md` - modules and module links
* `docs/index.rst` - modules and reST links 

Then build the module documentation and correct any errors. Once the reST `docsrc` files are generating correctly, you
can build the documentation.

# Building Module Documentation

The `ansible-doc-extractor` is a Python CLI application that reads an Ansible module source file, extracts the embedded
documentation, and injects the documentation into a Jinja2 file that produces a reST document. The target should be the
top-level `docsrc` directory.

Run the following for each module and at each module documentation change:

```bash
ansible-doc-extractor ../docsrc ./plugins/modules/the_module_in_question.py 
```

Or you can run the bash script, `generate_rst.sh`, which will file glob the `modules/` directory and execute the above.

For new modules, you will also want to edit the `docsrc/index.rst` file and add the module to the `toctree::` 
directive.

NOTE: You must declare the `ANSIBLE_COLLECTIONS_PATH` so the document fragments, etc. can be found by Ansible.

# Building the Site Documentation Locally

The Sphinx configuration targets the `docsrc` directory and outputs the constructed pages and supporting assets
to the `_build` directory.

To run the build, simply run `make clean; make html` from within the `site` directory.

# Building the Site Documentation for GitHub

Run `make clean; make github` from within the `site` directory. This will build the site documentation locally and then
copy it to the `docs` directory.  Just make sure the project is set to publish from the `docs` directory automatically.

