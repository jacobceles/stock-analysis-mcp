import ast
import json

from unittest.mock import MagicMock

import pytest

from pytest_mock import MockerFixture

from stock_analysis_mcp.api.mcp_server import (
    _safe_eval,
    _safe_pow,
    get_chaikin_money_flow_tool,
    get_ema_tool,
    get_equity_data,
    get_ichimoku_a_tool,
    get_ichimoku_b_tool,
    get_macd_tool,
    get_on_balance_volume_tool,
    get_reddit_stock_news_tool,
    get_roc_tool,
    get_rsi_tool,
    get_stoch_tool,
    get_stock_metadata_tool,
    get_tsi_tool,
    get_volume_weighted_average_price_tool,
    health_check,
    perform_calculation,
)


def test_safe_pow() -> None:
    assert _safe_pow(2.0, 3.0) == 8.0
    assert _safe_pow(2.0, -1.0) == 0.5

    with pytest.raises(ValueError, match="Exponent 1001 too large"):
        _safe_pow(2.0, 1001)

    with pytest.raises(ValueError, match="Exponent -1001 too large"):
        _safe_pow(2.0, -1001)


def test_safe_eval_constants() -> None:
    assert _safe_eval(ast.parse("42", mode="eval").body) == 42.0
    assert _safe_eval(ast.parse("3.14", mode="eval").body) == 3.14

    with pytest.raises(ValueError, match="Only numeric constants allowed"):
        _safe_eval(ast.parse("'hello'", mode="eval").body)


def test_safe_eval_binop() -> None:
    assert _safe_eval(ast.parse("2 + 3", mode="eval").body) == 5.0
    assert _safe_eval(ast.parse("5 - 2", mode="eval").body) == 3.0
    assert _safe_eval(ast.parse("4 * 3", mode="eval").body) == 12.0
    assert _safe_eval(ast.parse("10 / 2", mode="eval").body) == 5.0
    assert _safe_eval(ast.parse("2 ** 3", mode="eval").body) == 8.0

    with pytest.raises(ValueError, match="Arithmetic error: division by zero"):
        _safe_eval(ast.parse("1 / 0", mode="eval").body)


def test_safe_eval_unaryop() -> None:
    assert _safe_eval(ast.parse("-5", mode="eval").body) == -5.0


def test_safe_eval_unsupported() -> None:
    with pytest.raises(ValueError, match="Unsupported expression"):
        _safe_eval(ast.parse("x", mode="eval").body)

    with pytest.raises(ValueError, match="Unsupported expression"):
        _safe_eval(ast.parse("[1, 2]", mode="eval").body)


def test_perform_calculation() -> None:
    assert perform_calculation("2 + 3 * 4") == 14.0
    assert perform_calculation("(2 + 3) * 4") == 20.0


@pytest.mark.asyncio
async def test_health_check() -> None:
    request = MagicMock()
    response = await health_check(request)
    assert json.loads(response.body) == {"status": "ok"}
    assert response.status_code == 200


def test_get_stock_metadata_tool(mocker: MockerFixture) -> None:
    mock_get_metadata = mocker.patch("stock_analysis_mcp.api.mcp_server.get_equity_metadata", return_value={"sector": "Technology"})
    res = get_stock_metadata_tool("AAPL")
    mock_get_metadata.assert_called_once_with("AAPL")
    assert res == {"sector": "Technology"}


def test_get_equity_data(mocker: MockerFixture) -> None:
    mock_df = MagicMock()
    mock_df.values.tolist.return_value = [[1, 2, 3]]
    mock_get_data = mocker.patch("stock_analysis_mcp.api.mcp_server.get_data", return_value=mock_df)
    res = get_equity_data("AAPL", "2023-01-01", "2023-01-31")
    mock_get_data.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")
    assert res == [[1, 2, 3]]


def test_get_macd_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_macd", return_value=[1.0, 2.0])
    assert get_macd_tool("AAPL", "2023-01-01", "2023-01-31") == [1.0, 2.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_rsi_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_rsi", return_value=[50.0, 60.0])
    assert get_rsi_tool("AAPL", "2023-01-01", "2023-01-31") == [50.0, 60.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_tsi_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_tsi", return_value=[1.0, -1.0])
    assert get_tsi_tool("AAPL", "2023-01-01", "2023-01-31") == [1.0, -1.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_stoch_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_stoch", return_value=[80.0, 20.0])
    assert get_stoch_tool("AAPL", "2023-01-01", "2023-01-31", 14, 3) == [80.0, 20.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31", 14, 3)


def test_get_roc_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_roc", return_value=[5.0, 10.0])
    assert get_roc_tool("AAPL", "2023-01-01", "2023-01-31", 12) == [5.0, 10.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31", 12)


def test_get_ema_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_ema", return_value=[150.0, 155.0])
    assert get_ema_tool("AAPL", "2023-01-01", "2023-01-31", 12) == [150.0, 155.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31", 12)


def test_get_ichimoku_a_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_ichimoku_a", return_value=[100.0, 105.0])
    assert get_ichimoku_a_tool("AAPL", "2023-01-01", "2023-01-31") == [100.0, 105.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_ichimoku_b_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_ichimoku_b", return_value=[90.0, 95.0])
    assert get_ichimoku_b_tool("AAPL", "2023-01-01", "2023-01-31") == [90.0, 95.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_on_balance_volume_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_on_balance_volume", return_value=[1000.0, 2000.0])
    assert get_on_balance_volume_tool("AAPL", "2023-01-01", "2023-01-31") == [1000.0, 2000.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_chaikin_money_flow_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_chaikin_money_flow", return_value=[0.1, 0.2])
    assert get_chaikin_money_flow_tool("AAPL", "2023-01-01", "2023-01-31") == [0.1, 0.2]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_volume_weighted_average_price_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_volume_weighted_average_price", return_value=[150.0, 152.0])
    assert get_volume_weighted_average_price_tool("AAPL", "2023-01-01", "2023-01-31") == [150.0, 152.0]
    mock_func.assert_called_once_with("AAPL", "2023-01-01", "2023-01-31")


def test_get_reddit_stock_news_tool(mocker: MockerFixture) -> None:
    mock_func = mocker.patch("stock_analysis_mcp.api.mcp_server.get_reddit_stock_news", return_value=[{"title": "News"}])
    assert get_reddit_stock_news_tool("AAPL", "week") == [{"title": "News"}]
    mock_func.assert_called_once_with("AAPL", "week")
