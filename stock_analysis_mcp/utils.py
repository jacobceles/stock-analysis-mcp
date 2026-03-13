import logging
import os

from typing import Any

import pandas as pd
import praw  # type: ignore

from praw.models import Submission  # type: ignore
from ta.momentum import roc, rsi, stoch, tsi  # type: ignore
from ta.trend import adx, aroon_down, aroon_up, ema_indicator, ichimoku_a, ichimoku_b, macd, psar_down, psar_up  # type: ignore
from ta.volume import chaikin_money_flow, on_balance_volume, volume_weighted_average_price  # type: ignore

from stock_analysis_mcp.constants import (
    DUMP_DIR,
    REDDIT_POST_LIMIT,
    REDDIT_SUBREDDITS,
)
from stock_analysis_mcp.logging_config import setup_logging
from stock_analysis_mcp.nse_client import default_client

setup_logging()
logger = logging.getLogger(__name__)


def get_equity_metadata(symbol: str) -> dict:
    # Use the default client to fetch metadata
    response_json = default_client.get_metadata(symbol)
    return response_json.get("metadata", {})


def get_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    os.makedirs(DUMP_DIR, exist_ok=True)
    files = os.listdir(DUMP_DIR)
    file_name = f"{symbol}_{start_date}_{end_date}.csv"
    if file_name in files:
        file_path = os.path.join(DUMP_DIR, file_name)
        df = pd.read_csv(file_path)
    else:
        response = default_client.get_historical(symbol, start_date, end_date)
        merged_data = []
        merged_data.extend(response)
        df = pd.DataFrame(merged_data)
        file_name = f"{symbol}_{start_date}_{end_date}.csv"
        file_path = os.path.join(DUMP_DIR, file_name)
        df.to_csv(file_path, index=False)
    return df


def get_macd(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return macd(df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_rsi(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return rsi(df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_tsi(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return tsi(df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_stoch(symbol: str, start_date: str, end_date: str, window: int, smooth_window: int) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return stoch(
        df.CH_TRADE_HIGH_PRICE,
        df.CH_TRADE_LOW_PRICE,
        df.CH_CLOSING_PRICE,
        window,
        smooth_window,
        fillna=True,
    ).tolist()


def get_roc(symbol: str, start_date: str, end_date: str, window: int) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return roc(df.CH_CLOSING_PRICE, window, fillna=True).tolist()


def get_ema(symbol: str, start_date: str, end_date: str, window: int) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return ema_indicator(df.CH_CLOSING_PRICE, window, fillna=True).tolist()


def get_ichimoku_a(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return ichimoku_a(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, fillna=True).tolist()


def get_ichimoku_b(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return ichimoku_b(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, fillna=True).tolist()


def get_adx(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return adx(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_psar_up(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return psar_up(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_psar_down(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return psar_down(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_aroon_up(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return aroon_up(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, df.CH_CLOSING_PRICE, fillna=True).tolist()


def get_aroon_down(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return aroon_down(df.CH_TRADE_HIGH_PRICE, df.CH_TRADE_LOW_PRICE, df.CH_CLOSING_PRICE, fillna=True).tolist()


# Volume based metrics - On-Balance Volume (OBV), Chaikin Money Flow (CMF), Volume Weighted Average Price (VWAP)


def get_on_balance_volume(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return on_balance_volume(df.CH_CLOSING_PRICE, df.CH_TOT_TRADED_QTY, fillna=True).tolist()


def get_chaikin_money_flow(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return chaikin_money_flow(
        df.CH_TRADE_HIGH_PRICE,
        df.CH_TRADE_LOW_PRICE,
        df.CH_CLOSING_PRICE,
        df.CH_TOT_TRADED_QTY,
        fillna=True,
    ).tolist()


def get_volume_weighted_average_price(symbol: str, start_date: str, end_date: str) -> list[float]:
    df = get_data(symbol, start_date, end_date)
    return volume_weighted_average_price(
        df.CH_TRADE_HIGH_PRICE,
        df.CH_TRADE_LOW_PRICE,
        df.CH_CLOSING_PRICE,
        df.CH_TOT_TRADED_QTY,
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

        for subreddit_name in REDDIT_SUBREDDITS:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                search_results = subreddit.search(search_query, limit=limit, time_filter=time_filter)

                for post in search_results:
                    comments = get_top_comments(post, 5)
                    posts.append(
                        {
                            "title": post.title,
                            "content": post.selftext[:500] + "..." if len(post.selftext) > 500 else post.selftext,
                            "url": f"https://reddit.com{post.permalink}",
                            "score": post.score,
                            "subreddit": subreddit_name,
                            "created_utc": post.created_utc,
                            "num_comments": post.num_comments,
                            "comments": comments,
                            "flair": post.link_flair_text if post.link_flair_text else "None",
                        }
                    )
            except Exception as e:
                logger.warning("Error fetching Reddit posts for %s: %s", symbol, e)
                continue

        posts.sort(key=lambda x: x["score"], reverse=True)
        return posts[:limit]

    except Exception as e:
        return [
            {
                "message": f"Error fetching Reddit posts for {symbol}: {e!s}",
            }
        ]


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
