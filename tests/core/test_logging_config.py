import logging
import os
import sys
import pytest

from colorlog import ColoredFormatter
from pythonjsonlogger import jsonlogger

from stock_analysis_mcp.core.logging_config import get_logger, setup_logging


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before and after each test."""
    # Store original handlers
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level

    yield

    # Restore original handlers
    root_logger.handlers = original_handlers
    root_logger.setLevel(original_level)


def test_setup_logging_json_default(mocker):
    # Mock environment variable LOG_FORMAT
    mocker.patch.dict(os.environ, clear=True)

    # Mock sys.stdout
    mocker.patch("sys.stdout")

    logger = setup_logging()

    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]

    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, jsonlogger.JsonFormatter)

def test_setup_logging_color_format(mocker):
    # Mock environment variable LOG_FORMAT
    mocker.patch.dict(os.environ, {"LOG_FORMAT": "color"}, clear=True)

    # Mock sys.stdout
    mocker.patch("sys.stdout")

    logger = setup_logging()

    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]

    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, ColoredFormatter)


def test_get_logger():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"

def test_get_logger_no_name():
    logger = get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "root"
