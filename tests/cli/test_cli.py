import json
import sys

from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest

from stock_analysis_mcp.cli import build_parser, main, perform_calculation


class TestBuildParser:
    def test_parser_requires_command(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_metadata_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["metadata", "AAPL"])
        assert args.command == "metadata"
        assert args.symbol == "AAPL"

    def test_rsi_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["rsi", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        assert args.command == "rsi"
        assert args.symbol == "AAPL"
        assert args.start == "2025-01-01"
        assert args.end == "2025-03-31"

    def test_stoch_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["stoch", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        assert args.window == 14
        assert args.smooth_window == 3

    def test_stoch_custom_windows(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["stoch", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31", "--window", "20", "--smooth-window", "5"])
        assert args.window == 20
        assert args.smooth_window == 5

    def test_roc_default_window(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["roc", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        assert args.window == 12

    def test_ema_default_window(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["ema", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        assert args.window == 12

    def test_reddit_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["reddit", "AAPL"])
        assert args.time_filter == "month"

    def test_reddit_custom_filter(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["reddit", "AAPL", "--time-filter", "week"])
        assert args.time_filter == "week"

    def test_calc_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["calc", "2 + 3 * 4"])
        assert args.command == "calc"
        assert args.equation == "2 + 3 * 4"

    def test_indicator_missing_dates(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["rsi", "AAPL"])

    def test_all_simple_indicators_parse(self) -> None:
        parser = build_parser()
        for cmd in ["macd", "rsi", "tsi", "ichimoku-a", "ichimoku-b", "adx", "psar-up", "psar-down", "aroon-up", "aroon-down", "obv", "cmf", "vwap"]:
            args = parser.parse_args([cmd, "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
            assert args.command == cmd
            assert args.symbol == "AAPL"


class TestPerformCalculation:
    def test_basic_arithmetic(self) -> None:
        assert perform_calculation("2 + 3") == 5.0

    def test_order_of_operations(self) -> None:
        assert perform_calculation("2 + 3 * 4") == 14.0

    def test_negative_numbers(self) -> None:
        assert perform_calculation("-5 + 3") == -2.0

    def test_division(self) -> None:
        assert perform_calculation("10 / 4") == 2.5

    def test_power(self) -> None:
        assert perform_calculation("2 ** 3") == 8.0

    def test_division_by_zero(self) -> None:
        with pytest.raises(ValueError, match="Arithmetic error"):
            perform_calculation("1 / 0")

    def test_large_exponent(self) -> None:
        with pytest.raises(ValueError, match="Exponent"):
            perform_calculation("2 ** 10000")

    def test_invalid_expression(self) -> None:
        with pytest.raises(SyntaxError):
            perform_calculation("import os")


class TestMainOutput:
    def _capture_output(self, argv: list[str]) -> str:
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            main(argv)
        finally:
            sys.stdout = old_stdout
        return captured.getvalue()

    def test_calc_json_output(self) -> None:
        output = self._capture_output(["calc", "2 + 3"])
        result = json.loads(output)
        assert result == 5.0

    @patch("stock_analysis_mcp.cli.get_equity_metadata")
    def test_metadata_json_output(self, mock_metadata: object) -> None:
        mock_metadata.return_value = {"symbol": "AAPL", "sector": "Technology"}  # type: ignore
        output = self._capture_output(["metadata", "AAPL"])
        result = json.loads(output)
        assert result["symbol"] == "AAPL"
        assert result["sector"] == "Technology"

    @patch("stock_analysis_mcp.cli.get_rsi")
    def test_rsi_json_output(self, mock_rsi: object) -> None:
        mock_rsi.return_value = [50.0, 55.0, 60.0]  # type: ignore
        output = self._capture_output(["rsi", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        result = json.loads(output)
        assert result == [50.0, 55.0, 60.0]

    @patch("stock_analysis_mcp.cli.get_macd")
    def test_macd_json_output(self, mock_macd: object) -> None:
        mock_macd.return_value = [1.0, 2.0, 3.0]  # type: ignore
        output = self._capture_output(["macd", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        result = json.loads(output)
        assert result == [1.0, 2.0, 3.0]

    @patch("stock_analysis_mcp.cli.get_data")
    def test_history_json_output(self, mock_data: object) -> None:
        df = pd.DataFrame({"Open": [100.0], "Close": [105.0]})
        mock_data.return_value = df  # type: ignore
        output = self._capture_output(["history", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31"])
        result = json.loads(output)
        assert isinstance(result, list)

    @patch("stock_analysis_mcp.cli.get_reddit_stock_news")
    def test_reddit_json_output(self, mock_reddit: object) -> None:
        mock_reddit.return_value = [{"title": "AAPL to the moon", "score": 42}]  # type: ignore
        output = self._capture_output(["reddit", "AAPL", "--time-filter", "week"])
        result = json.loads(output)
        assert len(result) == 1
        assert result[0]["title"] == "AAPL to the moon"

    @patch("stock_analysis_mcp.cli.get_stoch")
    def test_stoch_passes_windows(self, mock_stoch: object) -> None:
        mock_stoch.return_value = [50.0]  # type: ignore
        self._capture_output(["stoch", "AAPL", "--start", "2025-01-01", "--end", "2025-03-31", "--window", "20", "--smooth-window", "5"])
        mock_stoch.assert_called_once_with("AAPL", "2025-01-01", "2025-03-31", 20, 5)  # type: ignore

    def test_error_outputs_json(self) -> None:
        with patch("stock_analysis_mcp.cli.get_equity_metadata", side_effect=RuntimeError("test error")):
            captured = StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            with pytest.raises(SystemExit):
                main(["metadata", "INVALID"])
            sys.stdout = old_stdout
            result = json.loads(captured.getvalue())
            assert "error" in result


class TestMainModule:
    def test_main_module_invocation(self) -> None:
        with patch("stock_analysis_mcp.cli.main") as mock_main:
            import runpy

            runpy.run_module("stock_analysis_mcp", run_name="__main__")
            mock_main.assert_called_once()
