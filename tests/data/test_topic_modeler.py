import pandas as pd
import pytest

from eda.topic_modeler import TextCleaner, TopicModeler  # adjust import as needed


def test_text_cleaner_removes_punctuation_and_urls():
    cleaner = TextCleaner()
    raw_text = pd.Series(
        [
            "Hello, World! Visit http://example.com.",
            None,
            "Clean THIS text!!!",
            "Multiple   spaces",
        ]
    )
    cleaned = cleaner.transform(raw_text)
    expected = pd.Series(
        ["hello world visit", "", "clean this text", "multiple spaces"]
    )
    pd.testing.assert_series_equal(cleaned, expected)


def test_topic_modeler_fit_and_keywords():
    data = pd.DataFrame(
        {
            "headline": [
                "Economy is growing fast",
                "Sports events postponed due to weather",
                "New tech innovations in AI",
                "Political debates heat up",
                "Health officials announce new guidelines",
            ]
        }
    )

    modeler = TopicModeler(data, text_col="headline", n_topics=2)
    modeler.fit()
    keywords = modeler.get_keywords()

    assert isinstance(keywords, dict)
    assert len(keywords) == 2
    for topic, words in keywords.items():
        assert topic.startswith("Topic ")
        assert isinstance(words, list)
        assert all(isinstance(w, str) for w in words)
        assert len(words) > 0


def test_get_labeled_df_contains_predicted_topic_and_plot_runs():
    data = pd.DataFrame(
        {
            "headline": [
                "Economy is growing fast",
                "Sports events postponed due to weather",
                "New tech innovations in AI",
                "Political debates heat up",
                "Health officials announce new guidelines",
            ]
        }
    )

    modeler = TopicModeler(data, text_col="headline", n_topics=2)
    modeler.fit()
    labeled_df = modeler.get_labeled_df()
    assert "Predicted Topic" not in labeled_df.columns  # before plotting

    # Run plot function, which adds "Predicted Topic"
    modeler.plot_topic_distribution()

    labeled_df = modeler.get_labeled_df()
    assert "Predicted Topic" in labeled_df.columns
    assert labeled_df["Predicted Topic"].str.startswith("Topic ").all()


def test_empty_and_missing_text_column():
    # Empty dataframe
    empty_df = pd.DataFrame(columns=["headline"])
    modeler = TopicModeler(empty_df, text_col="headline")
    with pytest.raises(ValueError):
        modeler.fit()  # fitting on empty data should fail

    # Missing column
    df = pd.DataFrame({"text": ["sample text"]})
    with pytest.raises(KeyError):
        TopicModeler(df, text_col="headline")  # 'headline' column missing


def test_text_cleaner_fit_returns_self():
    cleaner = TextCleaner()
    assert cleaner.fit(None) is cleaner
