import logging
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd
import praw  # type: ignore
import ta.trend  # type: ignore
import yfinance as yf  # type: ignore

from praw.models import Submission  # type: ignore
from ta.momentum import roc, rsi, stoch, tsi  # type: ignore
from ta.trend import adx, aroon_down, aroon_up, ema_indicator, ichimoku_a, ichimoku_b, macd, psar_down  # type: ignore
from ta.volume import chaikin_money_flow, on_balance_volume, volume_weighted_average_price  # type: ignore

from stock_analysis_mcp.core.constants import (
    DUMP_DIR,
    REDDIT_BATCH_SIZE,
    REDDIT_POST_LIMIT,
    REDDIT_SUBREDDITS,
)
from stock_analysis_mcp.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Manual cache that skips empty DataFrames (errors/missing data are not cached)
_data_cache: dict[tuple[str, str, str], pd.DataFrame] = {}


def clear_cache() -> None:
    """Clear the data cache. Useful for testing."""
    _data_cache.clear()


def get_equity_metadata(symbol: str) -> dict:
    """Fetches metadata for a given symbol using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except Exception as e:
        logger.error("Error fetching metadata for %s: %s", symbol, e)
        return {}


def _get_data_internal(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Internal function to fetch and cache historical price data. Only successful fetches are cached."""
    key = (symbol, start_date, end_date)
    if key in _data_cache:
        return _data_cache[key]

    dump_dir = Path(DUMP_DIR).resolve()
    os.makedirs(dump_dir, exist_ok=True)
    file_name = f"{symbol}_{start_date}_{end_date}.csv"
    file_path = (dump_dir / file_name).resolve()

    if not file_path.is_relative_to(dump_dir):
        raise ValueError("Invalid symbol or dates: path traversal detected")

    if file_path.exists():
        df = pd.read_csv(file_path)
        _data_cache[key] = df
        return df

    try:
        logger.info("Fetching data for %s from %s to %s", symbol, start_date, end_date)
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if df.empty:
            logger.warning("No data found for %s", symbol)
            return pd.DataFrame()

        # Handle multi-index columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df = df.rename(columns={"Adj Close": "Adj_Close"})

        df.to_csv(file_path, index=False)
        _data_cache[key] = df
        return df

    except Exception as e:
        logger.error("Error fetching data for %s: %s", symbol, e)
        return pd.DataFrame()


def get_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetches historical price data. Returns cached data directly (read-only)."""
    return _get_data_internal(symbol, start_date, end_date)


def get_macd(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return macd(df.Close, fillna=True).tolist()


def get_rsi(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return rsi(df.Close, fillna=True).tolist()


def get_tsi(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return tsi(df.Close, fillna=True).tolist()


def get_stoch(symbol: str, start_date: str, end_date: str, window: int, smooth_window: int) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return stoch(
        df.High,
        df.Low,
        df.Close,
        window,
        smooth_window,
        fillna=True,
    ).tolist()


def get_roc(symbol: str, start_date: str, end_date: str, window: int) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return roc(df.Close, window, fillna=True).tolist()


def get_ema(symbol: str, start_date: str, end_date: str, window: int) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return ema_indicator(df.Close, window, fillna=True).tolist()


def get_ichimoku_a(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return ichimoku_a(df.High, df.Low, fillna=True).tolist()


def get_ichimoku_b(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return ichimoku_b(df.High, df.Low, fillna=True).tolist()


def get_adx(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return adx(df.High, df.Low, df.Close, fillna=True).tolist()


def get_psar_up(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    psar = ta.trend.PSARIndicator(high=df["High"], low=df["Low"], close=df["Close"])
    return psar.psar_up().dropna().tolist()


def get_psar_down(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return psar_down(df.High, df.Low, df.Close, fillna=True).tolist()


def get_aroon_up(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return aroon_up(df.High, df.Low, df.Close, fillna=True).tolist()


def get_aroon_down(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return aroon_down(df.High, df.Low, df.Close, fillna=True).tolist()


def get_on_balance_volume(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return on_balance_volume(df.Close, df.Volume, fillna=True).tolist()


def get_chaikin_money_flow(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return chaikin_money_flow(
        df.High,
        df.Low,
        df.Close,
        df.Volume,
        fillna=True,
    ).tolist()


def get_volume_weighted_average_price(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    if df.empty:
        return []
    return volume_weighted_average_price(
        df.High,
        df.Low,
        df.Close,
        df.Volume,
        fillna=True,
    ).tolist()


def _truncate_text(text: str, limit: int = 500) -> str:
    """Helper function to truncate text to a specified limit, appending '...' if truncated."""
    return text[:limit] + "..." if len(text) > limit else text


def get_reddit_stock_news(symbol: str, time_filter: str = "month") -> list[dict]:
    try:
        reddit_client_id = os.environ.get("REDDIT_CLIENT_ID")
        reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
        reddit_user_agent = os.environ.get("REDDIT_USER_AGENT", "stock-analysis-mcp/1.0")
        limit = REDDIT_POST_LIMIT

        reddit = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret, user_agent=reddit_user_agent)

        posts = []
        search_query = f"{symbol} OR '${symbol}'"

        # Single executor reused for all subreddit fetching and comment fetching
        with ThreadPoolExecutor(max_workers=REDDIT_BATCH_SIZE) as executor:

            def _fetch_subreddit(subreddit_name: str) -> list[dict]:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    search_results = list(subreddit.search(search_query, limit=limit, time_filter=time_filter))

                    # Fetch comments using the shared executor
                    post_comments: dict[int, list[dict]] = {}
                    comment_futures = {executor.submit(get_top_comments, post, 5): idx for idx, post in enumerate(search_results)}
                    for future in as_completed(comment_futures):
                        post_comments[comment_futures[future]] = future.result()

                    results = []
                    for idx, post in enumerate(search_results):
                        results.append(
                            {
                                "title": post.title,
                                "content": _truncate_text(post.selftext, 500),
                                "url": f"https://reddit.com{post.permalink}",
                                "score": post.score,
                                "subreddit": subreddit_name,
                                "created_utc": post.created_utc,
                                "num_comments": post.num_comments,
                                "comments": post_comments.get(idx, []),
                                "flair": post.link_flair_text if post.link_flair_text else "None",
                            }
                        )
                    return results
                except Exception as e:
                    logger.warning("Error fetching Reddit posts for %s: %s", symbol, e)
                    return []

            for i in range(0, len(REDDIT_SUBREDDITS), REDDIT_BATCH_SIZE):
                batch = REDDIT_SUBREDDITS[i : i + REDDIT_BATCH_SIZE]
                futures = {executor.submit(_fetch_subreddit, name): name for name in batch}
                for future in as_completed(futures):
                    posts.extend(future.result())

        posts.sort(key=lambda x: x["score"], reverse=True)
        return posts[:limit]

    except Exception as e:
        return [{"message": f"Error fetching Reddit posts for {symbol}: {e!s}"}]


def get_top_comments(post: Submission, limit: int = 3) -> list[dict[str, Any]]:
    """Fetches top comments from a post."""
    post.comments.replace_more(limit=0)
    return [
        {
            "author": str(getattr(comment, "author", "")),
            "body": _truncate_text(getattr(comment, "body", ""), 500),
            "score": getattr(comment, "score", 0),
        }
        for comment in post.comments.list()[:limit]
    ]
