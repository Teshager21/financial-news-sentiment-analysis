"""
Ticker Analysis Module
------------------------
Performs loading, sentiment analysis, technical indicator computation,
and visualization for a given stock ticker and related news data.

Author: [Your Name]
Date: 2025-06-03
"""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import pynance as pn  # Add this import for financial metrics
import yfinance as yf
from ta import add_all_ta_features
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class TickerAnalyzer:
    """
    A class to perform sentiment analysis, technical indicator extraction,
    and visualization for a given stock ticker.
    """

    def __init__(self, ticker: str, period: str = "6mo", interval: str = "1d"):
        """
        Initializes the TickerAnalyzer.

        Args:
            ticker (str): The stock ticker symbol.
            period (str): Period of historical data (e.g. '1y', '6mo').
            interval (str): Data interval (e.g. '1d', '1h').
        """
        self.ticker = ticker.upper()
        self.period = period
        self.interval = interval
        self.analyzer = SentimentIntensityAnalyzer()
        self.price_df: Optional[pd.DataFrame] = None
        self.sentiment_df: Optional[pd.DataFrame] = None
        self.merged_df: Optional[pd.DataFrame] = None

    def load_price_data(self) -> pd.DataFrame:
        """Loads historical stock price data."""
        try:
            df = yf.download(self.ticker, period=self.period, interval=self.interval)
            df.reset_index(inplace=True)
            self.price_df = df
            return df
        except Exception as e:
            raise RuntimeError(f"Failed to load price data for {self.ticker}: {e}")

    def add_technical_indicators(self) -> pd.DataFrame:
        """Adds technical indicators to the stock price data."""
        if self.price_df is None:
            raise ValueError("Price data not loaded. Run load_price_data() first.")

        try:
            df = add_all_ta_features(
                self.price_df.copy(),
                open="Open",
                high="High",
                low="Low",
                close="Close",
                volume="Volume",
            )
            self.price_df = df
            return df
        except Exception as e:
            raise RuntimeError(f"Failed to add technical indicators: {e}")

    def analyze_sentiment(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes sentiment in news headlines.

        Args:
            news_df (pd.DataFrame): News data with 'headline' and 'date' columns.
        """
        if "headline" not in news_df.columns or "date" not in news_df.columns:
            raise ValueError("news_df must contain 'headline' and 'date' columns.")

        try:
            news_df["sentiment"] = news_df["headline"].apply(
                lambda text: self.analyzer.polarity_scores(text)["compound"]
            )
            self.sentiment_df = news_df
            return news_df
        except Exception as e:
            raise RuntimeError(f"Sentiment analysis failed: {e}")

    def merge_price_and_sentiment(self) -> pd.DataFrame:
        """Merges price data with sentiment scores based on date."""
        if self.price_df is None or self.sentiment_df is None:
            raise ValueError("Ensure both price data and sentiment data are loaded.")

        try:
            sentiment_df = self.sentiment_df.copy()
            sentiment_df["Date"] = pd.to_datetime(sentiment_df["date"]).dt.date
            price_df = self.price_df.copy()
            price_df["Date"] = pd.to_datetime(price_df["Date"]).dt.date

            merged_df = pd.merge(price_df, sentiment_df, on="Date", how="left")
            self.merged_df = merged_df
            return merged_df
        except Exception as e:
            raise RuntimeError(f"Failed to merge data: {e}")

    def plot_price_and_sentiment(self) -> None:
        """Plots stock closing price and sentiment score over time."""
        if self.merged_df is None:
            raise ValueError(
                "Merged data not available. Run merge_price_and_sentiment() first."
            )

        try:
            df = self.merged_df.copy()

            fig, ax1 = plt.subplots(figsize=(12, 6))

            ax1.plot(df["Date"], df["Close"], color="blue", label="Close Price")
            ax1.set_ylabel("Close Price", color="blue")
            ax1.tick_params(axis="y", labelcolor="blue")

            ax2 = ax1.twinx()
            ax2.plot(
                df["Date"], df["sentiment"], color="red", alpha=0.5, label="Sentiment"
            )
            ax2.set_ylabel("Sentiment Score", color="red")
            ax2.tick_params(axis="y", labelcolor="red")

            plt.title(f"{self.ticker} Price vs News Sentiment")
            fig.tight_layout()
            fig.legend(loc="upper left")
            plt.show()
        except Exception as e:
            raise RuntimeError(f"Failed to generate plot: {e}")

    def load_price_data_from_csv(
        self, filepath: str, date_col: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Loads historical stock price data from a local CSV file.

        Args:
            filepath (str): Path to the CSV file containing price data.
            date_col (str, optional): Name of the date column to parse.
                                    If None, attempts to auto-detect.

        Returns:
            pd.DataFrame: The loaded price dataframe.
        """
        try:
            df = pd.read_csv(filepath)

            # Auto-detect date column if not provided
            if date_col is None:
                date_candidates = [
                    col
                    for col in df.columns
                    if "date" in col.lower() or "time" in col.lower()
                ]
                if not date_candidates:
                    raise ValueError(
                        "No date-like column found. Please specify `date_col` manually."
                    )
                date_col = date_candidates[0]

            df[date_col] = pd.to_datetime(df[date_col])
            df.sort_values(by=date_col, inplace=True)
            df.reset_index(drop=True, inplace=True)

            df.rename(columns={date_col: "Date"}, inplace=True)
            self.price_df = df
            return df

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except ValueError as e:
            raise ValueError(f"CSV column issue: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load price data from CSV: {e}")

    def plot_indicators(self, indicators=None):
        """
        Plot selected technical indicators along with closing price.

        :param indicators: List of indicator column names to plot.
                           If None, plot default indicators ['momentum_rsi', 'trend_macd']
        """
        if indicators is None:
            indicators = ["momentum_rsi", "trend_macd"]

        plt.figure(figsize=(14, 8))

        # Plot Closing Price on top subplot
        plt.subplot(len(indicators) + 1, 1, 1)
        plt.plot(
            self.price_df["Date"],
            self.price_df["Close"],
            label="Close Price",
            color="blue",
        )
        plt.title("Close Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)

        # Plot each indicator on separate subplot
        for i, indicator in enumerate(indicators, start=2):
            if indicator in self.price_df.columns:
                plt.subplot(len(indicators) + 1, 1, i)
                plt.plot(
                    self.price_df["Date"],
                    self.price_df[indicator],
                    label=indicator,
                    color="orange",
                )
                plt.title(indicator)
                plt.xlabel("Date")
                plt.grid(True)
            else:
                print(f"Warning: Indicator '{indicator}' not found in data.")

        plt.tight_layout()
        plt.show()

    def compute_financial_metrics(self, risk_free_rate=0.02):
        if self.price_df is None or self.price_df.empty:
            raise ValueError("Price data not loaded. Run load_price_data() first.")

        df = self.price_df.copy()

        # Normalize column names to lowercase
        df.columns = [col.lower() for col in df.columns]

        # Ensure required 'close' column exists
        if "close" not in df.columns:
            raise ValueError("Expected 'close' column not found in price data.")

        # Drop rows with missing close values
        df = df[["close"]].copy()
        df.dropna(inplace=True)

        # Compute daily return
        df["daily_return"] = df["close"].pct_change()
        df.dropna(inplace=True)

        if df.empty or len(df) < 2:
            raise ValueError(
                f"Not enough data to compute financial metrics. Available rows: {len(df)}"
            )

        # Financial metrics
        cumulative_return = (df["close"].iloc[-1] / df["close"].iloc[0]) - 1
        annualized_volatility = df["daily_return"].std() * np.sqrt(252)
        sharpe_ratio = (
            df["daily_return"].mean() * 252 - risk_free_rate
        ) / annualized_volatility
        max_drawdown = ((df["close"] / df["close"].cummax()) - 1).min()
        calmar_ratio = (
            cumulative_return / abs(max_drawdown) if max_drawdown != 0 else np.nan
        )

        return {
            "Cumulative Return": cumulative_return,
            "Annualized Volatility": annualized_volatility,
            "Sharpe Ratio": sharpe_ratio,
            "Max Drawdown": max_drawdown,
            "Calmar Ratio": calmar_ratio,
        }

    def plot_price_and_indicators(self, indicators=None):
        """
        Plot closing price and selected technical indicators.

        :param indicators: List of indicator column names to plot.
                           Defaults to ['momentum_rsi', 'trend_macd'].
        """
        if indicators is None:
            indicators = ["momentum_rsi", "trend_macd"]

        plt.figure(figsize=(15, 10))

        # Use Date column or index for x-axis
        x_axis = (
            self.price_df["Date"]
            if "Date" in self.price_df.columns
            else self.price_df.index
        )

        # Plot Close Price
        plt.subplot(len(indicators) + 1, 1, 1)
        plt.plot(x_axis, self.price_df["Close"], label="Close Price", color="blue")
        plt.title("Close Price")
        plt.ylabel("Price")
        plt.grid(True)

        # Plot each indicator
        for i, indicator in enumerate(indicators, start=2):
            if indicator in self.price_df.columns:
                plt.subplot(len(indicators) + 1, 1, i)
                plt.plot(
                    x_axis, self.price_df[indicator], label=indicator, color="green"
                )
                plt.title(indicator)
                plt.ylabel(indicator)
                plt.grid(True)
            else:
                print(f"Warning: Indicator '{indicator}' not found in price_df.")

        plt.tight_layout()
        plt.show()
