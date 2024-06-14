VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

VENV-DOCS = .venv-docs
PYTHON-DOCS = $(VENV-DOCS)/bin/python3
PIP-DOCS = $(VENV-DOCS)/bin/pip


.PHONY: clean
clean:
	@echo "Cleaning repository"
	rm -rf build
	rm -rf dist
	rm -rf app
	rm -rf src/*.egg-info
	rm -rf .pytest_cache

#.PHONY: test
#test:
#	@echo "Running tests"
#	python

#.PHONY: setup
#setup: requirements.txt
#	@echo "Cleaning repository"
# 	python3 -m venv venv
# 	./venv/bin/pip install -r requirements.txt

setup-docs: docs/requirements.txt
	@echo "Creating venv in docs"
	python3 -m venv ${VENV-DOCS}
	@echo "Installing requirements for docs"
	${PIP-DOCS} install -r docs/requirements.txt

build-docs:
#	@echo "Copying README to docs"
#	cp README.md docs/intro.md
	@echo "Building docs"
	source ${VENV-DOCS}/bin/activate && jupyter-book build docs/