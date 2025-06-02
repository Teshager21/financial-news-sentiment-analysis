# src/eda/visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class DataVisualizer:
    def __init__(
        self,
        df: pd.DataFrame,
        headline_col: str = "headline",
        publisher_col: str = "publisher",
        date_col: str = "date",
    ):
        self.df = df.copy()
        self.headline_col = headline_col
        self.publisher_col = publisher_col
        self.date_col = date_col

    def plot_headline_length_distribution(self, bins: int = 30):
        """
        Visualizes distribution of headline lengths with histogram
        and prints summary stats.
        """
        if self.headline_col not in self.df.columns:
            raise KeyError(f"Column '{self.headline_col}' not found in DataFrame.")

        lengths = self.df[self.headline_col].dropna().astype(str).apply(len)

        print("Headline Length Statistics:")
        print(lengths.describe())

        plt.figure(figsize=(10, 6))
        sns.histplot(lengths, bins=bins, kde=True, color="skyblue")
        plt.title("Headline Length Distribution")
        plt.xlabel("Headline Length (characters)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()

    def plot_articles_per_publisher(self, top_n: int = 20):
        """
        Bar plot of article counts per publisher (top_n publishers).
        """
        if self.publisher_col not in self.df.columns:
            raise KeyError(f"Column '{self.publisher_col}' not found in DataFrame.")

        counts = self.df[self.publisher_col].value_counts().head(top_n)

        plt.figure(figsize=(12, 6))
        sns.barplot(x=counts.values, y=counts.index, palette="viridis")
        plt.title(f"Top {top_n} Publishers by Article Count")
        plt.xlabel("Number of Articles")
        plt.ylabel("Publisher")
        plt.tight_layout()
        plt.show()

    def plot_weekday_distribution(self):
        """
        Bar plot of article counts by weekday from the date column.
        Assumes date column is already converted to datetime.
        """
        if self.date_col not in self.df.columns:
            raise KeyError(f"Column '{self.date_col}' not found in DataFrame.")

        if not pd.api.types.is_datetime64_any_dtype(self.df[self.date_col]):
            raise TypeError(f"Column '{self.date_col}' must be datetime dtype.")

        weekdays = self.df[self.date_col].dt.day_name()
        counts = (
            weekdays.value_counts()
            .reindex(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
            )
            .fillna(0)
        )

        plt.figure(figsize=(10, 5))
        sns.barplot(x=counts.index, y=counts.values, palette="magma")
        plt.title("Article Count by Weekday")
        plt.xlabel("Weekday")
        plt.ylabel("Number of Articles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
