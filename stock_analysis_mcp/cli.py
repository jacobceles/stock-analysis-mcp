import argparse
import ast
import json
import math
import operator
import sys

from collections.abc import Callable
from typing import Any


def _safe_pow(base: float, exp: float) -> float:
    if abs(exp) > 1000:
        raise ValueError(f"Exponent {exp} too large")
    return float(math.pow(base, exp))


_binary_operators: dict[type, Callable[..., float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: _safe_pow,
}

_unary_operators: dict[type, Callable[..., float]] = {
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, int | float):
            return float(node.value)
        raise ValueError("Only numeric constants allowed")
    if isinstance(node, ast.BinOp):
        op = _binary_operators[type(node.op)]
        try:
            return op(_safe_eval(node.left), _safe_eval(node.right))
        except (OverflowError, ZeroDivisionError, ValueError) as e:
            raise ValueError(f"Arithmetic error: {e}") from e
    if isinstance(node, ast.UnaryOp):
        op = _unary_operators[type(node.op)]
        try:
            return op(_safe_eval(node.operand))
        except (OverflowError, ValueError) as e:
            raise ValueError(f"Arithmetic error: {e}") from e
    raise ValueError("Unsupported expression")


def perform_calculation(equation: str) -> float:
    tree = ast.parse(equation, mode="eval")
    return _safe_eval(tree.body)


def _output_json(data: Any) -> None:
    json.dump(data, sys.stdout, default=str)
    print()


def _add_date_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stock_analysis_mcp", description="Stock analysis CLI — JSON output to stdout")
    sub = parser.add_subparsers(dest="command", required=True)

    # metadata
    p = sub.add_parser("metadata", help="Stock metadata (PE ratio, sector, etc.)")
    p.add_argument("symbol", help="Stock symbol (e.g. AAPL, RELIANCE.NS)")

    # history
    p = sub.add_parser("history", help="Historical OHLCV data")
    p.add_argument("symbol", help="Stock symbol")
    _add_date_args(p)

    # Simple indicator commands: (name, help)
    simple_indicators = [
        ("macd", "MACD (Moving Average Convergence Divergence)"),
        ("rsi", "RSI (Relative Strength Index)"),
        ("tsi", "TSI (True Strength Index)"),
        ("ichimoku-a", "Ichimoku Cloud component A"),
        ("ichimoku-b", "Ichimoku Cloud component B"),
        ("adx", "Average Directional Index"),
        ("psar-up", "Parabolic SAR (uptrend)"),
        ("psar-down", "Parabolic SAR (downtrend)"),
        ("aroon-up", "Aroon Up indicator"),
        ("aroon-down", "Aroon Down indicator"),
        ("obv", "On-Balance Volume"),
        ("cmf", "Chaikin Money Flow"),
        ("vwap", "Volume Weighted Average Price"),
    ]
    for name, help_text in simple_indicators:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("symbol", help="Stock symbol")
        _add_date_args(p)

    # Indicators with window parameter
    p = sub.add_parser("stoch", help="Stochastic Oscillator")
    p.add_argument("symbol", help="Stock symbol")
    _add_date_args(p)
    p.add_argument("--window", type=int, default=14, help="N period (default: 14)")
    p.add_argument("--smooth-window", type=int, default=3, help="SMA period over stoch_k (default: 3)")

    p = sub.add_parser("roc", help="Rate of Change")
    p.add_argument("symbol", help="Stock symbol")
    _add_date_args(p)
    p.add_argument("--window", type=int, default=12, help="N period (default: 12)")

    p = sub.add_parser("ema", help="Exponential Moving Average")
    p.add_argument("symbol", help="Stock symbol")
    _add_date_args(p)
    p.add_argument("--window", type=int, default=12, help="N period (default: 12)")

    # reddit
    p = sub.add_parser("reddit", help="Reddit stock sentiment")
    p.add_argument("symbol", help="Stock symbol")
    p.add_argument("--time-filter", default="month", choices=["hour", "day", "week", "month", "year", "all"], help="Time filter (default: month)")

    # calc
    p = sub.add_parser("calc", help="Safe math expression evaluator")
    p.add_argument("equation", help="Math expression (e.g. '2 + 3 * 4')")

    return parser


def _get_service_functions() -> dict[str, Callable[..., Any]]:
    """Lazy-import service functions only when needed (avoids loading yfinance/pandas/praw on startup)."""
    from stock_analysis_mcp.services.stock_service import (
        get_adx,
        get_aroon_down,
        get_aroon_up,
        get_chaikin_money_flow,
        get_ema,
        get_ichimoku_a,
        get_ichimoku_b,
        get_macd,
        get_on_balance_volume,
        get_psar_down,
        get_psar_up,
        get_roc,
        get_rsi,
        get_stoch,
        get_tsi,
        get_volume_weighted_average_price,
    )

    return {
        "macd": lambda args: get_macd(args.symbol, args.start, args.end),
        "rsi": lambda args: get_rsi(args.symbol, args.start, args.end),
        "tsi": lambda args: get_tsi(args.symbol, args.start, args.end),
        "stoch": lambda args: get_stoch(args.symbol, args.start, args.end, args.window, args.smooth_window),
        "roc": lambda args: get_roc(args.symbol, args.start, args.end, args.window),
        "ema": lambda args: get_ema(args.symbol, args.start, args.end, args.window),
        "ichimoku-a": lambda args: get_ichimoku_a(args.symbol, args.start, args.end),
        "ichimoku-b": lambda args: get_ichimoku_b(args.symbol, args.start, args.end),
        "adx": lambda args: get_adx(args.symbol, args.start, args.end),
        "psar-up": lambda args: get_psar_up(args.symbol, args.start, args.end),
        "psar-down": lambda args: get_psar_down(args.symbol, args.start, args.end),
        "aroon-up": lambda args: get_aroon_up(args.symbol, args.start, args.end),
        "aroon-down": lambda args: get_aroon_down(args.symbol, args.start, args.end),
        "obv": lambda args: get_on_balance_volume(args.symbol, args.start, args.end),
        "cmf": lambda args: get_chaikin_money_flow(args.symbol, args.start, args.end),
        "vwap": lambda args: get_volume_weighted_average_price(args.symbol, args.start, args.end),
    }


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "calc":
            _output_json(perform_calculation(args.equation))
        else:
            # Lazy-import heavy dependencies only for non-calc commands
            from stock_analysis_mcp.services.stock_service import get_data, get_equity_metadata, get_reddit_stock_news

            if args.command == "metadata":
                _output_json(get_equity_metadata(args.symbol))
            elif args.command == "history":
                _output_json(get_data(args.symbol, args.start, args.end).values.tolist())
            elif args.command == "reddit":
                _output_json(get_reddit_stock_news(args.symbol, args.time_filter))
            else:
                dispatch = _get_service_functions()
                if args.command in dispatch:
                    _output_json(dispatch[args.command](args))
                else:
                    parser.print_help()
                    sys.exit(1)
    except Exception as e:
        _output_json({"error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
