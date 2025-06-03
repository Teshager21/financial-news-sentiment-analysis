import pandas as pd
import pytest

from src.eda.time_series_analyzer import TimeSeriesAnalyzer


def test_init_raises_keyerror_on_missing_date_col():
    df = pd.DataFrame({"not_date": [1, 2, 3]})
    with pytest.raises(KeyError):
        TimeSeriesAnalyzer(df, date_col="date")


def test_prepare_date_index_creates_datetime_index():
    data = {"date": ["2025-06-01", "2025-06-02", "invalid_date"], "val": [1, 2, 3]}
    df = pd.DataFrame(data)
    tsa = TimeSeriesAnalyzer(df, date_col="date")
    assert pd.api.types.is_datetime64_any_dtype(tsa.df.index)
    # The invalid date row should be dropped
    assert len(tsa.df) == 2


def test_get_publication_frequency_daily_and_weekly():
    dates = pd.date_range(start="2025-06-01", periods=10)
    df = pd.DataFrame({"date": dates, "val": range(10)})
    tsa = TimeSeriesAnalyzer(df)
    daily_counts = tsa.get_publication_frequency("D")
    assert daily_counts.sum() == 10
    weekly_counts = tsa.get_publication_frequency("W")
    assert weekly_counts.sum() == 10


def test_detect_spikes_returns_expected_dates():
    base_dates = [
        "2025-06-01",
        "2025-06-02",
        *["2025-06-03"] * 10,  # spike count = 10
        "2025-06-04",
        "2025-06-05",
    ]
    df = pd.DataFrame({"date": base_dates})
    tsa = TimeSeriesAnalyzer(df)

    series = tsa.get_publication_frequency()
    mean = series.mean()
    std = series.std()
    print(f"Mean: {mean}, Std: {std}")
    print(series)

    threshold = 1.5  # lower threshold to catch spikes easier
    spikes = tsa.detect_spikes(threshold=threshold)
    print(spikes)

    assert not spikes.empty, "No spikes detected but expected one."
    assert (
        pd.Timestamp("2025-06-03") in spikes["date"].values
    ), "Expected spike date not detected."


def test_plot_publication_trend_runs_without_error():
    dates = pd.date_range(start="2025-06-01", periods=5)
    df = pd.DataFrame({"date": dates, "val": range(5)})
    tsa = TimeSeriesAnalyzer(df)
    # Just call the plot function to check no exception is raised
    tsa.plot_publication_trend()
    tsa.plot_publication_trend(rolling=2)


def test_plot_spikes_runs_without_error():
    dates = pd.date_range(start="2025-06-01", periods=5)
    counts = [1, 1, 10, 1, 1]
    df = pd.DataFrame({"date": dates.repeat(counts), "val": range(sum(counts))})
    tsa = TimeSeriesAnalyzer(df)
    tsa.plot_spikes()
