# Makefile to simplify some common operations.

# Find our exact Python 3 version. Override with PYTHONBIN variable before
# calling.
PYTHONBIN ?= $(shell python3-config --prefix)/bin/python3

PYVER := $(shell $(PYTHONBIN) -c 'import sys;print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
ABIFLAGS := $(shell $(PYTHONBIN)-config --abiflags)
SUFFIX := $(shell $(PYTHONBIN)-config --extension-suffix)

export PYVER

# Darwin using homebrew does not need sudo, but most other platforms do.
OSNAME = $(shell uname)
ifeq ($(OSNAME), Darwin)
	SUDO = 
else
	SUDO = sudo
endif

GPG = gpg2

.PHONY: info build install clean distclean develop test sdist requirements docs lint bdist sign publish

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  info          Show info about the Python being used."
	@echo "  lint          to lint the source with flake8."
	@echo "  build         to just build the packages."
	@echo "  install       to install from this workspace."
	@echo "  develop       to set up for local development."
	@echo "  test          to run unit tests."
	@echo "  clean         to clean up build artifacts."
	@echo "  distclean     to make source tree pristine."
	@echo "  sdist         to build source distribution."
	@echo "  bdist         to build binary distribution (wheel)."
	@echo "  publish       to push to PyPI."
	@echo "  docs          to build the documention."

info:
	@echo Found Python version: $(PYVER)$(ABIFLAGS)
	@echo Specific Python used: $(PYTHONBIN)
	@echo Python exension suffix: $(SUFFIX)
	@echo sudo: $(SUDO)

lint:
	$(PYTHONBIN) -m flake8 botfly/

build:
	$(PYTHONBIN) setup.py build

install: build
	$(PYTHONBIN) setup.py install --skip-build --optimize

requirements:
	$(SUDO) $(PYTHONBIN) -m pip install -r dev-requirements.txt

develop: requirements
	$(PYTHONBIN) setup.py develop --user

test:
	$(PYTHONBIN) setup.py test

clean:
	$(PYTHONBIN) setup.py clean
	find . -depth -type d -name __pycache__ -exec rm -rf {} \;

distclean: clean
	make -C docs clean
	rm -rf botfly.egg-info
	rm -rf dist
	rm -rf build
	rm -rf .cache
	rm -rf .eggs

sdist: requirements
	$(PYTHONBIN) setup.py sdist

bdist:
	$(PYTHONBIN) setup.py bdist_wheel

sign: bdist sdist
	$(GPG) --detach-sign -a dist/botfly-*.whl
	$(GPG) --detach-sign -a dist/botfly-*.tar.gz

publish: sign
	$(PYTHONBIN) -m twine upload -r pypi dist/*

docs:
	make -C docs html
