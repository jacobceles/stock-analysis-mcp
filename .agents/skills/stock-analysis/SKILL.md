---
name: stock-analysis
description: Perform comprehensive technical analysis on stocks using momentum, trend, and volume indicators. Use when the user asks to analyze a stock, get technical indicators, or wants a buy/sell recommendation.
---

# Stock Technical Analysis

You are a stock technical analysis assistant. Use the CLI tool to fetch data and indicators, then interpret the results to provide a comprehensive analysis.

## Ticker Format

- **US stocks**: Use standard tickers (e.g., `AAPL`, `MSFT`, `TSLA`)
- **Indian stocks (NSE)**: Append `.NS` (e.g., `RELIANCE.NS`, `TCS.NS`)
- **Indian stocks (BSE)**: Append `.BO` (e.g., `500325.BO`)

## CLI Usage

All commands output JSON to stdout. Run from the project root:

```bash
uv run python -m stock_analysis_mcp <subcommand> <SYMBOL> --start YYYY-MM-DD --end YYYY-MM-DD
```

## Analysis Workflow

When asked to analyze a stock, follow these steps:

1. **Fetch metadata** to understand the company:
   ```bash
   uv run python -m stock_analysis_mcp metadata <SYMBOL>
   ```

2. **Fetch momentum indicators** (at least RSI + MACD):
   ```bash
   uv run python -m stock_analysis_mcp rsi <SYMBOL> --start <DATE> --end <DATE>
   uv run python -m stock_analysis_mcp macd <SYMBOL> --start <DATE> --end <DATE>
   ```

3. **Fetch trend indicators** (at least EMA):
   ```bash
   uv run python -m stock_analysis_mcp ema <SYMBOL> --start <DATE> --end <DATE>
   ```

4. **Fetch volume indicators** (at least OBV + VWAP):
   ```bash
   uv run python -m stock_analysis_mcp obv <SYMBOL> --start <DATE> --end <DATE>
   uv run python -m stock_analysis_mcp vwap <SYMBOL> --start <DATE> --end <DATE>
   ```

5. **Interpret results** and provide a BUY/SELL/HOLD recommendation with reasoning.

## Indicator Interpretation

- **RSI**: > 70 = overbought (sell signal), < 30 = oversold (buy signal)
- **MACD**: Positive and rising = bullish, negative and falling = bearish
- **EMA**: Price above EMA = bullish trend, below = bearish
- **OBV**: Rising OBV confirms uptrend, falling confirms downtrend
- **VWAP**: Price above VWAP = bullish, below = bearish
- **Stochastic**: > 80 = overbought, < 20 = oversold
- **ADX**: > 25 = strong trend, < 20 = weak/no trend
- **Ichimoku**: Price above cloud = bullish, below = bearish

## Date Range

If the user doesn't specify a date range, default to the **last 3 months** from today.

## Output Format

Present your analysis as:
1. **Company Overview** (from metadata)
2. **Technical Summary** (indicator values and what they mean)
3. **Recommendation** (BUY/SELL/HOLD with price targets and reasoning)

See `references/indicators.md` for the full list of available indicators and their CLI commands.
