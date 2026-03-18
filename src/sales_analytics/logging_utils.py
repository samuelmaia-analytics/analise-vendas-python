from __future__ import annotations

import logging

from .config import get_runtime_config


class _RuntimeContextFilter(logging.Filter):
    def __init__(self, *, environment: str, pipeline_name: str) -> None:
        super().__init__()
        self._environment = environment
        self._pipeline_name = pipeline_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.environment = self._environment
        record.pipeline_name = self._pipeline_name
        return True


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    runtime = get_runtime_config()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | env=%(environment)s | pipeline=%(pipeline_name)s | %(name)s | %(message)s"
        )
    )
    handler.addFilter(_RuntimeContextFilter(environment=runtime.environment, pipeline_name=runtime.pipeline_name))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, runtime.log_level, logging.INFO))
    logger.propagate = False
    return logger
