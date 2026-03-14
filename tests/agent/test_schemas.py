import pytest

from pydantic import ValidationError

from stock_analysis_mcp.agent.plot_agent import PlotDataOutput


def test_plot_data_output_valid() -> None:
    data = {
        "x_values": ["2023-01-01", "2023-01-02"],
        "open": [100.0, 101.0],
        "high": [105.0, 106.0],
        "low": [95.0, 96.0],
        "close": [102.0, 103.0],
        "title": "Test Chart",
        "xlabel": "Date",
        "ylabel": "Price",
    }
    output = PlotDataOutput(**data)  # type: ignore
    assert output.x_values == data["x_values"]
    assert output.open == data["open"]


def test_plot_data_output_missing_required() -> None:
    data = {
        "x_values": ["2023-01-01"],
        "open": [100.0],
        # Missing high, low, close
    }
    with pytest.raises(ValidationError):
        # We use type: ignore because we are intentionally passing incomplete data
        # to test Pydantic's validation error.
        PlotDataOutput(**data)  # type: ignore


def test_plot_data_output_defaults() -> None:
    data = {"x_values": ["2023-01-01"], "open": [100.0], "high": [100.0], "low": [100.0], "close": [100.0]}
    output = PlotDataOutput(**data)  # type: ignore
    assert output.title == "Candlestick Chart"
    assert output.xlabel == "Date"
    assert output.ylabel == "Price"
