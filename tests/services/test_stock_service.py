import pandas as pd
import pytest

from pytest_mock import MockerFixture

from stock_analysis_mcp.services.stock_service import get_data, get_macd, get_reddit_stock_news, get_rsi


@pytest.fixture
def mock_df() -> pd.DataFrame:
    return pd.DataFrame(
        {"Date": ["2023-01-01", "2023-01-02"], "Open": [100.0, 101.0], "High": [105.0, 106.0], "Low": [95.0, 96.0], "Close": [102.0, 103.0], "Adj_Close": [102.0, 103.0], "Volume": [1000, 1100]}
    )


def test_get_data_empty(mocker: MockerFixture) -> None:
    # Mock yfinance to return empty DF
    mocker.patch("yfinance.download", return_value=pd.DataFrame())
    df = get_data("AAPL", "2023-01-01", "2023-01-02")
    assert df.empty


def test_get_data_success(mocker: MockerFixture, mock_df: pd.DataFrame) -> None:
    mocker.patch("yfinance.download", return_value=mock_df)
    # Mock os.makedirs and df.to_csv to avoid file I/O
    mocker.patch("os.makedirs")
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("pandas.DataFrame.to_csv")

    df = get_data("AAPL", "2023-01-01", "2023-01-02")
    assert not df.empty
    assert "Close" in df.columns
    assert len(df) == 2


def test_get_data_exception(mocker: MockerFixture) -> None:
    mocker.patch("yfinance.download", side_effect=Exception("API Error"))
    # Mock os.makedirs and os.path.exists to reach the yf.download call
    mocker.patch("os.makedirs")
    mocker.patch("os.path.exists", return_value=False)

    df = get_data("AAPL", "2023-01-01", "2023-01-02")
    assert df.empty


def test_get_macd(mocker: MockerFixture, mock_df: pd.DataFrame) -> None:
    mocker.patch("stock_analysis_mcp.services.stock_service.get_data", return_value=mock_df)
    # Mock macd function from ta
    mocker.patch("stock_analysis_mcp.services.stock_service.macd", return_value=pd.Series([1.0, 1.1]))

    res = get_macd("AAPL", "2023-01-01", "2023-01-02")
    assert len(res) == 2
    assert res == [1.0, 1.1]


def test_get_rsi(mocker: MockerFixture, mock_df: pd.DataFrame) -> None:
    mocker.patch("stock_analysis_mcp.services.stock_service.get_data", return_value=mock_df)
    mocker.patch("stock_analysis_mcp.services.stock_service.rsi", return_value=pd.Series([50.0, 55.0]))

    res = get_rsi("AAPL", "2023-01-01", "2023-01-02")
    assert len(res) == 2
    assert res == [50.0, 55.0]


from unittest.mock import MagicMock

def test_get_reddit_stock_news_success(mocker: MockerFixture) -> None:
    # Setup mock posts
    mock_post1 = MagicMock()
    mock_post1.title = "Post 1"
    mock_post1.selftext = "Content 1"
    mock_post1.permalink = "/r/test/comments/123/post_1"
    mock_post1.score = 100
    mock_post1.created_utc = 1600000000.0
    mock_post1.num_comments = 1
    mock_post1.link_flair_text = "News"

    mock_post2 = MagicMock()
    mock_post2.title = "Post 2"
    mock_post2.selftext = "Content 2" * 100  # to test > 500 length
    mock_post2.permalink = "/r/test/comments/124/post_2"
    mock_post2.score = 50
    mock_post2.created_utc = 1600000001.0
    mock_post2.num_comments = 0
    mock_post2.link_flair_text = None

    # Setup mock Reddit instance
    mock_reddit_instance = MagicMock()
    mock_subreddit = MagicMock()
    mock_subreddit.search.return_value = [mock_post1, mock_post2]
    mock_reddit_instance.subreddit.return_value = mock_subreddit

    mocker.patch("praw.Reddit", return_value=mock_reddit_instance)

    mocker.patch(
        "stock_analysis_mcp.services.stock_service.get_top_comments",
        return_value=[{"author": "user1", "body": "comment 1", "score": 10}]
    )

    mocker.patch("stock_analysis_mcp.services.stock_service.REDDIT_SUBREDDITS", ["TestSubreddit"])

    res = get_reddit_stock_news("AAPL")

    assert len(res) == 2
    # Ensure sorted by score
    assert res[0]["title"] == "Post 1"
    assert res[0]["score"] == 100
    assert res[0]["subreddit"] == "TestSubreddit"
    assert res[0]["flair"] == "News"
    assert len(res[0]["comments"]) == 1
    assert res[0]["comments"][0]["author"] == "user1"

    assert res[1]["title"] == "Post 2"
    assert res[1]["score"] == 50
    assert res[1]["flair"] == "None"
    assert len(res[1]["content"]) == 503  # 500 chars + "..."
    assert res[1]["content"].endswith("...")


def test_get_reddit_stock_news_fetch_subreddit_exception(mocker: MockerFixture) -> None:
    # Setup mock post for the successful subreddit
    mock_post = MagicMock()
    mock_post.title = "Good Post"
    mock_post.selftext = "Content"
    mock_post.permalink = "/r/good/comments/123/good"
    mock_post.score = 100
    mock_post.created_utc = 1600000000.0
    mock_post.num_comments = 0
    mock_post.link_flair_text = None

    # Setup mock Reddit instance
    mock_reddit_instance = MagicMock()

    # We want one subreddit to work, and another to fail
    def mock_subreddit_func(subreddit_name: str) -> MagicMock:
        mock_sub = MagicMock()
        if subreddit_name == "FailSubreddit":
            mock_sub.search.side_effect = Exception("Mocked search error")
        else:
            mock_sub.search.return_value = [mock_post]
        return mock_sub

    mock_reddit_instance.subreddit.side_effect = mock_subreddit_func

    mocker.patch("praw.Reddit", return_value=mock_reddit_instance)

    mocker.patch(
        "stock_analysis_mcp.services.stock_service.get_top_comments",
        return_value=[]
    )

    # Use two subreddits: one succeeds, one fails
    mocker.patch(
        "stock_analysis_mcp.services.stock_service.REDDIT_SUBREDDITS",
        ["GoodSubreddit", "FailSubreddit"]
    )

    res = get_reddit_stock_news("AAPL")

    # The result should contain the post from GoodSubreddit
    assert len(res) == 1
    assert res[0]["title"] == "Good Post"
    assert res[0]["subreddit"] == "GoodSubreddit"


def test_get_reddit_stock_news_exception(mocker: MockerFixture) -> None:
    # Mock praw.Reddit to raise an exception
    mocker.patch("praw.Reddit", side_effect=Exception("Mocked error"))

    res = get_reddit_stock_news("AAPL")

    assert len(res) == 1
    assert res[0]["message"] == "Error fetching Reddit posts for AAPL: Mocked error"
