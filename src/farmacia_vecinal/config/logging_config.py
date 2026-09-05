"""Configuracion centralizada del registro de eventos de la aplicacion."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_DIRECTORY = Path(__file__).resolve().parents[3] / "database" / "logs"
DEFAULT_LOG_FILENAME = "farmacia.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
MAX_LOG_BYTES = 1_048_576
BACKUP_COUNT = 3


def configure_logging(log_directory: Path | str = DEFAULT_LOG_DIRECTORY) -> None:
    """Configura consola y archivo rotativo para toda la aplicacion."""
    root_logger = logging.getLogger()
    if getattr(root_logger, "_farmacia_configured", False):
        return

    resolved_directory = Path(log_directory)
    resolved_directory.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        resolved_directory / DEFAULT_LOG_FILENAME,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger._farmacia_configured = True
    root_logger.info("Logging configurado; archivo: %s", file_handler.baseFilename)
