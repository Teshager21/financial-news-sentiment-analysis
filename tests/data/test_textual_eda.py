import pandas as pd
import pytest

from eda.textual_eda import (
    TextualEDA,
)  # Adjust this import according to your project structure


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "headline": ["News A", "Breaking B", "Update C"],
            "source": ["Source1", "Source2", "Source1"],
            "date": ["2025-06-01", "2025-06-02", "2025-06-02"],
        }
    )


def test_init_with_non_dataframe():
    with pytest.raises(TypeError):
        TextualEDA("not a dataframe")


def test_headline_length_stats(sample_df):
    eda = TextualEDA(sample_df)
    stats = eda.headline_length_stats()
    assert "count" in stats.index
    assert stats["count"] == len(sample_df)
    assert stats["min"] == min(len(h) for h in sample_df["headline"])
    assert stats["max"] == max(len(h) for h in sample_df["headline"])


def test_articles_per_publisher(sample_df):
    eda = TextualEDA(sample_df)
    counts = eda.articles_per_publisher()
    assert counts["Source1"] == 2
    assert counts["Source2"] == 1


def test_articles_per_publisher_missing_column():
    df = pd.DataFrame({"headline": ["A"], "sourcex": ["S"]})
    eda = TextualEDA(df, source_col="source")
    with pytest.raises(KeyError) as excinfo:
        eda.articles_per_publisher()
    assert "Column 'source' not found" in str(excinfo.value)
    assert "Did you mean 'sourcex'?" in str(excinfo.value)


def test_publication_trends(sample_df):
    eda = TextualEDA(sample_df)
    daily_counts, weekday_dist = eda.publication_trends()
    assert isinstance(daily_counts, pd.Series)
    assert isinstance(weekday_dist, pd.Series)
    # Check correct date count
    assert daily_counts[pd.to_datetime("2025-06-02").date()] == 2
    # Check weekdays are day names
    # Just check the index contains only valid weekday names (subset of possible weekdays)
    valid_days = {
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    }
    assert set(weekday_dist.index).issubset(valid_days)


def test_weekday_distribution(sample_df):
    eda = TextualEDA(sample_df)
    eda.publication_trends()  # Ensure date col is parsed
    weekdays = eda.weekday_distribution()
    assert weekdays.index.is_monotonic_increasing
    assert weekdays.sum() == len(sample_df)


def test_weekday_distribution_with_invalid_dates():
    df = pd.DataFrame({"headline": ["A"], "source": ["S"], "date": ["invalid-date"]})
    eda = TextualEDA(df)
    # publication_trends drops invalid dates so no error
    eda.publication_trends()
    with pytest.raises(ValueError):
        eda.weekday_distribution()
