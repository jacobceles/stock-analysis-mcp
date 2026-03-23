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


def test_get_reddit_stock_news_exception(mocker: MockerFixture) -> None:
    # Mock praw.Reddit to raise an exception
    mocker.patch("praw.Reddit", side_effect=Exception("Mocked error"))

    res = get_reddit_stock_news("AAPL")

    assert len(res) == 1
    assert res[0]["message"] == "Error fetching Reddit posts for AAPL: Mocked error"


def test_get_top_comments_success(mocker: MockerFixture) -> None:
    from stock_analysis_mcp.services.stock_service import get_top_comments

    mock_submission = mocker.MagicMock()
    mock_comment1 = mocker.MagicMock()
    mock_comment1.author = "Author 1"
    mock_comment1.body = "Comment 1"
    mock_comment1.score = 10
    mock_comment2 = mocker.MagicMock()
    mock_comment2.author = "Author 2"
    mock_comment2.body = "Comment 2"
    mock_comment2.score = 20

    mock_comments_list = [mock_comment1, mock_comment2]
    # In python magicmock len() is 0 by default. So we need to mock __len__
    mock_submission.comments.__len__.return_value = len(mock_comments_list)
    mock_submission.comments.__getitem__.side_effect = lambda i: mock_comments_list[i]
    mock_submission.comments.replace_more = mocker.MagicMock()

    comments = get_top_comments(mock_submission, limit=1)

    mock_submission.comments.replace_more.assert_called_once_with(limit=0)
    assert len(comments) == 1
    assert comments[0]["body"] == "Comment 1"
    assert comments[0]["score"] == 10


def test_get_top_comments_exceeds_limit(mocker: MockerFixture) -> None:
    from stock_analysis_mcp.services.stock_service import get_top_comments

    mock_submission = mocker.MagicMock()
    mock_comment1 = mocker.MagicMock()
    mock_comment1.author = "Author 1"
    mock_comment1.body = "Comment 1"
    mock_comment1.score = 10

    mock_comments_list = [mock_comment1]
    mock_submission.comments.__len__.return_value = len(mock_comments_list)
    mock_submission.comments.__getitem__.side_effect = lambda i: mock_comments_list[i]
    mock_submission.comments.replace_more = mocker.MagicMock()

    comments = get_top_comments(mock_submission, limit=3)

    mock_submission.comments.replace_more.assert_called_once_with(limit=0)
    assert len(comments) == 1
    assert comments[0]["body"] == "Comment 1"
    assert comments[0]["score"] == 10


def test_get_top_comments_empty(mocker: MockerFixture) -> None:
    from stock_analysis_mcp.services.stock_service import get_top_comments

    mock_submission = mocker.MagicMock()

    mock_comments_list = []
    mock_submission.comments.__len__.return_value = len(mock_comments_list)
    mock_submission.comments.__getitem__.side_effect = lambda i: mock_comments_list[i]
    mock_submission.comments.replace_more = mocker.MagicMock()

    comments = get_top_comments(mock_submission, limit=3)

    mock_submission.comments.replace_more.assert_called_once_with(limit=0)
    assert len(comments) == 0
