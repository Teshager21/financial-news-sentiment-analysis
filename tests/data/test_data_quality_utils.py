import pandas as pd
import pytest

from src.eda.data_quality_utils import (
    DataQualityUtils,
)  # Adjust this import to match your file structure


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            " Unnamed: 0 ": [1, 2, 3],
            "Name ": ["Alice", "Bob", None],
            "Email": ["alice@example.com", None, "bob@example.com"],
            " Date of Birth ": ["2020-01-01", "N/A", "null"],
            "duplicate": ["x", "x", "x"],
        }
    )


def test_init_with_non_dataframe():
    """Should raise a TypeError if input is not a DataFrame"""
    with pytest.raises(TypeError):
        DataQualityUtils("not a dataframe")


def test_clean_column_names(sample_df):
    """Should standardize column names"""
    dq = DataQualityUtils(sample_df)
    df_clean = dq.clean_column_names()
    assert "unnamed:_0" in df_clean.columns
    assert "date_of_birth" in df_clean.columns


def test_drop_redundant_columns(sample_df):
    """Should drop 'unnamed:_0' and duplicate columns"""
    dq = DataQualityUtils(sample_df)
    dq.clean_column_names()
    df_clean = dq.drop_redundant_columns()
    assert "unnamed:_0" not in df_clean.columns
    assert df_clean.columns.duplicated().sum() == 0


def test_clean_dataframe(sample_df):
    """Should apply both cleaning steps and return cleaned DataFrame"""
    dq = DataQualityUtils(sample_df)
    df_cleaned = dq.clean_dataframe()
    assert "unnamed:_0" not in df_cleaned.columns
    assert "date_of_birth" in df_cleaned.columns


def test_columns_with_significant_missing_values(sample_df):
    """Should return only columns with missing percentage > threshold"""
    dq = DataQualityUtils(sample_df)
    result = dq.columns_with_significant_missing_values(threshold=20)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "#missing_values" in result.columns
    assert "percentage" in result.columns


def test_check_duplicates(sample_df):
    """Should correctly count duplicate rows"""
    dq = DataQualityUtils(sample_df)
    assert dq.check_duplicates() == 0


def test_find_invalid_values(sample_df):
    """Should find invalid entries in object columns"""
    dq = DataQualityUtils(sample_df)
    dq.clean_column_names()
    invalids = dq.find_invalid_values()
    assert isinstance(invalids, dict)
    assert "date_of_birth" in invalids


def test_summary_missing_values(sample_df):
    """Should return summary of missing values"""
    dq = DataQualityUtils(sample_df)
    summary = dq.summary()
    assert "#missing_values" in summary.columns
    assert "percentage" in summary.columns


def test_count_duplicates(sample_df):
    """Should match check_duplicates for compatibility"""
    dq = DataQualityUtils(sample_df)
    assert dq.count_duplicates() == dq.check_duplicates()


def test_convert_columns_to_datetime(sample_df, capsys):
    """Should convert datetime-related columns and print conversion info"""
    dq = DataQualityUtils(sample_df)
    dq.clean_column_names()
    result_df = dq.convert_columns_to_datetime()

    assert pd.api.types.is_datetime64_any_dtype(result_df["date_of_birth"])
    captured = capsys.readouterr()
    assert "Converted" in captured.out or "not found" in captured.out
