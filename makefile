
PIP := pip
PACKAGE := easy_python_requirements
PYTEST_OPTS := -v --cov=$(PACKAGE) --cov-report=term-missing --cov-report=html

.PHONY : test

test:
	$(PIP) install --upgrade pep8 pep257 pylint coverage pytest pytest-cov
	py.test $(PYTEST_OPTS)

coverage:
	py.test --cov=easy_python_requirements --cov-report=term-missing --cov-report=html

cbook_coverage:
	py.test --cov=easy_python_requirements --cov-report=term-missing --cov-report=html
	rm -r ~/Downloads/htmlcov/
	mv htmlcov ~/Downloads/
