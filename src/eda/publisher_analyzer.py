import matplotlib.pyplot as plt
import seaborn as sns


class PublisherAnalyzer:
    """
    Analyzes publisher-related patterns in a news dataset,
    including frequency, domain patterns, and sentiment trends.
    """

    def __init__(self, df, publisher_col="publisher", sentiment_col="sentiment_score"):
        """
        Initialize the analyzer with dataset and column names.

        Parameters:
            df (pd.DataFrame): The input dataset.
            publisher_col (str): Column containing publisher identifiers.
            sentiment_col (str): Column containing sentiment scores (if available).
        """
        self.df = df.copy()
        self.publisher_col = publisher_col
        self.sentiment_col = sentiment_col
        self.results = {}

    def analyze_top_publishers(self, top_n=10, plot=True):
        """
        Analyze the top publishers by article count.

        Parameters:
            top_n (int): Number of top publishers to return.
            plot (bool): Whether to display a bar plot.

        Returns:
            pd.Series: Publisher counts for the top N publishers.
        """
        top_publishers = self.df[self.publisher_col].value_counts().head(top_n)
        self.results["top_publishers"] = top_publishers

        if plot:
            plt.figure(figsize=(8, 5))
            sns.barplot(
                x=top_publishers.values, y=top_publishers.index, palette="viridis"
            )
            plt.title("Top Publishers")
            plt.xlabel("Article Count")
            plt.tight_layout()
            plt.show()

        return top_publishers

    def analyze_domains(self, top_n=10, plot=True):
        """
        Extract and analyze domains from email-style publisher names.

        Parameters:
            top_n (int): Number of top domains to return.
            plot (bool): Whether to display a bar plot.

        Returns:
            pd.Series: Domain counts for the top N domains.
        """
        self.df["publisher_domain"] = self.df[self.publisher_col].str.extract(
            r"@([\w\.-]+)"
        )
        domain_counts = self.df["publisher_domain"].value_counts().head(top_n)
        self.results["domain_counts"] = domain_counts

        if plot:
            plt.figure(figsize=(8, 5))
            sns.barplot(
                x=domain_counts.values, y=domain_counts.index, palette="coolwarm"
            )
            plt.title("Top Publisher Domains (Emails)")
            plt.xlabel("Article Count")
            plt.tight_layout()
            plt.show()

        return domain_counts

    def analyze_sentiment_by_publisher(self, top_n=10, plot=True):
        """
        Analyze average sentiment scores by publisher.

        Parameters:
            top_n (int): Number of publishers to show.
            plot (bool): Whether to display a bar plot.

        Returns:
            pd.Series or None: Average sentiment scores by publisher, or None if column is missing.
        """
        if self.sentiment_col not in self.df.columns:
            print("⚠️ Sentiment column not found. Skipping sentiment analysis.")
            return None

        sentiment_by_pub = (
            self.df.groupby(self.publisher_col)[self.sentiment_col]
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
        )
        self.results["sentiment_by_publisher"] = sentiment_by_pub

        if plot:
            plt.figure(figsize=(8, 5))
            sns.barplot(
                x=sentiment_by_pub.values, y=sentiment_by_pub.index, palette="crest"
            )
            plt.title("Top Publishers by Average Sentiment")
            plt.xlabel("Avg Sentiment Score")
            plt.tight_layout()
            plt.show()

        return sentiment_by_pub

    def run_all(self, top_n=10, plot=True):
        """
        Run all analyses: top publishers, domain extraction, and sentiment scores.

        Parameters:
            top_n (int): Top N results to return from each analysis.
            plot (bool): Whether to display plots for each analysis.

        Returns:
            dict: Dictionary of results with keys:
                  - 'top_publishers'
                  - 'domain_counts'
                  - 'sentiment_by_publisher' (if sentiment column exists)
        """
        print("\n🔹 Analyzing Top Publishers...")
        self.analyze_top_publishers(top_n, plot)

        print("\n🔹 Analyzing Email Domains...")
        self.analyze_domains(top_n, plot)

        print("\n🔹 Analyzing Sentiment by Publisher...")
        self.analyze_sentiment_by_publisher(top_n, plot)

        return self.results
