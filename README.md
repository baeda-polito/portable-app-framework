# `afdd-framework`: automated fault detection and diagnostics toolkit

[![Powered by NumFOCUS](https://img.shields.io/badge/powered%20by-BAEDALAB-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://numfocus.org) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3509134.svg)](https://doi.org/10.5281/zenodo.3509134) [![License - BSD 3-Clause](https://img.shields.io/pypi/l/afdd.svg)](https://github.com/afdd-dev/afdd/blob/main/LICENSE) [![Slack](https://img.shields.io/badge/join_Slack-information-brightgreen.svg?logo=slack)](https://afdd.pydata.org/docs/dev/development/community.html?highlight=slack#community-slack) |

## What is it?

**afdd** is a Python package that provides fast, flexible, and expressive data
structures designed to make working with "relational" or "labeled" data both
easy and intuitive. It aims to be the fundamental high-level building block for
doing practical, **real world** data analysis in Python. Additionally, it has
the broader goal of becoming **the most powerful and flexible open source data
analysis / manipulation tool available in any language**. It is already well on
its way towards this goal.

The official documentation is hosted on [PyData.org](https://afdd.pydata.org/afdd-docs/stable/).

## Table of Contents

- [Main Features](#main-features)

## Main Features

Here are just a few of the things that afdd does well:

- feature 1

## Installation

The source code is currently hosted on GitHub at:
https://github.com/afdd-dev/afdd

The afdd package requires Python >= 3.8. It can be installed with pip:

```sh
# or PyPI
pip install afdd
```

The list of changes to afdd between each release can be found
[here](https://afdd.pydata.org/afdd-docs/stable/whatsnew/index.html). For full
details, see the commit logs at https://github.com/afdd-dev/afdd.

## Dependencies

- [NumPy - Adds support for large, multi-dimensional arrays, matrices and high-level mathematical functions to operate on these arrays](https://www.numpy.org)

See the [full installation instructions](https://afdd.pydata.org/afdd-docs/stable/install.html#dependencies) for
minimum supported versions of required, recommended and optional dependencies.

## License

[BSD 3](LICENSE)

## Background

Work on ``afdd`` started at [AQR](https://www.aqr.com/) (a quantitative hedge fund) in 2008 and
has been under active development since then.

## Getting Help

For usage questions, the best place to go to is [StackOverflow](https://stackoverflow.com/questions/tagged/afdd).
Further, general questions and discussions can also take place on
the [pydata mailing list](https://groups.google.com/forum/?fromgroups#!forum/pydata).

## Discussion and Development

Most development discussions take place on GitHub in this repo, via
the [GitHub issue tracker](https://github.com/afdd-dev/afdd/issues).

Further, the [afdd-dev mailing list](https://mail.python.org/mailman/listinfo/afdd-dev) can also be used for
specialized discussions or design issues, and
a [Slack channel](https://afdd.pydata.org/docs/dev/development/community.html?highlight=slack#community-slack) is
available for quick development related questions.

There are also
frequent [community meetings](https://afdd.pydata.org/docs/dev/development/community.html#community-meeting) for
project maintainers open to the community as well as
monthly [new contributor meetings](https://afdd.pydata.org/docs/dev/development/community.html#new-contributor-meeting)
to help support new contributors.

Additional information on the communication channels can be found on
the [contributor community](https://afdd.pydata.org/docs/development/community.html) page.

## Contributing to afdd

[![Open Source Helpers](https://www.codetriage.com/afdd-dev/afdd/badges/users.svg)](https://www.codetriage.com/afdd-dev/afdd)

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

A detailed overview on how to contribute can be found in the *
*[contributing guide](https://afdd.pydata.org/docs/dev/development/contributing.html)**.

If you are simply looking to start working with the afdd codebase, navigate to
the [GitHub "issues" tab](https://github.com/afdd-dev/afdd/issues) and start looking through interesting issues.
There are a number of issues listed
under [Docs](https://github.com/afdd-dev/afdd/issues?labels=Docs&sort=updated&state=open)
and [good first issue](https://github.com/afdd-dev/afdd/issues?labels=good+first+issue&sort=updated&state=open)
where you could start out.

You can also triage issues which may include reproducing bug reports, or asking for vital information such as version
numbers or reproduction instructions. If you would like to start triaging issues, one easy way to get started is
to [subscribe to afdd on CodeTriage](https://www.codetriage.com/afdd-dev/afdd).

Or maybe through using afdd you have an idea of your own or are looking for something in the documentation and
thinking ‘this can be improved’...you can do something about it!

Feel free to ask questions on the [mailing list](https://groups.google.com/forum/?fromgroups#!forum/pydata) or
on [Slack](https://afdd.pydata.org/docs/dev/development/community.html?highlight=slack#community-slack).

As contributors and maintainers to this project, you are expected to abide by afdd' code of conduct. More information
can be found at: [Contributor Code of Conduct](https://github.com/afdd-dev/.github/blob/master/CODE_OF_CONDUCT.md)

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
