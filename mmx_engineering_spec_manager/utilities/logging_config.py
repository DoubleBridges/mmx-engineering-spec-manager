from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from PySide6.QtCore import QStandardPaths


_DEF_LOGGER_NAME = "mmx_esm"


def _app_log_dir() -> Path:
    p = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    p.mkdir(parents=True, exist_ok=True)
    return p


def _default_log_path() -> Path:
    return _app_log_dir() / "app.log"


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a configured logger. Uses a rotating file handler under the app data directory.
    Idempotent: multiple calls will not duplicate handlers.
    """
    logger_name = name or _DEF_LOGGER_NAME
    logger = logging.getLogger(logger_name)
    if getattr(logger, "_mmx_es_logger_configured", False):
        return logger

    logger.setLevel(logging.INFO)

    log_path = _default_log_path()
    handler = RotatingFileHandler(str(log_path), maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fmt = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # Prevent duplicate propagation to root if user adds their own root handlers
    logger.propagate = False
    logger._mmx_es_logger_configured = True  # type: ignore[attr-defined]
    return logger
