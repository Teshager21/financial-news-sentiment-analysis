from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from utils.ticker_analyzer import TickerAnalyzer  # Replace with actual path


@pytest.fixture
def analyzer():
    return TickerAnalyzer("AAPL")


@patch("yfinance.download")
def test_load_price_data_success(mock_download, analyzer):
    mock_df = pd.DataFrame(
        {
            "Date": pd.date_range(start="2024-01-01", periods=5),
            "Open": np.random.rand(5),
            "High": np.random.rand(5),
            "Low": np.random.rand(5),
            "Close": np.random.rand(5),
            "Volume": np.random.randint(100, 1000, size=5),
        }
    ).set_index("Date")

    mock_download.return_value = mock_df

    df = analyzer.load_price_data()
    assert isinstance(df, pd.DataFrame)
    assert "Date" in df.columns
    assert not df.empty


def test_analyze_sentiment_success(analyzer):
    news = pd.DataFrame(
        {
            "headline": ["Markets rally", "Recession fears", "Mixed earnings"],
            "date": pd.date_range(start="2024-01-01", periods=3),
        }
    )
    result = analyzer.analyze_sentiment(news)
    assert "sentiment" in result.columns
    assert len(result) == 3


def test_analyze_sentiment_invalid_input(analyzer):
    with pytest.raises(ValueError, match="must contain 'headline' and 'date'"):
        analyzer.analyze_sentiment(pd.DataFrame({"title": ["Missing headline"]}))


def test_merge_price_and_sentiment_success(analyzer):
    analyzer.price_df = pd.DataFrame(
        {"Date": pd.date_range("2024-01-01", periods=3), "Close": [100, 102, 101]}
    )

    analyzer.sentiment_df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "headline": ["Good", "Bad", "Neutral"],
            "sentiment": [0.5, -0.5, 0.0],
        }
    )

    merged = analyzer.merge_price_and_sentiment()
    assert "sentiment" in merged.columns
    assert len(merged) == 3


def test_compute_financial_metrics(analyzer):
    analyzer.price_df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=10),
            "Close": np.linspace(100, 110, 10),
        }
    )

    metrics = analyzer.compute_financial_metrics()
    assert isinstance(metrics, dict)
    assert "Sharpe Ratio" in metrics
    assert isinstance(metrics["Sharpe Ratio"], float)


def test_load_price_data_from_csv_invalid(analyzer):
    with pytest.raises(FileNotFoundError):
        analyzer.load_price_data_from_csv("nonexistent.csv")


def test_load_price_data_from_csv_success(tmp_path, analyzer):
    file_path = tmp_path / "sample.csv"
    df = pd.DataFrame(
        {"my_date": pd.date_range("2024-01-01", periods=5), "Close": np.random.rand(5)}
    )
    df.to_csv(file_path, index=False)

    result = analyzer.load_price_data_from_csv(str(file_path), date_col="my_date")
    assert "Date" in result.columns
    assert len(result) == 5
