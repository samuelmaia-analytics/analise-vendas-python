.PHONY: setup lint type linkcheck test test-cov quality run precommit release-check release-bump-patch changelog-check run-pipeline build-artifacts data-dictionary docker-build docker-run-pipeline docker-run-app

setup:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check .

type:
	mypy src

linkcheck:
	python scripts/check_markdown_links.py

release-check:
	python scripts/check_version_sync.py

changelog-check:
	python scripts/check_changelog.py

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80

quality: lint type linkcheck release-check changelog-check test

run:
	streamlit run app.py

run-cli:
	sales-analytics growth --period M

build-artifacts:
	sales-analytics build-artifacts

run-pipeline:
	sales-analytics run-pipeline

data-dictionary:
	sales-analytics generate-data-dictionary

docker-build:
	docker build -t sales-analytics-portfolio .

docker-smoke-cli:
	docker run --rm sales-analytics-portfolio sales-analytics summary

docker-run-pipeline:
	docker run --rm -v ${CURDIR}/reports:/app/reports -v ${CURDIR}/data:/app/data sales-analytics-portfolio

docker-run-app:
	docker run --rm -p 8501:8501 -v ${CURDIR}/reports:/app/reports -v ${CURDIR}/data:/app/data sales-analytics-portfolio streamlit run app.py --server.address 0.0.0.0

release-bump-patch:
	python scripts/bump_version.py --part patch

precommit:
	pre-commit run --all-files
