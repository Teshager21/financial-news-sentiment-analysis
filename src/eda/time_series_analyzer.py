# src/eda/time_series_analyzer.py

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class TimeSeriesAnalyzer:
    def __init__(self, df: pd.DataFrame, date_col: str = "date"):
        if date_col not in df.columns:
            raise KeyError(f"Column '{date_col}' not found in DataFrame.")
        self.df = df.copy()
        self.date_col = date_col
        self._prepare_date_index()

    def _prepare_date_index(self):
        """Ensure datetime index for time series operations."""
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col], errors="coerce")
        self.df.dropna(subset=[self.date_col], inplace=True)
        self.df.set_index(self.date_col, inplace=True)

    def get_publication_frequency(self, freq: str = "D") -> pd.Series:
        """Return article counts aggregated by given frequency (e.g. 'D', 'W', 'M')."""
        return self.df.resample(freq).size()

    def plot_publication_trend(self, freq: str = "D", rolling: int | None = None):
        """Visualize publication trend with optional rolling average."""
        series = self.get_publication_frequency(freq)
        plt.figure(figsize=(14, 5))
        sns.lineplot(data=series, label="Raw Count")
        if rolling:
            sns.lineplot(
                data=series.rolling(rolling).mean(), label=f"{rolling}-period MA"
            )
        plt.title(f"Publication Frequency ({freq})")
        plt.xlabel("Date")
        plt.ylabel("Number of Articles")
        plt.tight_layout()
        plt.show()

    def detect_spikes(self, freq: str = "D", threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect dates with spike in article counts using standard deviation method.
        Returns DataFrame with spike dates and counts.
        """
        series = self.get_publication_frequency(freq)
        mean = series.mean()
        std = series.std()
        spike_dates = series[series > mean + threshold * std]
        return spike_dates.reset_index().rename(columns={0: "article_count"})

    def plot_spikes(self, freq: str = "D", threshold: float = 3.0):
        """Plot time series with spikes highlighted."""
        series = self.get_publication_frequency(freq)
        spikes = self.detect_spikes(freq, threshold).set_index(self.date_col)

        plt.figure(figsize=(14, 5))
        sns.lineplot(data=series, label="Article Count")
        plt.scatter(spikes.index, spikes["article_count"], color="red", label="Spikes")
        plt.title(f"Spikes in Article Frequency ({freq})")
        plt.xlabel("Date")
        plt.ylabel("Number of Articles")
        plt.legend()
        plt.tight_layout()
        plt.show()
