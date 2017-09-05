install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest

coverage:
	-coverage run --branch --source=zellij,tests -m py.test
	coverage report -m

htmlcov: coverage
	coverage html

clean:
	-rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ */*/*/*/__pycache__ */*/*/*/*/__pycache__
	-rm -f .coverage
	-rm -rf htmlcov

sterile: clean
	-rm -rf .cache .hypothesis *.egg-info

cloc:
	cloc --vcs=git .

lint:
	pylint bin tests zellij/ *.py

samples:
	zellij straps cards --tiles=6 --strap-width=18 --rotate=45 --background=salmon --size=910x580 --debug=world --output=card_straps.png
	python bin/talk_pictures.py
	zellij straps threestars --tiles=2 --debug=strapify
	zellij candystripe breath --tiles=6
