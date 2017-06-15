ENV_DIR := $(shell pwd)/_env
PYTHON_BIN := $(shell which python)

.DEFAULT_GOAL = all

.PHONY: all
all: help

.PHONY: help
help:
	@cat README.md

.PHONY: test
test: setup.py env
	PYTHONPATH=src bash -c "${ENV_DIR}/bin/python test/run_tests.py ${JUSTTEST}"

.PHONY: coverage
coverage: $(ENV_DIR)/bin/coverage setup.py env
	rm -rf htmlcov/
	$(ENV_DIR)/bin/coverage erase
	PYTHONPATH=src bash -c "${ENV_DIR}/bin/python ${ENV_DIR}/bin/coverage run --source src test/run_tests.py"
	bash -c "${ENV_DIR}/bin/python ${ENV_DIR}/bin/coverage report -m --fail-under=100 --omit=*main.py,*sender.py"
	$(ENV_DIR)/bin/coverage html

verify:
	flake8 --select=E10,E11,E9,F src test

style:
	flake8 --select=E,W,C,N --max-line-length=100 src test

explain-style:
	flake8 --select=E,W,C,N --show-pep8 --first --max-line-length=100 src test

.PHONY: env
env: $(ENV_DIR)/.eggs_installed

$(ENV_DIR)/bin/python:
	virtualenv --python=$(PYTHON_BIN) $(ENV_DIR)
	$(ENV_DIR)/bin/pip install --upgrade "setuptools>0.7"

$(ENV_DIR)/bin/coverage: $(ENV_DIR)/bin/python
	$(ENV_DIR)/bin/pip install coverage

.PHONY: build_sasclient_egg
build_sasclient_egg: $(ENV_DIR)/bin/python setup.py
	$(ENV_DIR)/bin/python setup.py bdist_egg -d $(EGG_DIR)

$(ENV_DIR)/.eggs_installed: $(ENV_DIR)/bin/python setup.py $(shell find src -type f -not -name "*.pyc")
	$(ENV_DIR)/bin/python setup.py bdist_egg -d .eggs

	# Download the egg files they depend upon
	${ENV_DIR}/bin/easy_install -zmaxd .eggs/ .eggs/*.egg

	# Install the downloaded egg files
	${ENV_DIR}/bin/easy_install --allow-hosts=None -f .eggs/ .eggs/*.egg

	# Touch the sentinel file
	touch $@

.PHONY: clean
clean: envclean pyclean

.PHONY: pyclean
pyclean:
	find . -name \*.pyc -exec rm -f {} \;
	rm -rf *.egg-info dist
	rm -f .coverage
	rm -rf htmlcov/

.PHONY: envclean
envclean:
	rm -rf bin eggs develop-eggs parts .installed.cfg bootstrap.py .downloads .buildout_downloads
	rm -rf distribute-*.tar.gz
	rm -rf $(ENV_DIR)
