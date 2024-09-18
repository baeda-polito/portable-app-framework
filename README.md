# `portable-app-framework` A framework for Energy Management solutions

[![Powered by NumFOCUS](https://img.shields.io/badge/powered%20by-BAEDALAB-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://numfocus.org) [![License - BSD 3-Clause](https://img.shields.io/pypi/l/afdd.svg)](https://github.com/RobertoChiosa/afdd/blob/main/LICENSE)

**portable-app-framework** is a Python package that provides a toolkit for developing, scaling and maintaining energy
management and information systems (EMIS) applications using an ontology-based approach. Key contributions include an
interoperable layer based on Brick schema, the formalization of application constraints pertaining metadata and data
requirements, and a field demonstration. The framework allows for querying metadata models, fetching data,
preprocessing, and analyzing data, thereby offering a modular and flexible workflow for application development.

## Table of Contents

- [Main Features](#main-features)
    - [Command Line Interface (CLI)](#command-line-interface-cli)
    - [Application class](#application-class)
- [Installation](#installation)
    - [From source](#from-source)
    - [From test PyPI](#from-test-pypi)
    - [From PyPI](#from-pypi)
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
df_preprocess = app.preprocess(df)
final_result = app.analyze(df_preprocess)
```

## Installation

The source code is currently hosted on GitHub at
https://github.com/RobertoChiosa/portable-app-framework and the list of changes for each release can be found in the
[CHANGELOG](https://github.com/RobertoChiosa/portable-app-framework/blob/main/CHANGELOG.md).

The `portable-app-framework` package requires Python >= 3.9. The main dependencies are reported in
the [`requirements.txt`](requirements.txt) and in the [`setup.py`](setup.py) file.

You can install the package in different ways depending on the level of usage you want to have.

- [x] From source
- [x] From PyPI

### From source

You can install the package from source by cloning the repository and running the following command:

```sh
git clone https://github.com/RobertoChiosa/portable-app-framework.git
cd portable-app-framework
pip install .
```

### From PyPI

You can install the stable version from PyPI with the following command:

```sh
pip install pfb-toolkit
```

## Contributing

[//]: # ([![Open Source Helpers]&#40;https://www.codetriage.com/RobertoChiosa/afdd/badges/users.svg&#41;]&#40;https://www.codetriage.com/RobertoChiosa/afdd&#41;)

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

Most development discussions take place on GitHub in this repo, via
the [GitHub issue tracker](https://github.com/RobertoChiosa/portable-app-framework/issues).

If you are simply looking to start working with the `portable_app_framework` codebase, navigate to
the [GitHub "issues" tab](https://github.com/RobertoChiosa/portable-app-framework/issues) and start looking through
interesting issues.

Or maybe through using `portable_app_framework` you have an idea of your own or are looking for something in the
documentation and
thinking ‘this can be improved’...you can do something about it!

## License

The present repository has been released under [MIT LICENSE](LICENSE.md)

## Cite

Work on ``portable-app-framework`` started in 2021 as an internal project at BAEDA Lab to deploy energy management and
information systems application in a most reliable way instead of solving implementation issues from scratch every time.
We found that the framework enabled faster deployment of such solutions thanks to the builtin methods that allowed the
analyst to skip ripetitive data integration tasks. Moreover allowed non analyst expert of metadata schema to exploit the
power of such tools. So we decided to create this package to share our experience with the scientific community and not
only.

To cite the package in publications use:

```bibtex
@article{CHIOSA2024114802,
    title = {A portable application framework for energy management and information systems (EMIS) solutions using Brick semantic schema},
    journal = {Energy and Buildings},
    volume = {323},
    pages = {114802},
    year = {2024},
    issn = {0378-7788},
    doi = {https://doi.org/10.1016/j.enbuild.2024.114802},
    url = {https://www.sciencedirect.com/science/article/pii/S0378778824009186},
    author = {Roberto Chiosa and Marco Savino Piscitelli and Marco Pritoni and Alfonso Capozzoli},
    keywords = {Energy management and information systems, Portable application, Brick metadata schema, Anomaly detection, Machine learning},
    abstract = {This paper introduces a portable framework for developing, scaling and maintaining energy management and information systems (EMIS) applications using an ontology-based approach. Key contributions include an interoperable layer based on Brick schema, the formalization of application constraints pertaining metadata and data requirements, and a field demonstration. The framework allows for querying metadata models, fetching data, preprocessing, and analyzing data, thereby offering a modular and flexible workflow for application development. Its effectiveness is demonstrated through a case study involving the development and implementation of a data-driven anomaly detection tool for the photovoltaic systems installed at the Politecnico di Torino, Italy. During eight months of testing, the framework was used to tackle practical challenges including: (i) developing a machine learning-based anomaly detection pipeline, (ii) replacing data-driven models during operation, (iii) optimizing model deployment and retraining, (iv) handling critical changes in variable naming conventions and sensor availability (v) extending the pipeline from one system to additional ones.}
}
```

