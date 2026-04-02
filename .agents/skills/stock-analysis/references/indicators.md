# Available Indicators

All commands output JSON to stdout. Usage: `uv run python -m stock_analysis_mcp <command> <SYMBOL> [options]`

## Data Commands

| Command | Description | Example |
|---|---|---|
| `metadata <SYMBOL>` | Company info (PE, sector, etc.) | `metadata AAPL` |
| `history <SYMBOL> --start DATE --end DATE` | Historical OHLCV data | `history AAPL --start 2025-01-01 --end 2025-03-31` |
| `calc <EQUATION>` | Safe math expression evaluator | `calc "2 + 3 * 4"` |

## Momentum Indicators

| Command | Description | Interpretation |
|---|---|---|
| `macd` | Moving Average Convergence Divergence | Positive = bullish momentum, negative = bearish. Crossovers signal trend changes. |
| `rsi` | Relative Strength Index | > 70 = overbought, < 30 = oversold. Divergences signal reversals. |
| `tsi` | True Strength Index | Similar to RSI but smoother. Positive = bullish, crossover of signal line = trade signal. |
| `stoch --window N --smooth-window N` | Stochastic Oscillator | > 80 = overbought, < 20 = oversold. Default: window=14, smooth=3. |
| `roc --window N` | Rate of Change | Positive = upward momentum, negative = downward. Default: window=12. |

## Trend Indicators

| Command | Description | Interpretation |
|---|---|---|
| `ema --window N` | Exponential Moving Average | Price above EMA = uptrend, below = downtrend. Default: window=12. |
| `ichimoku-a` | Ichimoku Cloud A | Leading span A of the cloud. |
| `ichimoku-b` | Ichimoku Cloud B | Leading span B. Price above both = strong bullish. |
| `adx` | Average Directional Index | > 25 = strong trend, < 20 = no trend. Does not indicate direction. |
| `psar-up` | Parabolic SAR (uptrend) | Dots below price = uptrend confirmed. |
| `psar-down` | Parabolic SAR (downtrend) | Dots above price = downtrend confirmed. |
| `aroon-up` | Aroon Up | > 70 = strong uptrend, < 30 = weak. |
| `aroon-down` | Aroon Down | > 70 = strong downtrend, < 30 = weak. |

## Volume Indicators

| Command | Description | Interpretation |
|---|---|---|
| `obv` | On-Balance Volume | Rising OBV = accumulation (bullish), falling = distribution (bearish). |
| `cmf` | Chaikin Money Flow | Positive = buying pressure, negative = selling pressure. |
| `vwap` | Volume Weighted Average Price | Price above VWAP = bullish, below = bearish. Institutional benchmark. |

## Reddit Sentiment

| Command | Description |
|---|---|
| `reddit <SYMBOL> --time-filter FILTER` | Reddit discussions. Filters: hour, day, week, month, year, all. Default: month. |

## Common Options

All indicator commands require:
- `<SYMBOL>` — positional argument (e.g., `AAPL`, `RELIANCE.NS`)
- `--start YYYY-MM-DD` — start date
- `--end YYYY-MM-DD` — end date
