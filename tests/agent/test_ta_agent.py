from unittest.mock import MagicMock, patch

import pytest

from google.adk.tools.tool_context import ToolContext

from stock_analysis_mcp.agent.ta_agent import (
    exit_loop,
    get_adx_tool,
    get_aroon_down_tool,
    get_aroon_up_tool,
    get_chaikin_money_flow_tool,
    get_ema_tool,
    get_equity_data,
    get_ichimoku_a_tool,
    get_ichimoku_b_tool,
    get_macd_tool,
    get_on_balance_volume_tool,
    get_psar_down_tool,
    get_psar_up_tool,
    get_reddit_stock_news_tool,
    get_roc_tool,
    get_rsi_tool,
    get_stoch_tool,
    get_stock_metadata_tool,
    get_tsi_tool,
    get_volume_weighted_average_price_tool,
)


def test_exit_loop_with_actions() -> None:
    """Test exit_loop sets actions.escalate to True when actions is present."""
    mock_context = MagicMock(spec=ToolContext)

    result = exit_loop(mock_context)

    assert result == {}
    assert mock_context.actions.escalate is True


def test_exit_loop_missing_actions() -> None:
    """Test exit_loop raises AttributeError when actions is missing."""
    mock_context = MagicMock(spec=ToolContext)
    del mock_context.actions

    with pytest.raises(AttributeError):
        exit_loop(mock_context)


# --- Tool wrapper tests ---


@patch("stock_analysis_mcp.agent.ta_agent.get_equity_metadata", return_value={"symbol": "AAPL"})
def test_get_stock_metadata_tool(mock_fn: MagicMock) -> None:
    result = get_stock_metadata_tool("AAPL")
    mock_fn.assert_called_once_with("AAPL")
    assert result == {"symbol": "AAPL"}


@patch("stock_analysis_mcp.agent.ta_agent.get_data")
def test_get_equity_data_tool(mock_fn: MagicMock) -> None:
    mock_df = MagicMock()
    mock_df.values.tolist.return_value = [[1, 2], [3, 4]]
    mock_fn.return_value = mock_df
    result = get_equity_data("AAPL", "2025-01-01", "2025-03-31")
    mock_fn.assert_called_once_with("AAPL", "2025-01-01", "2025-03-31")
    assert result == [[1, 2], [3, 4]]


@patch("stock_analysis_mcp.agent.ta_agent.get_macd", return_value=[1.0, 2.0])
def test_get_macd_tool(mock_fn: MagicMock) -> None:
    assert get_macd_tool("AAPL", "2025-01-01", "2025-03-31") == [1.0, 2.0]
    mock_fn.assert_called_once_with("AAPL", "2025-01-01", "2025-03-31")


@patch("stock_analysis_mcp.agent.ta_agent.get_rsi", return_value=[50.0])
def test_get_rsi_tool(mock_fn: MagicMock) -> None:
    assert get_rsi_tool("AAPL", "2025-01-01", "2025-03-31") == [50.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_tsi", return_value=[0.5])
def test_get_tsi_tool(mock_fn: MagicMock) -> None:
    assert get_tsi_tool("AAPL", "2025-01-01", "2025-03-31") == [0.5]


@patch("stock_analysis_mcp.agent.ta_agent.get_stoch", return_value=[80.0])
def test_get_stoch_tool(mock_fn: MagicMock) -> None:
    assert get_stoch_tool("AAPL", "2025-01-01", "2025-03-31", 14, 3) == [80.0]
    mock_fn.assert_called_once_with("AAPL", "2025-01-01", "2025-03-31", 14, 3)


@patch("stock_analysis_mcp.agent.ta_agent.get_roc", return_value=[2.0])
def test_get_roc_tool(mock_fn: MagicMock) -> None:
    assert get_roc_tool("AAPL", "2025-01-01", "2025-03-31", 12) == [2.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_ema", return_value=[101.0])
def test_get_ema_tool(mock_fn: MagicMock) -> None:
    assert get_ema_tool("AAPL", "2025-01-01", "2025-03-31", 12) == [101.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_ichimoku_a", return_value=[100.0])
def test_get_ichimoku_a_tool(mock_fn: MagicMock) -> None:
    assert get_ichimoku_a_tool("AAPL", "2025-01-01", "2025-03-31") == [100.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_ichimoku_b", return_value=[99.0])
def test_get_ichimoku_b_tool(mock_fn: MagicMock) -> None:
    assert get_ichimoku_b_tool("AAPL", "2025-01-01", "2025-03-31") == [99.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_adx", return_value=[25.0])
def test_get_adx_tool(mock_fn: MagicMock) -> None:
    assert get_adx_tool("AAPL", "2025-01-01", "2025-03-31") == [25.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_psar_up", return_value=[95.0])
def test_get_psar_up_tool(mock_fn: MagicMock) -> None:
    assert get_psar_up_tool("AAPL", "2025-01-01", "2025-03-31") == [95.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_psar_down", return_value=[105.0])
def test_get_psar_down_tool(mock_fn: MagicMock) -> None:
    assert get_psar_down_tool("AAPL", "2025-01-01", "2025-03-31") == [105.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_aroon_up", return_value=[70.0])
def test_get_aroon_up_tool(mock_fn: MagicMock) -> None:
    assert get_aroon_up_tool("AAPL", "2025-01-01", "2025-03-31") == [70.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_aroon_down", return_value=[30.0])
def test_get_aroon_down_tool(mock_fn: MagicMock) -> None:
    assert get_aroon_down_tool("AAPL", "2025-01-01", "2025-03-31") == [30.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_on_balance_volume", return_value=[1000.0])
def test_get_on_balance_volume_tool(mock_fn: MagicMock) -> None:
    assert get_on_balance_volume_tool("AAPL", "2025-01-01", "2025-03-31") == [1000.0]


@patch("stock_analysis_mcp.agent.ta_agent.get_chaikin_money_flow", return_value=[0.1])
def test_get_chaikin_money_flow_tool(mock_fn: MagicMock) -> None:
    assert get_chaikin_money_flow_tool("AAPL", "2025-01-01", "2025-03-31") == [0.1]


@patch("stock_analysis_mcp.agent.ta_agent.get_volume_weighted_average_price", return_value=[100.5])
def test_get_volume_weighted_average_price_tool(mock_fn: MagicMock) -> None:
    assert get_volume_weighted_average_price_tool("AAPL", "2025-01-01", "2025-03-31") == [100.5]


@patch("stock_analysis_mcp.agent.ta_agent.get_reddit_stock_news", return_value=[{"title": "test"}])
def test_get_reddit_stock_news_tool(mock_fn: MagicMock) -> None:
    assert get_reddit_stock_news_tool("AAPL", "week") == [{"title": "test"}]
    mock_fn.assert_called_once_with("AAPL", "week")
