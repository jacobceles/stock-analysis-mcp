# Stock Analysis Skills

A framework-agnostic stock analysis toolkit that works with any LLM agent — Claude Code, Cursor, Copilot, Codex, OpenClaw, ADK, or any tool that supports [SKILL.md](https://agentskills.io/specification).

## Features

- **Technical Indicators**: MACD, RSI, TSI, EMA, ROC, Stochastic Oscillator, Ichimoku Cloud, ADX, Parabolic SAR, Aroon
- **Volume Metrics**: On-Balance Volume (OBV), Chaikin Money Flow (CMF), VWAP
- **Reddit Sentiment**: Stock news and discussions from Reddit
- **Global Stock Data**: NSE, NYSE, NASDAQ, BSE via `yfinance`
- **Framework-Agnostic Skills**: Auto-discovered by any SKILL.md-compatible agent
- **JSON CLI**: All data accessible via command-line with JSON output
- **Web UI**: ADK-powered web interface with LiteLLM

## Prerequisites

- [Python 3.14+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [prek](https://github.com/j178/prek) — Git hook runner (recommended)

```bash
# macOS
brew install python@3.14 uv j178/tap/prek

# Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://raw.githubusercontent.com/j178/prek/main/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
cargo install prek

# Any platform with Rust
cargo install prek
```

## Quick Start

### 1. Setup

```bash
make setup
```

### 2. Use the CLI

```bash
# Stock metadata
uv run python -m stock_analysis_mcp metadata AAPL

# Technical indicators
uv run python -m stock_analysis_mcp rsi AAPL --start 2025-01-01 --end 2025-03-31
uv run python -m stock_analysis_mcp macd RELIANCE.NS --start 2025-01-01 --end 2025-03-31

# Reddit sentiment (requires REDDIT_CLIENT_ID/SECRET env vars)
uv run python -m stock_analysis_mcp reddit AAPL --time-filter week

# Math calculations
uv run python -m stock_analysis_mcp calc "100 * 1.05 ** 5"
```

All commands output JSON to stdout.

## Using with LLM Agents

Skills are located in `.agents/skills/` and are auto-discovered by compatible agents.

| Agent/Framework | How It Works |
|---|---|
| Claude Code | Discovers `.agents/skills/`, runs CLI via Bash |
| Cursor | Discovers `.agents/skills/`, runs CLI via terminal |
| Copilot | Discovers `.agents/skills/`, runs CLI via terminal |
| Codex | Discovers `.agents/skills/`, runs CLI via shell |
| OpenClaw | Loads skills, runs CLI via shell execution |
| Google ADK | Discovers `.agents/skills/` via SkillToolset |

### Available Skills

| Skill | Description |
|---|---|
| `stock-analysis` | Full technical analysis with BUY/SELL/HOLD recommendation |
| `stock-sentiment` | Reddit sentiment analysis for a stock |
| `stock-compare` | Side-by-side comparison of multiple stocks |

### Ticker Format

- **US stocks**: Standard tickers (e.g., `AAPL`, `MSFT`, `TSLA`)
- **Indian stocks (NSE)**: Append `.NS` (e.g., `RELIANCE.NS`, `TCS.NS`)
- **Indian stocks (BSE)**: Append `.BO` (e.g., `500325.BO`)

## Web UI

Run the built-in web-based stock analysis agent powered by LiteLLM.

### 1. Configure environment

Create a `.env` file (see `.env.sample`):

```bash
LITE_LLM_MODEL=gemini/gemini-2.5-flash
LITE_LLM_API_KEY=your-api-key
```

### 2. Run

**Local:**
```bash
uv run python -m stock_analysis_mcp.api.adk_server
```

**Docker:**
```bash
make docker-build
make docker-up
```

Once running, open the Web UI at **http://localhost:8080/dev-ui/** and select `stock_ta_assistant` from the agent dropdown.

### Sample Prompts

> Analyze the technical indicators for RELIANCE.NS over the last month and show me a candlestick chart.

> Analyze the technical indicators for AAPL over the last month and plot the RSI alongside price action.

> What's the Reddit sentiment for TCS.NS this week?

*Note: For Indian stocks, append `.NS` for NSE or `.BO` for BSE (e.g., `RELIANCE.NS`). US stocks use standard tickers (e.g., `AAPL`).*

## CLI Reference

All indicator commands require `--start YYYY-MM-DD --end YYYY-MM-DD`.

| Command | Description | Extra Options |
|---|---|---|
| `metadata <SYMBOL>` | Company info (PE, sector, etc.) | — |
| `history <SYMBOL>` | Historical OHLCV data | — |
| `macd <SYMBOL>` | MACD | — |
| `rsi <SYMBOL>` | Relative Strength Index | — |
| `tsi <SYMBOL>` | True Strength Index | — |
| `stoch <SYMBOL>` | Stochastic Oscillator | `--window`, `--smooth-window` |
| `roc <SYMBOL>` | Rate of Change | `--window` |
| `ema <SYMBOL>` | Exponential Moving Average | `--window` |
| `ichimoku-a <SYMBOL>` | Ichimoku Cloud A | — |
| `ichimoku-b <SYMBOL>` | Ichimoku Cloud B | — |
| `adx <SYMBOL>` | Average Directional Index | — |
| `psar-up <SYMBOL>` | Parabolic SAR (uptrend) | — |
| `psar-down <SYMBOL>` | Parabolic SAR (downtrend) | — |
| `aroon-up <SYMBOL>` | Aroon Up | — |
| `aroon-down <SYMBOL>` | Aroon Down | — |
| `obv <SYMBOL>` | On-Balance Volume | — |
| `cmf <SYMBOL>` | Chaikin Money Flow | — |
| `vwap <SYMBOL>` | VWAP | — |
| `reddit <SYMBOL>` | Reddit sentiment | `--time-filter` (hour/day/week/month/year/all) |
| `calc <EQUATION>` | Math expression evaluator | — |

## Environment Variables

| Variable | Required For | Default |
|---|---|---|
| `REDDIT_CLIENT_ID` | Reddit sentiment | — |
| `REDDIT_CLIENT_SECRET` | Reddit sentiment | — |
| `REDDIT_USER_AGENT` | Reddit sentiment | `stock-analysis-mcp/1.0` |
| `LITE_LLM_MODEL` | Web UI | — |
| `LITE_LLM_API_KEY` | Web UI | — |
| `HOST` | Server binding | `127.0.0.1` |
| `PORT` | Server port | `8080` |
| `LOG_FORMAT` | Logging style | `json` (`color` for dev) |

## Development

```bash
make setup      # Install dependencies + git hooks
make test       # Run tests (parallel with pytest-xdist)
make format     # Format code (ruff)
make lint       # Lint code (ruff)
make typecheck  # Type check (mypy + pyrefly)
make all        # Run everything
```

### Git Hooks

Git hooks are managed via [prek](https://github.com/j178/prek) — a fast, Rust-based hook runner. Install it before running `make setup`:

```bash
brew install j178/tap/prek    # macOS
# or
cargo install prek            # any platform with Rust
```

If prek is not installed, `make setup` will print a warning and skip hook installation.

## Credits

- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [PRAW](https://github.com/praw-dev/praw) for Reddit integration
- [ta](https://github.com/bukosabino/ta) for technical analysis indicators
