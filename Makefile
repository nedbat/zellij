install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest

coverage:
	coverage run --branch --source=zellij,tests -m py.test
	coverage report -m

htmlcov: coverage
	coverage html

clean:
	-rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ */*/*/*/__pycache__ */*/*/*/*/__pycache__
	-rm -f .coverage

sterile: clean
	-rm -rf .cache .hypothesis *.egg-info

cloc:
	cloc --vcs=git .
