# Portable Framework for Building Applications - PFB-Toolkit

[![Powered by NumFOCUS](https://img.shields.io/badge/powered%20by-BAEDALAB-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://numfocus.org) [![License - BSD 3-Clause](https://img.shields.io/pypi/l/afdd.svg)](https://github.com/RobertoChiosa/afdd/blob/main/LICENSE)

## What is it?

**portable-app-framework** is a Python package that provides a toolkit to create portable applications.

## Table of Contents

- [Main Features](#main-features)
    - [Command Line Interface (CLI)](#command-line-interface-cli)
    - [Application class](#application-class)
- [Installation](#installation)
    - [From source](#from-source)
    - [From test PyPI](#from-test-pypi)
    - [From PyPI](#from-pypi)
- [Dependencies](#dependencies)
- [Background](#background)
- [Contributing](#contributing)
- [License](#license)

## Main Features

Here are just a few of the things that `portable-app-framework` does.

### Command Line Interface (CLI)

You can use the CLI to to create, manage and update applications

```
> portable-app-framework -h

usage: portable-app-framework [-h] {new,update} ...

Utils CLI for the afdd framework.

positional arguments:
  {new,update}
    new         Create a new application folder from template.
    update      Update README of an application.

options:
  -h, --help    show this help message and exit

```

### Application class

A python class that helps to create a portable application. Once you created a new application in your project you can
set up and run an application with the following lines of code

```python
import pandas as pd
import brickschema
from portable_app_framework import Application

app = Application(
    metadata=brickschema.Graph(),
    app_name='app_name'
)
qualify_result = app.qualify()  # True/False
fetch_result = app.fetch()  # Dict of mapped variables
df = pd.DataFrame()  # get df according to your logic 
df_clean = app.clean(df)
final_result = app.analyze(df_clean)
```

## Installation

The source code is currently hosted on GitHub at
https://github.com/RobertoChiosa/portable-app-framework and the list of changes for each release can be found in the
[CHANGELOG](https://github.com/RobertoChiosa/portable-app-framework/blob/main/CHANGELOG.md).

The `portable-app-framework` package requires Python >= 3.9.

You can install the package in different ways depending on the level of usage you want to have.

- [x] From source
- [x] From test PyPI
- [ ] From PyPI (not yet released)

### From source

You can install the package from source by cloning the repository and running the following command:

```sh
git clone https://github.com/RobertoChiosa/portable-app-framework.git
cd portable-app-framework
pip install .
```

### From test PyPI

You can install the latest test version from test PyPI with the following command:

```sh
pip install -i https://test.pypi.org/simple/ PFB-Toolkit==0.1.3
```

### From PyPI

You can install the stable version from PyPI with the following command:

```sh
pip install portable-app-framework
```

## Dependencies

The main dependencies are reported in the requirements.txt and in the setup.py file.
See
the [full installation instructions](https://portable-app-framework.pydata.org/portable-app-framework-docs/stable/install.html#dependencies)
for minimum supported versions of required, recommended and optional dependencies.

## Contributing

[//]: # ([![Open Source Helpers]&#40;https://www.codetriage.com/RobertoChiosa/afdd/badges/users.svg&#41;]&#40;https://www.codetriage.com/RobertoChiosa/afdd&#41;)

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

A detailed overview on how to contribute can be found in
the [contributing guide](https://github.com/RobertoChiosa/portable-app-framework/blob/main/CONTRIBUTING.md).

Most development discussions take place on GitHub in this repo, via
the [GitHub issue tracker](https://github.com/RobertoChiosa/portable-app-framework/issues).

If you are simply looking to start working with the `portable_app_framework` codebase, navigate to
the [GitHub "issues" tab](https://github.com/RobertoChiosa/portable-app-framework/issues) and start looking through
interesting issues.

Or maybe through using `portable_app_framework` you have an idea of your own or are looking for something in the
documentation and
thinking ‘this can be improved’...you can do something about it!

As contributors and maintainers to this project, you are expected to abide
by [Contributor Code of Conduct](https://github.com/RobertoChiosa/portable-app-framework/blob/main/CODE_OF_CONDUCT.md).

## License

The present repository has been released under [MIT LICENSE](LICENSE)

## Cite

Work on ``portable-app-framework`` started in 2021 as an internal project at BAEDA Lab to deploy energy management and
information systems application in a most reliable way instead of solving implementation issues from scratch every time.
We found that the framework enabled faster deployment of such solutions thanks to the builtin methods that allowed the
analyst to skip ripetitive data integration tasks. Moreover allowed non analyst expert of metadata schema to exploit the
power of such tools. So we decided to create this package to share our experience with the scientific community and not
only.

To cite the package in publications use:

```bibtex
@software{portable-app-framework,
    author = {Roberto Chiosa},
    title = {Portable Framework for Building Applications - PFB-Toolkit},
    url = {}
}
```

