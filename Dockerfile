FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV APP_ENV=container

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY pyproject.toml README.md README.pt-BR.md requirements.txt requirements-dev.txt VERSION ./
COPY src ./src
COPY app ./app
COPY assets ./assets
COPY data ./data
COPY docs ./docs
COPY scripts ./scripts
COPY app.py ./

RUN pip install --upgrade pip && pip install -e ".[dev]"

USER appuser

EXPOSE 8501

CMD ["sales-analytics", "run-pipeline"]
