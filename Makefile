VERSION := 2023.10.1

# all runs help
all : help

# help lists out targets
help :
	$(info $(NULL))
	$(info ** Available Targets **)
	$(info $(NULL))
	$(info $(NULL)	build        - builds a python egg for installation)
	$(info $(NULL)	clean        - removes build directories)
	$(info $(NULL)	depsinstall  - installs dependencies via pip)
	$(info $(NULL)	depsupdate   - upgrades dependencies via pip)
	$(info $(NULL)	help         - prints this message)
	$(info $(NULL)	install      - installs the project onto the system)
	$(info $(NULL)	lint         - runs linting for the project)
	$(info $(NULL)	test         - runs tests for the project)
	$(info $(NULL)	testcoverage - runs test coverage reports for the project)
	$(info $(NULL)	versionget   - returns the current project version)
	$(info $(NULL)	versionset   - updates the project version in all version files)
	$(info $(NULL))
	@:

build:
	python3 -m build --wheel --no-isolation

clean:
	rm -rf build dist eljef_media.egg-info \
		eljef/__pycache__ eljef/media/__pycache__ \
		eljef/media/cli/__pycache__ eljef/media/lib/__pycache__ \
		tests/__pycache__ tests/_trial_temp \
		.pytest_cache .coverage

depsinstall:
	pip install -r requirements.txt

depsupdate:
	pip install --upgrade -r requirements.txt

install:
	python3 -m installer dist/*.whl

lint:
	flake8 eljef/media
	pylint eljef/media

test:
	pytest

testcoverage:
	pytest --cov=eljef/ tests/

versionget:
	@echo $(VERSION)

versionset:
	@$(eval OLDVERSION=$(shell cat setup.py | awk -F"[=,]" '/version=/{gsub("\047", ""); print $$2}'))
	@sed -i -e "s/$(OLDVERSION)/$(VERSION)/" eljef/media/__version__.py
	@sed -i -e "s/version='$(OLDVERSION)'/version='$(VERSION)'/" setup.py
