import difflib

import pandas as pd


class TextualEDA:
    def __init__(
        self,
        df: pd.DataFrame,
        headline_col: str = "headline",
        source_col: str = "source",
        date_col: str = "date",
    ):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        self.df = df.copy()
        self.headline_col = headline_col
        self.source_col = source_col
        self.date_col = date_col

    def headline_length_stats(self) -> pd.Series:
        """
        Compute basic statistics (count, mean, std, min, max, etc.)
        for headline lengths.
        """
        self.df["headline_length"] = self.df[self.headline_col].astype(str).str.len()
        return self.df["headline_length"].describe()

    def articles_per_publisher(self) -> pd.Series:
        """
        Count the number of articles per publisher,
        with a helpful suggestion if missing.
        """
        if self.source_col not in self.df.columns:
            suggestion = difflib.get_close_matches(
                self.source_col, self.df.columns, n=1
            )
            message = f"Column '{self.source_col}' not found."
            if suggestion:
                message += f" Did you mean '{suggestion[0]}'?"
            raise KeyError(message)
        return self.df[self.source_col].value_counts()

    def publication_trends(self) -> tuple[pd.Series, pd.Series]:
        """
        Analyze publication date trends.

        Returns:
            - Daily article count (by date)
            - Weekday distribution of articles
        """
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col], errors="coerce")
        self.df = self.df.dropna(subset=[self.date_col])

        daily_counts = self.df[self.date_col].dt.date.value_counts().sort_index()
        weekday_distribution = self.df[self.date_col].dt.day_name().value_counts()

        return daily_counts, weekday_distribution

    def weekday_distribution(self) -> pd.Series:
        """
        Return the number of articles published on each weekday.
        """
        if self.df[self.date_col].isna().all():
            raise ValueError(
                f"Column '{self.date_col}' could not be converted to datetime."
            )

        weekdays = self.df[self.date_col].dt.day_name()
        return weekdays.value_counts().sort_index(
            key=lambda x: pd.to_datetime(x, format="%A").dayofweek
        )
