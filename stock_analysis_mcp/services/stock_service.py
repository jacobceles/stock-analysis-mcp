import functools
import logging
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pandas as pd
import praw  # type: ignore
import yfinance as yf  # type: ignore

from praw.models import Submission  # type: ignore
from ta.momentum import roc, rsi, stoch, tsi  # type: ignore
from ta.trend import adx, aroon_down, aroon_up, ema_indicator, ichimoku_a, ichimoku_b, macd, psar_down, psar_up  # type: ignore
from ta.volume import chaikin_money_flow, on_balance_volume, volume_weighted_average_price  # type: ignore

from stock_analysis_mcp.core.constants import (
    DUMP_DIR,
    REDDIT_BATCH_SIZE,
    REDDIT_COMMENT_BATCH_SIZE,
    REDDIT_POST_LIMIT,
    REDDIT_SUBREDDITS,
)
from stock_analysis_mcp.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_equity_metadata(symbol: str) -> dict:
    """Fetches metadata for a given symbol using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except Exception as e:
        logger.error("Error fetching metadata for %s: %s", symbol, e)
        return {}


@functools.lru_cache(maxsize=32)
def _get_data_internal(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Internal function to fetch historical price data and cache it in memory."""
    os.makedirs(DUMP_DIR, exist_ok=True)
    file_name = f"{symbol}_{start_date}_{end_date}.csv"
    file_path = os.path.join(DUMP_DIR, file_name)

    if os.path.exists(file_path):
        return pd.read_csv(file_path)

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

        # Normalize column names
        df = df.rename(
            columns={
                "Date": "Date",
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Adj Close": "Adj_Close",
                "Volume": "Volume",
            }
        )

        df.to_csv(file_path, index=False)
        return df

    except Exception as e:
        logger.error("Error fetching data for %s: %s", symbol, e)
        return pd.DataFrame()


def get_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetches historical price data for a given symbol using yfinance and caches it."""
    return _get_data_internal(symbol, start_date, end_date).copy()


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
    return psar_up(df.High, df.Low, df.Close, fillna=True).tolist()


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


def get_reddit_stock_news(symbol: str, time_filter: str = "month") -> list[dict]:
    try:
        reddit_client_id = os.environ.get("REDDIT_CLIENT_ID")
        reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
        reddit_user_agent = os.environ.get("REDDIT_USER_AGENT", "stock-analysis-mcp/1.0")
        limit = REDDIT_POST_LIMIT

        reddit = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret, user_agent=reddit_user_agent)

        posts = []
        search_query = f"{symbol} OR '${symbol}'"

        def _fetch_subreddit(subreddit_name: str) -> list[dict]:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                search_results = list(subreddit.search(search_query, limit=limit, time_filter=time_filter))

                # Fetch comments in parallel batches
                post_comments: dict[int, list[dict]] = {}
                for i in range(0, len(search_results), REDDIT_COMMENT_BATCH_SIZE):
                    batch = search_results[i : i + REDDIT_COMMENT_BATCH_SIZE]
                    with ThreadPoolExecutor(max_workers=REDDIT_COMMENT_BATCH_SIZE) as comment_executor:
                        future_to_idx = {comment_executor.submit(get_top_comments, post, 5): i + j for j, post in enumerate(batch)}
                        for future in as_completed(future_to_idx):
                            post_comments[future_to_idx[future]] = future.result()

                results = []
                for idx, post in enumerate(search_results):
                    results.append(
                        {
                            "title": post.title,
                            "content": post.selftext[:500] + "..." if len(post.selftext) > 500 else post.selftext,
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

        batch_size = min(REDDIT_BATCH_SIZE, len(REDDIT_SUBREDDITS))
        for i in range(0, len(REDDIT_SUBREDDITS), batch_size):
            batch = REDDIT_SUBREDDITS[i : i + batch_size]
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = {executor.submit(_fetch_subreddit, name): name for name in batch}
                for future in as_completed(futures):
                    posts.extend(future.result())

        posts.sort(key=lambda x: x["score"], reverse=True)
        return posts[:limit]

    except Exception as e:
        return [{"message": f"Error fetching Reddit posts for {symbol}: {e!s}"}]


def get_top_comments(post: Submission, limit: int = 3) -> list[dict[str, Any]]:
    """Fetches top comments from a post."""
    comments: list[dict[str, Any]] = []
    post.comments.replace_more(limit=0)
    for i in range(min(limit, len(post.comments))):
        comment = post.comments[i]
        comments.append(
            {
                "author": str(comment.author),
                "body": comment.body[:500] + "..." if len(comment.body) > 500 else comment.body,
                "score": comment.score,
            }
        )
    return comments
