"""Structured application logging."""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure root logger and return the application logger."""
    log_level = (level or settings.log_level).upper()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Quiet noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logging.getLogger("speakflow")


def get_logger(name: str = "speakflow") -> logging.Logger:
    return logging.getLogger(name)
