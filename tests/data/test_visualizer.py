import pytest
import pandas as pd
from src.eda.visualizer import DataVisualizer


def test_plot_headline_length_distribution(capsys):
    df = pd.DataFrame(
        {"headline": ["Short", "A bit longer headline", None, "Another headline"]}
    )
    visualizer = DataVisualizer(df)

    # Should print stats and plot without error
    visualizer.plot_headline_length_distribution()
    captured = capsys.readouterr()
    assert "Headline Length Statistics" in captured.out

    # Test missing column error
    visualizer_missing = DataVisualizer(df.drop(columns=["headline"]))
    with pytest.raises(KeyError):
        visualizer_missing.plot_headline_length_distribution()


def test_plot_articles_per_publisher():
    df = pd.DataFrame({"publisher": ["A", "B", "A", "C", "B", "B"]})
    visualizer = DataVisualizer(df)

    # Should plot without error
    visualizer.plot_articles_per_publisher(top_n=2)

    # Test missing column error
    visualizer_missing = DataVisualizer(df.drop(columns=["publisher"]))
    with pytest.raises(KeyError):
        visualizer_missing.plot_articles_per_publisher()


def test_plot_weekday_distribution():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2023-06-01",
                    "2023-06-02",
                    "2023-06-03",
                    "2023-06-04",
                    "2023-06-05",
                    "2023-06-06",
                    "2023-06-07",
                ]
            )
        }
    )
    visualizer = DataVisualizer(df)

    # Should plot without error
    visualizer.plot_weekday_distribution()

    # Missing date column
    visualizer_missing = DataVisualizer(df.drop(columns=["date"]))
    with pytest.raises(KeyError):
        visualizer_missing.plot_weekday_distribution()

    # Wrong dtype for date_col
    df_wrong_dtype = df.copy()
    df_wrong_dtype["date"] = df_wrong_dtype["date"].astype(str)
    visualizer_wrong_dtype = DataVisualizer(df_wrong_dtype)
    with pytest.raises(TypeError):
        visualizer_wrong_dtype.plot_weekday_distribution()
