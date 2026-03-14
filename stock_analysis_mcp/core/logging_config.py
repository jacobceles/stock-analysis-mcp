import logging
import os
import sys

from colorlog import ColoredFormatter
from pythonjsonlogger import jsonlogger


def setup_logging() -> logging.Logger:
    """Configure logging: JSON by default, colorized when LOG_FORMAT=color."""
    # Default to JSON; use colorized when LOG_FORMAT=color
    use_json = os.getenv("LOG_FORMAT", "json").lower() != "color"

    if use_json:
        # Production/K8s: JSON format
        formatter: logging.Formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
            timestamp=True,
        )
    else:
        # Local dev: Colored format (auto-disables colors when redirected)
        formatter = ColoredFormatter(
            "%(log_color)s[%(asctime)s] [%(levelname)s]%(reset)s %(name_log_color)s%(name)s:%(reset)s %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bold",
            },
            secondary_log_colors={
                "name": {
                    "DEBUG": "blue",
                    "INFO": "blue",
                    "WARNING": "blue",
                    "ERROR": "blue",
                    "CRITICAL": "blue",
                }
            },
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    return root_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
