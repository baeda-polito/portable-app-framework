# `portable-app-framework`: automated fault detection and diagnostics toolkit

[![Powered by NumFOCUS](https://img.shields.io/badge/powered%20by-BAEDALAB-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://numfocus.org) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3509134.svg)](https://doi.org/10.5281/zenodo.3509134) [![License - BSD 3-Clause](https://img.shields.io/pypi/l/afdd.svg)](https://github.com/RobertoChiosa/afdd/blob/main/LICENSE) [![Slack](https://img.shields.io/badge/join_Slack-information-brightgreen.svg?logo=slack)](https://afdd.pydata.org/docs/dev/development/community.html?highlight=slack#community-slack) |

## What is it?

**portable-app-framework** is a Python package that provides

The official documentation is hosted
on [PyData.org](https://portable-app-framework.pydata.org/portable-app-framework-docs/stable/).

## Table of Contents

- [Main Features](#main-features)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [License](#license)
- [Background](#background)
- [Getting Help](#getting-help)
- [Discussion and Development](#discussion-and-development)
- [Contributing to `portable-app-framework`](#contributing-to-portable-app-framework)

## Main Features

Here are just a few of the things that portable-app-framework does well:

- cli to create new apps
- application based on brick schema

## Installation

The source code is currently hosted on GitHub at:
https://github.com/RobertoChiosa/portable-app-framework

The portable-app-framework package requires Python >= 3.8. It can be installed with pip:

```sh
# or PyPI
pip install portable-app-framework
```

The list of changes to portable-app-framework between each release can be found
[here](https://github.com/RobertoChiosa/portable-app-framework/CHANGELOG.md).

## Dependencies

- [NumPy - Adds support for large, multi-dimensional arrays, matrices and high-level mathematical functions to operate on these arrays](https://www.numpy.org)

See
the [full installation instructions](https://portable-app-framework.pydata.org/portable-app-framework-docs/stable/install.html#dependencies)
for
minimum supported versions of required, recommended and optional dependencies.

## License

The present repository has been released under [MIT LICENSE](LICENSE)

## Background

Work on ``portable-app-framework`` started at

## Getting Help

For usage questions, the best place to go

## Discussion and Development

Most development discussions take place on GitHub in this repo, via
the [GitHub issue tracker](https://github.com/RobertoChiosa/portable-app-framework/issues).

## Contributing to `portable-app-framework`

[//]: # ([![Open Source Helpers]&#40;https://www.codetriage.com/RobertoChiosa/afdd/badges/users.svg&#41;]&#40;https://www.codetriage.com/RobertoChiosa/afdd&#41;)

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

A detailed overview on how to contribute can be found in
the [contributing guide](https://github.com/RobertoChiosa/portable-app-framework/blob/main/CONTRIBUTING.md).

If you are simply looking to start working with the afdd codebase, navigate to
the [GitHub "issues" tab](https://github.com/RobertoChiosa/portable-app-framework/issues) and start looking through
interesting
issues.
There are a number of issues listed
under [Docs](https://github.com/RobertoChiosa/portable-app-framework/issues?labels=Docs&sort=updated&state=open)
and [good first issue](https://github.com/RobertoChiosa/portable-app-framework/issues?labels=good+first+issue&sort=updated&state=open)
where you could start out.

Or maybe through using afdd you have an idea of your own or are looking for something in the documentation and
thinking ‘this can be improved’...you can do something about it!

As contributors and maintainers to this project, you are expected to abide by afdd code of conduct. More information
can be found
at: [Contributor Code of Conduct](https://github.com/RobertoChiosa/portable-app-framework/blob/main/CODE_OF_CONDUCT.md)

<hr>

[Go to Top](#table-of-contents)

* https://towardsdatascience.com/how-to-publish-a-python-package-to-pypi-7be9dd5d6dcd
* https://holypython.com/python-packaging-local-installation-tests-before-uploading/

```bash
python setup.py sdist bdist_wheel
pip install .
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload --repository pypi dist/*
```
