import matplotlib.pyplot as plt
import pandas as pd
import pytest

from eda.publisher_analyzer import PublisherAnalyzer


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "publisher": [
                "alice@example.com",
                "bob@example.com",
                "carol@test.org",
                "alice@example.com",
                "dan@news.net",
                "bob@example.com",
                "eve@sample.com",
                "frank@sample.com",
                "alice@example.com",
            ],
            "sentiment_score": [0.1, -0.2, 0.5, 0.4, 0.0, -0.1, 0.3, 0.2, 0.1],
        }
    )


@pytest.fixture
def sample_data_no_sentiment():
    return pd.DataFrame(
        {
            "publisher": [
                "alice@example.com",
                "bob@example.com",
                "carol@test.org",
                "dan@news.net",
            ]
        }
    )


def test_analyze_top_publishers(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    result = analyzer.analyze_top_publishers(top_n=2, plot=False)
    assert isinstance(result, pd.Series)
    assert result.index[0] == "alice@example.com"
    assert analyzer.results["top_publishers"].equals(result)


def test_analyze_top_publishers_plot(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    # test plotting runs without error; close plot to avoid display issues
    analyzer.analyze_top_publishers(top_n=2, plot=True)
    plt.close("all")


def test_analyze_domains(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    result = analyzer.analyze_domains(top_n=3, plot=False)
    expected_domains = ["example.com", "sample.com", "test.org"]
    assert all(domain in expected_domains for domain in result.index)
    assert analyzer.results["domain_counts"].equals(result)


def test_analyze_domains_plot(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    analyzer.analyze_domains(top_n=3, plot=True)
    plt.close("all")


def test_analyze_sentiment_by_publisher(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    result = analyzer.analyze_sentiment_by_publisher(top_n=2, plot=False)
    assert isinstance(result, pd.Series)
    # Check all publishers in result are valid publishers from input
    assert all(pub in sample_data["publisher"].values for pub in result.index)
    assert analyzer.results["sentiment_by_publisher"].equals(result)


def test_analyze_sentiment_by_publisher_no_column(sample_data_no_sentiment):
    analyzer = PublisherAnalyzer(sample_data_no_sentiment)
    result = analyzer.analyze_sentiment_by_publisher(top_n=2, plot=False)
    assert result is None


def test_analyze_sentiment_by_publisher_plot(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    analyzer.analyze_sentiment_by_publisher(top_n=2, plot=True)
    plt.close("all")


def test_run_all(sample_data):
    analyzer = PublisherAnalyzer(sample_data)
    results = analyzer.run_all(top_n=3, plot=False)
    assert "top_publishers" in results
    assert "domain_counts" in results
    assert "sentiment_by_publisher" in results
