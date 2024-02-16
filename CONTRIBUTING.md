# Contributing to portable-app-framework

This document is a set of guidelines and resources for contributing to the portable-app-framework effort.
Improvements and changes to this document are always welcome
via [Pull Request](https://github.com/BrickSchema/portable-app-framework/pulls)



## Development
* https://towardsdatascience.com/how-to-publish-a-python-package-to-pypi-7be9dd5d6dcd
* https://holypython.com/python-packaging-local-installation-tests-before-uploading/

```bash
python3 -m build --wheel # build the package
pip install . # install the package
python3 -m pytest # test the package

python setup.py check
python setup.py sdist bdist_wheel
pip install .
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload --repository pypi dist/*
```


### Commit style

* conventional style commit messages
* create changelog through this tool https://github.com/KeNaCo/auto-changelog

### Documentation 

```
jupyter-book build docs/

```

Copy main readme to docs folder as intro.md. In this way we will always have the intro updated.

```bash
cp README.md docs/intro.md 
```