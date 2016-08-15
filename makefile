.PHONY : test

test:
	python -m pytest -sv

coverage:
	py.test --cov=easy_python_requirements --cov-report=term-missing --cov-report=html

cbook_coverage:
	py.test --cov=easy_python_requirements --cov-report=term-missing --cov-report=html
	rm -r ~/Downloads/htmlcov/
	mv htmlcov ~/Downloads/
