.PHONY: setup lint type linkcheck test test-cov quality run precommit

setup:
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

lint:
	ruff check .

type:
	mypy src

linkcheck:
	python scripts/check_markdown_links.py

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80

quality: lint type linkcheck test

run:
	streamlit run app.py

precommit:
	pre-commit run --all-files
