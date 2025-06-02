import pandas as pd
from typing import Optional


class DataQualityUtils:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        self.df = df.copy()

    def clean_column_names(self):
        """
        Standardize column names: lowercase, strip spaces,
        and replace spaces with underscores.
        """
        self.df.columns = (
            self.df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
        )
        return self.df

    def drop_redundant_columns(self):
        """
        Drops commonly redundant columns like 'unnamed: 0' or exact duplicates.
        """
        if "unnamed:_0" in self.df.columns:
            self.df = self.df.drop(columns=["unnamed:_0"])
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]
        return self.df

    def clean_dataframe(self):
        """
        Run all preprocessing steps on the internal DataFrame.
        """
        self.clean_column_names()
        self.drop_redundant_columns()
        return self.df

    def columns_with_significant_missing_values(
        self, threshold: float = 5.0
    ) -> pd.DataFrame:
        missing_counts = self.df.isna().sum()
        missing_percent = (missing_counts / len(self.df)) * 100
        significant = missing_percent[missing_percent > threshold]
        return pd.DataFrame(
            {
                "#missing_values": missing_counts[significant.index],
                "percentage": significant.apply(lambda x: f"{x:.2f}%"),
            }
        ).sort_values(by="#missing_values", ascending=False)

    def check_duplicates(self):
        """
        Return the number of duplicate rows in the DataFrame.
        """
        return self.df.duplicated().sum()

    def find_invalid_values(self, additional_invalids=None) -> dict:
        """
        Identifies and summarizes invalid values in object columns.
        """
        if additional_invalids is None:
            additional_invalids = ["NA", "null", "NULL", "-", "N/A"]

        invalid_summary = {}
        for col in self.df.select_dtypes(include="object").columns:
            mask = self.df[col].astype(str).str.strip().isin(["", *additional_invalids])
            count = mask.sum()
            if count > 0:
                invalid_summary[col] = {
                    "count": count,
                    "examples": self.df.loc[mask, col].head(5),
                }
        return invalid_summary

    def summary(self) -> pd.DataFrame:
        """
        Provide a concise summary of missing data in the entire DataFrame.
        """
        missing_counts = self.df.isna().sum()
        missing_percent = (missing_counts / len(self.df)) * 100
        return pd.DataFrame(
            {
                "#missing_values": missing_counts,
                "percentage": missing_percent.map(lambda x: f"{x:.2f}%"),
            }
        ).sort_values(by="#missing_values", ascending=False)

    def count_duplicates(self) -> int:
        """
        Returns the number of duplicate rows in the DataFrame.
        """
        return self.df.duplicated().sum()

    def convert_columns_to_datetime(
        self, columns: Optional[list[str]] = None, errors: str = "coerce"
    ) -> pd.DataFrame:
        if columns is None:
            columns = [
                col
                for col in self.df.columns
                if "date" in col.lower() or "time" in col.lower()
            ]

        for col in columns:
            if col in self.df.columns:
                original_non_null = self.df[col].notna().sum()

                # Ensure strings and strip whitespaces
                self.df[col] = self.df[col].astype(str).str.strip()

                # Replace known bad values
                self.df[col] = self.df[col].replace(
                    ["", "nan", "null", "None", "NaT", "N/A"], pd.NA
                )

                # Convert datetime (handles timezone-aware strings too)
                self.df[col] = pd.to_datetime(self.df[col], errors=errors, utc=True)

                converted = self.df[col].notna().sum()
                print(
                    f"[{col}] Converted: {converted}/{original_non_null} "
                    f"({original_non_null - converted} became NaT)"
                )
            else:
                print(f"Warning: Column '{col}' not found.")
        return self.df
