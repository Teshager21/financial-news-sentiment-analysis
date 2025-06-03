import pandas as pd
import pytest

from nlp.sentiment_analyzer import SentimentAnalyzer


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "text": ["Market is booming!", "Economy is crashing.", "", None],
            "publisher": ["A", "B", "A", "B"],
            "date": pd.date_range("2023-06-01", periods=4),
        }
    )


@pytest.fixture
def price_df():
    return pd.DataFrame(
        {
            "date": pd.date_range("2023-06-01", periods=4),
            "close_price": [100, 101, 99, 98],
        }
    )


def test_analyze_text_and_score_to_label():
    analyzer = SentimentAnalyzer()
    assert isinstance(analyzer.analyze_text("Good news"), float)
    assert analyzer.score_to_label(0.2) == "Positive"
    assert analyzer.score_to_label(-0.2) == "Negative"
    assert analyzer.score_to_label(0.01) == "Neutral"


def test_apply_to_dataframe(sample_df):
    analyzer = SentimentAnalyzer()
    result = analyzer.apply_to_dataframe(sample_df.copy())
    assert "sentiment_score" in result.columns
    assert "sentiment_label" in result.columns
    assert result["sentiment_label"].isin(["Positive", "Neutral", "Negative"]).all()


def test_plot_sentiment_distribution(sample_df):
    analyzer = SentimentAnalyzer()
    df_scored = analyzer.apply_to_dataframe(sample_df.copy())
    analyzer.plot_sentiment_distribution(df_scored)


def test_plot_sentiment_over_time(sample_df):
    analyzer = SentimentAnalyzer()
    df_scored = analyzer.apply_to_dataframe(sample_df.copy())
    analyzer.plot_sentiment_over_time(df_scored)

    # Should handle missing date_col
    df_missing = df_scored.drop(columns=["date"])
    analyzer.plot_sentiment_over_time(df_missing)


def test_plot_publisher_sentiment(sample_df):
    analyzer = SentimentAnalyzer()
    df_scored = analyzer.apply_to_dataframe(sample_df.copy())
    analyzer.plot_publisher_sentiment(df_scored)

    # Should handle missing publisher_col
    df_missing = df_scored.drop(columns=["publisher"])
    analyzer.plot_publisher_sentiment(df_missing)


def test_correlation_with_prices(sample_df, price_df):
    analyzer = SentimentAnalyzer()
    df_scored = analyzer.apply_to_dataframe(sample_df.copy())

    corr = analyzer.correlation_with_prices(df_scored, price_df)
    assert isinstance(corr, float)

    # Should raise error if date column missing
    with pytest.raises(ValueError):
        analyzer.correlation_with_prices(df_scored.drop(columns=["date"]), price_df)
    with pytest.raises(ValueError):
        analyzer.correlation_with_prices(df_scored, price_df.drop(columns=["date"]))
