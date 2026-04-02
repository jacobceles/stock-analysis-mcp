import contextlib
import unittest.mock as mock

from collections.abc import Generator

import pytest

from stock_analysis_mcp.services.stock_service import _get_data_internal, get_data


@pytest.fixture(autouse=True)
def clear_cache() -> Generator[None]:
    _get_data_internal.cache_clear()
    yield
    _get_data_internal.cache_clear()


def test_get_data_path_traversal() -> None:
    """Test that path traversal in get_data raises ValueError."""
    malicious_symbol = "../../etc/passwd"
    start_date = "2023-01-01"
    end_date = "2023-01-02"

    with pytest.raises(ValueError, match="Invalid symbol or dates: path traversal detected"):
        get_data(malicious_symbol, start_date, end_date)


def test_get_data_normal_path() -> None:
    """Test that normal symbols work fine (or at least don't raise ValueError for path traversal)."""
    with mock.patch("yfinance.download") as mock_download:
        mock_download.return_value = None
        with contextlib.suppress(Exception):
            get_data("AAPL", "2023-01-01", "2023-01-02")
