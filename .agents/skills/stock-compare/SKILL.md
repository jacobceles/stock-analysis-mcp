---
name: stock-compare
description: Compare multiple stocks side-by-side using key technical indicators and metadata. Use when the user wants to compare two or more stocks.
---

# Stock Comparison

Compare multiple stocks using metadata and technical indicators.

## Ticker Format

- **US stocks**: Standard tickers (e.g., `AAPL`, `MSFT`)
- **Indian stocks (NSE)**: Append `.NS` (e.g., `RELIANCE.NS`)
- **Indian stocks (BSE)**: Append `.BO` (e.g., `500325.BO`)

## Workflow

For each stock the user wants to compare:

1. **Fetch metadata**:
   ```bash
   uv run python -m stock_analysis_mcp metadata <SYMBOL>
   ```

2. **Fetch key indicators** (use the last 3 months if no date range specified):
   ```bash
   uv run python -m stock_analysis_mcp rsi <SYMBOL> --start <DATE> --end <DATE>
   uv run python -m stock_analysis_mcp macd <SYMBOL> --start <DATE> --end <DATE>
   uv run python -m stock_analysis_mcp ema <SYMBOL> --start <DATE> --end <DATE>
   uv run python -m stock_analysis_mcp obv <SYMBOL> --start <DATE> --end <DATE>
   ```

3. **Present comparison** as a table:

| Metric | STOCK_A | STOCK_B |
|---|---|---|
| Sector | ... | ... |
| PE Ratio | ... | ... |
| RSI (latest) | ... | ... |
| MACD (latest) | ... | ... |
| EMA trend | Bullish/Bearish | Bullish/Bearish |
| OBV trend | Rising/Falling | Rising/Falling |

4. **Recommendation**: Which stock(s) look more favorable and why.

## Tips

- Use the latest value from indicator arrays (last element) for current readings
- Compare trends over the period, not just single values
- Consider sector and market cap differences when comparing
