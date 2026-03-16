import ast
import math
import operator
import os

from collections.abc import Callable
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from stock_analysis_mcp.services.stock_service import (
    get_chaikin_money_flow,
    get_data,
    get_ema,
    get_equity_metadata,
    get_ichimoku_a,
    get_ichimoku_b,
    get_macd,
    get_on_balance_volume,
    get_reddit_stock_news,
    get_roc,
    get_rsi,
    get_stoch,
    get_tsi,
    get_volume_weighted_average_price,
)

# Create a server instance
mcp = FastMCP(name="NSE Stock Analysis Server")


def _safe_pow(base: float, exp: float) -> float:
    """
    Safe exponentiation function that limits the exponent size and ensures float results.
    """
    if abs(exp) > 1000:
        raise ValueError(f"Exponent {exp} too large")

    result = math.pow(base, exp)
    return float(result)


binary_operators: dict[type, Callable[..., float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: _safe_pow,
}

unary_operators: dict[type, Callable[..., float]] = {
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, int | float):
            return float(node.value)
        raise ValueError("Only numeric constants allowed")

    if isinstance(node, ast.BinOp):
        op = binary_operators[type(node.op)]
        try:
            return op(_safe_eval(node.left), _safe_eval(node.right))
        except (OverflowError, ZeroDivisionError, ValueError) as e:
            raise ValueError(f"Arithmetic error: {e}") from e

    if isinstance(node, ast.UnaryOp):
        op = unary_operators[type(node.op)]
        try:
            return op(_safe_eval(node.operand))
        except (OverflowError, ValueError) as e:
            raise ValueError(f"Arithmetic error: {e}") from e

    raise ValueError("Unsupported expression")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


@mcp.tool
def perform_calculation(equation: str) -> float:
    """
    Computes the solution of the equation given,

    Params:
    equation: a mathematical equation as a string without any variables
    """
    tree = ast.parse(equation, mode="eval")
    return _safe_eval(tree.body)


@mcp.tool
def get_stock_metadata_tool(symbol: str) -> Any:
    """
    Gets general information about the stock like PE ratio, sector etc

    Params:
    symbol: Upper case symbol of the stock
    """
    return get_equity_metadata(symbol)


@mcp.tool
def get_equity_data(symbol: str, start_date: str, end_date: str) -> Any:
    """
    Gets the historical data for the given stock based on the dates provided

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_data(symbol, start_date, end_date).values.tolist()


# Tools for momentum - MACD, ROC, RSI and Stochastic Oscillator (SR)


@mcp.tool
def get_macd_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Gets the macd numbers for the given symbol

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_macd(symbol, start_date, end_date)


@mcp.tool
def get_rsi_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Gets the rsi for the given symbol

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_rsi(symbol, start_date, end_date)


@mcp.tool
def get_tsi_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Gets the tsi for the given symbol

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_tsi(symbol, start_date, end_date)


@mcp.tool
def get_stoch_tool(
    symbol: str,
    start_date: str,
    end_date: str,
    window: int = 14,
    smooth_window: int = 3,
) -> list[float]:
    """
    Computes the stochastic oscillator

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    window: n period
    smooth_window: sma period over stoch_k
    """
    return get_stoch(symbol, start_date, end_date, window, smooth_window)


@mcp.tool
def get_roc_tool(symbol: str, start_date: str, end_date: str, window: int = 12) -> list[float]:
    """
    Computes the ROC

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    window: n period
    smooth_window: sma period over stoch_k
    """
    return get_roc(symbol, start_date, end_date, window)


# Tools for indicating trend - EMA, Average Directional Index (ADX),  Ichimoku Cloud, Parabolic SAR, Aroon Indicator


@mcp.tool
def get_ema_tool(symbol: str, start_date: str, end_date: str, window: int = 12) -> list[float]:
    """
    Computes the Exponential Moving Average

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    window: n period
    """
    return get_ema(symbol, start_date, end_date, window)


@mcp.tool
def get_ichimoku_a_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Computes the Ichimoku A

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_ichimoku_a(symbol, start_date, end_date)


@mcp.tool
def get_ichimoku_b_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Computes the Ichimoku B

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_ichimoku_b(symbol, start_date, end_date)


def get_on_balance_volume_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Computes the On Balance Volume

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_on_balance_volume(symbol, start_date, end_date)


def get_chaikin_money_flow_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Computes the Chaikin Money Flow (CMF)

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_chaikin_money_flow(symbol, start_date, end_date)


def get_volume_weighted_average_price_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """
    Computes the Volume Weighted Average Price (VWAP)

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_volume_weighted_average_price(symbol, start_date, end_date)


@mcp.tool
def get_reddit_stock_news_tool(symbol: str, time_filter: str = "month") -> list[dict]:
    """
    Fetches recent stock-related news and discussions from Reddit.

    Params:
    symbol: Upper case symbol of the stock
    time_filter: Time filter for Reddit posts. Options: "hour", "day", "week", "month", "year", "all", default: "month"
    """
    return get_reddit_stock_news(symbol, time_filter)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")

    mcp.run(
        transport="sse",
        host=host,
        port=8000,
    )
