import datetime
import logging
import os

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext

from stock_analysis_mcp.agent.tools.plotting import generate_plot, generate_plot_data_agent
from stock_analysis_mcp.core.logging_config import setup_logging
from stock_analysis_mcp.services.stock_service import (
    get_adx,
    get_aroon_down,
    get_aroon_up,
    get_chaikin_money_flow,
    get_data,
    get_ema,
    get_equity_metadata,
    get_ichimoku_a,
    get_ichimoku_b,
    get_macd,
    get_on_balance_volume,
    get_psar_down,
    get_psar_up,
    get_reddit_stock_news,
    get_roc,
    get_rsi,
    get_stoch,
    get_tsi,
    get_volume_weighted_average_price,
)

setup_logging()
logger = logging.getLogger(__name__)

# --- State Keys ---
STATE_TA = "technical_analysis"
STATE_EVAL = "evaluation"
COMPLETION_PHRASE = "STOP EXECUTION"


def exit_loop(tool_context: ToolContext) -> dict[str, Any]:
    """Call this function ONLY when the critique indicates no further changes are needed, signaling
    the iterative process should end."""
    logger.info("  [Tool Call] exit_loop triggered by %s", tool_context.agent_name)
    tool_context.actions.escalate = True
    return {}


# --- Direct function tools (replacing MCPToolset) ---


def get_stock_metadata_tool(symbol: str) -> Any:
    """Gets general information about the stock like PE ratio, sector etc.

    Params:
    symbol: Upper case symbol of the stock
    """
    return get_equity_metadata(symbol)


def get_equity_data(symbol: str, start_date: str, end_date: str) -> Any:
    """Gets the historical data for the given stock based on the dates provided.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_data(symbol, start_date, end_date).values.tolist()


def get_macd_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Gets the MACD numbers for the given symbol.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_macd(symbol, start_date, end_date)


def get_rsi_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Gets the RSI for the given symbol.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_rsi(symbol, start_date, end_date)


def get_tsi_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Gets the TSI for the given symbol.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_tsi(symbol, start_date, end_date)


def get_stoch_tool(symbol: str, start_date: str, end_date: str, window: int = 14, smooth_window: int = 3) -> list[float]:
    """Computes the stochastic oscillator.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    window: n period
    smooth_window: sma period over stoch_k
    """
    return get_stoch(symbol, start_date, end_date, window, smooth_window)


def get_roc_tool(symbol: str, start_date: str, end_date: str, window: int = 12) -> list[float]:
    """Computes the ROC.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    window: n period
    """
    return get_roc(symbol, start_date, end_date, window)


def get_ema_tool(symbol: str, start_date: str, end_date: str, window: int = 12) -> list[float]:
    """Computes the Exponential Moving Average.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    window: n period
    """
    return get_ema(symbol, start_date, end_date, window)


def get_ichimoku_a_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Ichimoku A.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_ichimoku_a(symbol, start_date, end_date)


def get_ichimoku_b_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Ichimoku B.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_ichimoku_b(symbol, start_date, end_date)


def get_adx_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Average Directional Index (ADX).

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_adx(symbol, start_date, end_date)


def get_psar_up_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Parabolic SAR (uptrend).

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_psar_up(symbol, start_date, end_date)


def get_psar_down_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Parabolic SAR (downtrend).

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_psar_down(symbol, start_date, end_date)


def get_aroon_up_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Aroon Up indicator.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_aroon_up(symbol, start_date, end_date)


def get_aroon_down_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Aroon Down indicator.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_aroon_down(symbol, start_date, end_date)


def get_on_balance_volume_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the On Balance Volume.

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_on_balance_volume(symbol, start_date, end_date)


def get_chaikin_money_flow_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Chaikin Money Flow (CMF).

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_chaikin_money_flow(symbol, start_date, end_date)


def get_volume_weighted_average_price_tool(symbol: str, start_date: str, end_date: str) -> list[float]:
    """Computes the Volume Weighted Average Price (VWAP).

    Params:
    symbol: Upper case symbol of the stock
    start_date: the start date of the range, should be in YYYY-MM-DD
    end_date: the end date of the range, should be in YYYY-MM-DD
    """
    return get_volume_weighted_average_price(symbol, start_date, end_date)


def get_reddit_stock_news_tool(symbol: str, time_filter: str = "month") -> list[dict]:
    """Fetches recent stock-related news and discussions from Reddit.

    Params:
    symbol: Upper case symbol of the stock
    time_filter: Time filter for Reddit posts. Options: "hour", "day", "week", "month", "year", "all", default: "month"
    """
    return get_reddit_stock_news(symbol, time_filter)


today_date = datetime.datetime.now().strftime("%A, %d %B %Y")

ta_agent = LlmAgent(
    name="stock_ta_assistant",
    model=LiteLlm(
        model=os.environ.get("LITE_LLM_MODEL", ""),
        api_key=os.environ.get("LITE_LLM_API_KEY", ""),
    ),
    instruction=f"""
    You are an agent that helps to perform technical analysis for Global stocks (India, USA, etc.).
    The user will provide you with a stock ticker symbol.

    Ticker format guidelines:
    - For US stocks, use standard tickers (e.g., "AAPL", "MSFT", "TSLA").
    - For Indian stocks (NSE), append ".NS" (e.g., "RELIANCE.NS", "TCS.NS").
    - For Indian stocks (BSE), append ".BO" (e.g., "500325.BO").

    You have to use the given tools to perform technical analysis and provide sound information to the user.
    You can also fetch recent stock-related news and discussions from Reddit.
    You can also plot OHLC candlestick charts.
    While performing analysis try to plot relevant graphs for each of the indicators to support your analysis.
    You have to decide whether to BUY or SELL stock and at what price should the action to be taken.
    This action will then executed inside a simulated enviroment to evaluate your capabilities.

    While generating plots, STRICTLY ensure you follow these workflow:
    1. Call the `generate_plot_data_agent` tool with valid data.
    2. Call the `generate_plot` tool with the output from previous step to generate and save the plot as an artifact.

    Today's date is {today_date}.
    """,
    tools=[
        get_stock_metadata_tool,
        get_equity_data,
        get_macd_tool,
        get_rsi_tool,
        get_tsi_tool,
        get_stoch_tool,
        get_roc_tool,
        get_ema_tool,
        get_ichimoku_a_tool,
        get_ichimoku_b_tool,
        get_adx_tool,
        get_psar_up_tool,
        get_psar_down_tool,
        get_aroon_up_tool,
        get_aroon_down_tool,
        get_on_balance_volume_tool,
        get_chaikin_money_flow_tool,
        get_volume_weighted_average_price_tool,
        get_reddit_stock_news_tool,
        generate_plot_data_agent,
        generate_plot,
    ],
    output_key=STATE_TA,
)

root_agent = ta_agent
