# sentiment_analyzer.py

import matplotlib.pyplot as plt
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentAnalyzer:
    """
    Performs sentiment analysis on financial news headlines using VADER.
    """

    def __init__(
        self, text_col="text", score_col="sentiment_score", label_col="sentiment_label"
    ):
        """
        Initialize the sentiment analyzer.

        Parameters:
            text_col (str): Column containing the text to analyze.
            score_col (str): Column name to store compound sentiment score.
            label_col (str): Column name to store categorical sentiment label.
        """
        self.analyzer = SentimentIntensityAnalyzer()
        self.text_col = text_col
        self.score_col = score_col
        self.label_col = label_col

    def analyze_text(self, text):
        """
        Analyze a single text string and return the VADER compound score.

        Parameters:
            text (str): Input text.

        Returns:
            float: Compound sentiment score between -1 and 1.
        """
        return self.analyzer.polarity_scores(str(text))["compound"]

    def score_to_label(self, score):
        """
        Convert compound score to sentiment label.

        Parameters:
            score (float): VADER compound score.

        Returns:
            str: 'Positive', 'Neutral', or 'Negative'.
        """
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    def apply_to_dataframe(self, df):
        """
        Apply sentiment analysis to an entire DataFrame.

        Parameters:
            df (pd.DataFrame): Input DataFrame containing a text column.

        Returns:
            pd.DataFrame: Updated DataFrame with sentiment score and label columns.
        """
        df[self.score_col] = df[self.text_col].astype(str).apply(self.analyze_text)
        df[self.label_col] = df[self.score_col].apply(self.score_to_label)
        return df

    def plot_sentiment_distribution(self, df):
        """
        Plot bar chart of sentiment label counts.
        """
        sentiment_counts = df[self.label_col].value_counts()
        colors = {"Positive": "green", "Neutral": "grey", "Negative": "red"}
        sentiment_counts.plot(
            kind="bar", color=[colors.get(x, "blue") for x in sentiment_counts.index]
        )
        plt.title("Sentiment Distribution")
        plt.xlabel("Sentiment")
        plt.ylabel("Count")
        plt.show()

    def plot_sentiment_over_time(self, df, date_col="date"):
        """
        Plot average sentiment score over time.

        Args:
            df (pd.DataFrame): DataFrame containing a datetime column.
            date_col (str): Name of the datetime column.
        """
        if date_col not in df.columns:
            print(f"Column '{date_col}' not found in DataFrame.")
            return
        df[date_col] = pd.to_datetime(df[date_col])
        daily_sentiment = df.groupby(date_col)[self.score_col].mean()
        daily_sentiment.plot(figsize=(12, 6), marker="o")
        plt.title("Average Daily Sentiment Over Time")
        plt.xlabel("Date")
        plt.ylabel("Average Sentiment Score")
        plt.grid(True)
        plt.show()

    def plot_publisher_sentiment(self, df, publisher_col="publisher", top_n=10):
        """
        Plot average sentiment score for top N publishers.

        Args:
            df (pd.DataFrame): DataFrame containing publisher column.
            publisher_col (str): Name of publisher column.
            top_n (int): Number of top publishers to show.
        """
        if publisher_col not in df.columns:
            print(f"Column '{publisher_col}' not found in DataFrame.")
            return
        publisher_sentiment = (
            df.groupby(publisher_col)[self.score_col]
            .mean()
            .sort_values(ascending=False)
        )
        top_publishers = publisher_sentiment.head(top_n)
        top_publishers.plot(kind="bar", color="purple", figsize=(10, 5))
        plt.title(f"Top {top_n} Publishers by Average Sentiment Score")
        plt.xlabel("Publisher")
        plt.ylabel("Average Sentiment Score")
        plt.show()

    def correlation_with_prices(
        self, df, price_df, date_col="date", price_col="close_price"
    ):
        """
        Calculate correlation between average daily sentiment score and stock prices.

        Args:
            df (pd.DataFrame): DataFrame with sentiment and date columns.
            price_df (pd.DataFrame): DataFrame with stock prices.
            date_col (str): Date column name present in both DataFrames.
            price_col (str): Stock price column name in price_df.

        Returns:
            float: Pearson correlation coefficient.
        """
        if date_col not in df.columns or date_col not in price_df.columns:
            raise ValueError(
                f"Date column '{date_col}' missing from one or both DataFrames."
            )
        df[date_col] = pd.to_datetime(df[date_col])
        price_df[date_col] = pd.to_datetime(price_df[date_col])

        daily_sentiment = df.groupby(date_col)[self.score_col].mean().reset_index()
        merged = pd.merge(daily_sentiment, price_df[[date_col, price_col]], on=date_col)
        corr = merged[self.score_col].corr(merged[price_col])

        print(f"Correlation between sentiment and stock price: {corr:.3f}")
        return corr
