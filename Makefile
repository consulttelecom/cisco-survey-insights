# You can set these variables from the command line, and also from the environment for the first two.
SPHINXOPTS    ?= -W
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile build test-local-docs show-local-docs

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

build:
	python setup.py sdist bdist_wheel

test-local-docs:
	docker run -it --rm -v `PWD`:/repo containers.cisco.com/aide/sphinx-tools:v1.5.0 validate.sh

show-local-docs:
	docker run -it --rm -p 8000:8000 -v `PWD`:/repo containers.cisco.com/aide/sphinx-tools:v1.5.0 cicd.sh
