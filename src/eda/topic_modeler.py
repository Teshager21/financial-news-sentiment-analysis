import re

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline


class TextCleaner(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.pattern = re.compile(r"[^\w\s]")  # Remove punctuation

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.fillna("").apply(self._clean_text)

    def _clean_text(self, text):
        text = text.lower()
        text = re.sub(r"http\S+", "", text)  # Remove URLs
        text = self.pattern.sub("", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text


class TopicModeler:
    def __init__(self, df: pd.DataFrame, text_col: str = "headline", n_topics: int = 5):
        self.df = df.copy()
        self.text_col = text_col
        self.n_topics = n_topics
        self.vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words="english")
        self.lda_model = LatentDirichletAllocation(
            n_components=self.n_topics, random_state=42
        )
        self.pipeline = Pipeline(
            [("cleaner", TextCleaner()), ("tfidf", self.vectorizer)]
        )
        self.topic_keywords: dict[str, list[str]] = {}

    def fit(self):
        """
        Fit the LDA model to the cleaned text data.
        """
        cleaned_text = self.pipeline.named_steps["cleaner"].transform(
            self.df[self.text_col]
        )
        tfidf_matrix = self.pipeline.named_steps["tfidf"].fit_transform(cleaned_text)
        self.lda_model.fit(tfidf_matrix)
        self._extract_topic_keywords()
        return self

    def _extract_topic_keywords(self, n_top_words: int = 10):
        """
        Extract top keywords per topic.
        """
        feature_names = self.vectorizer.get_feature_names_out()
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_features = topic.argsort()[: -n_top_words - 1 : -1]
            self.topic_keywords[f"Topic {topic_idx + 1}"] = [
                feature_names[i] for i in top_features
            ]

    def display_topics(self):
        """
        Print extracted topics and keywords.
        """
        print("Top Keywords per Topic:")
        for topic, keywords in self.topic_keywords.items():
            print(f"{topic}: {', '.join(keywords)}")

    def plot_topic_distribution(self):
        """
        Plot number of articles per topic.
        """
        cleaned_text = self.pipeline.named_steps["cleaner"].transform(
            self.df[self.text_col]
        )
        tfidf_matrix = self.pipeline.named_steps["tfidf"].transform(cleaned_text)
        topic_distribution = self.lda_model.transform(tfidf_matrix).argmax(axis=1)

        topic_labels = [f"Topic {i + 1}" for i in topic_distribution]
        self.df["Predicted Topic"] = topic_labels

        plt.figure(figsize=(8, 5))
        sns.countplot(x="Predicted Topic", data=self.df, palette="cubehelix")
        plt.title("Distribution of Articles by Predicted Topic")
        plt.xlabel("Topic")
        plt.ylabel("Article Count")
        plt.tight_layout()
        plt.show()

    def get_keywords(self):
        return self.topic_keywords

    def get_labeled_df(self):
        return self.df
