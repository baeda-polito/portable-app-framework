VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


.PHONY: clean
clean:
	@echo "Cleaning repository"
	rm -rf build
	rm -rf dist
	rm -rf app
	rm -rf src/*.egg-info
	rm -rf .pytest_cache
	rm -rf test/*.log

.PHONY: test
test:
	@echo "Running tests"
	source ${VENV}/bin/activate && python3 -m pytest

.PHONY: build
build:
	@echo "Building package"
	source ${VENV}/bin/activate && python3 -m build --wheel

#.PHONY: deploy
#deploy:
#	python setup.py check \
#	python setup.py sdist bdist_wheel \
#	pip install . \
#	python3 -m twine upload --repository testpypi dist/* \
#	python3 -m twine upload --repository pypi dist/*

VENV-DOCS = .venv
PYTHON-DOCS = $(VENV-DOCS)/bin/python3
PIP-DOCS = $(VENV-DOCS)/bin/pip

setup-docs: docs/requirements.txt
	@echo "Creating venv in docs"
	python3 -m venv ${VENV-DOCS}
	@echo "Installing requirements for docs"
	${PIP-DOCS} install -r docs/requirements.txt

build-docs:
#	@echo "Copying README to docs"
#	cp README.md docs/intro.md
	@echo "Building docs"
	source ${VENV-DOCS}/bin/activate
	jupyter-book build docs/
