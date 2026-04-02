---
name: stock-sentiment
description: Analyze Reddit sentiment for a stock symbol. Use when the user asks about market sentiment, social media discussion, or news about a stock.
---

# Stock Sentiment Analysis

Fetch and analyze Reddit discussions about a stock to gauge market sentiment.

## Prerequisites

Requires `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` environment variables. Get credentials at https://www.reddit.com/prefs/apps (create a "script" application).

## Ticker Format

- **US stocks**: Standard tickers (e.g., `AAPL`, `MSFT`)
- **Indian stocks (NSE)**: Append `.NS` (e.g., `RELIANCE.NS`)
- **Indian stocks (BSE)**: Append `.BO` (e.g., `500325.BO`)

## Usage

```bash
uv run python -m stock_analysis_mcp reddit <SYMBOL> --time-filter <FILTER>
```

Time filters: `hour`, `day`, `week`, `month` (default), `year`, `all`

## Analysis Workflow

1. Fetch Reddit data:
   ```bash
   uv run python -m stock_analysis_mcp reddit <SYMBOL> --time-filter week
   ```

2. The output is a JSON list of posts sorted by score, each containing:
   - `title`, `content`, `url`, `score`, `subreddit`
   - `num_comments`, `comments` (top comments with scores)
   - `flair`, `created_utc`

3. Analyze and present:
   - **Overall sentiment**: Bullish / Bearish / Mixed
   - **Key themes**: What people are discussing
   - **Top posts**: Most upvoted discussions with links
   - **Notable comments**: Insightful or contrarian views

## Sources

Data is sourced from Indian stock subreddits: IndianStockMarket, IndianStreetBets, StockMarketIndia. For US stocks, results may be limited.
