VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

VENV-DOCS = .venv-docs
PYTHON-DOCS = $(VENV-DOCS)/bin/python3
PIP-DOCS = $(VENV-DOCS)/bin/pip

.PHONY: rm-git-cache
rm-git-cache:
	@echo "Removing git cached files"
	git rm -r --cached .
	git add .

.PHONY: clean
clean:
	@echo "Cleaning repository"
	rm -rf build
	rm -rf dist
	rm -rf app
	rm -rf *.db
	rm -rf src/*.egg-info
	rm -rf .pytest_cache
	rm -rf test/*.log
	rm -rf ${VENV}
	rm -rf ${VENV-DOCS}

.PHONY: setup
setup:
	@if [ ! -d "${VENV}" ]; then \
		echo "Creating venv"; \
		python3 -m venv ${VENV}; \
	fi
	echo "Venv already exists"; \
	source ${VENV}/bin/activate; \
	pip install --upgrade pip; \
	pip install poetry; \
	poetry config virtualenvs.create false; \
	poetry install; \

# https://johnfraney.ca/blog/create-publish-python-package-poetry/
.PHONY: build
build:
	@echo "Building package"
	source ${VENV}/bin/activate && \
	poetry build


.PHONY: test
test:
	@echo "Running tests"
	source ${VENV}/bin/activate && \
 	python3 -m test.test


.PHONY: install
install:
	@echo "Installing package"
	source ${VENV}/bin/activate && \
 	rm -rf poetry.lock && \
 	poetry install



.PHONY: publish
# https://stackoverflow.com/questions/68882603/using-python-poetry-to-publish-to-test-pypi-org
publish:
	@echo "Publishing package"
	source ${VENV}/bin/activate && \
	poetry install && \
	# poetry version patch && \
	poetry publish -r testpypi && \
	poetry publish

#.PHONY: deploy
#deploy:
#	python setup.py check \
#	python setup.py sdist bdist_wheel \
#	pip install . \
#	python3 -m twine upload --repository testpypi dist/* \
#	python3 -m twine upload --repository pypi dist/*

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
