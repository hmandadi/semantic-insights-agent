"""
Visualization Service

Provides intelligent chart selection and dataframe preparation
for Streamlit visualizations.
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd


logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class VisualizationService:

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert numeric-looking string columns into numeric types.
        """

        result = df.copy()

        for col in result.columns:

            if result[col].dtype == "object":

                try:

                    cleaned = (
                        result[col]
                        .astype(str)
                        .str.replace("$", "", regex=False)
                        .str.replace(",", "", regex=False)
                        .str.replace("%", "", regex=False)
                    )

                    converted = pd.to_numeric(
                        cleaned,
                        errors="coerce"
                    )

                    if converted.notna().sum() > 0:
                        result[col] = converted

                except Exception:
                    pass

        return result

    def get_chart_type(self, df: pd.DataFrame) -> Optional[str]:

        if df is None or df.empty:
            return None

        df = self._normalize_dataframe(df)

        text_cols = (
            df.select_dtypes(include=["object", "string"])
            .columns
            .tolist()
        )

        numeric_cols = (
            df.select_dtypes(include=["number"])
            .columns
            .tolist()
        )

        datetime_cols = (
            df.select_dtypes(include=["datetime64[ns]"])
            .columns
            .tolist()
        )

        if datetime_cols and numeric_cols:
            return "line"

        if text_cols and numeric_cols:
            return "bar"

        if len(numeric_cols) >= 2:
            return "bar"

        return None

    def prepare_chart_data(self, df: pd.DataFrame) -> pd.DataFrame:

        if df is None or df.empty:
            return pd.DataFrame()

        chart_df = self._normalize_dataframe(df.copy())

        chart_df.columns = [
            str(col).strip()
            for col in chart_df.columns
        ]

        chart_df = chart_df.reset_index(drop=True)

        return chart_df

    def get_chart_columns(
        self,
        df: pd.DataFrame
    ) -> tuple[str, str] | tuple[None, None]:

        if df is None or df.empty:
            return None, None

        df = self._normalize_dataframe(df)

        text_cols = (
            df.select_dtypes(include=["object", "string"])
            .columns
            .tolist()
        )

        numeric_cols = (
            df.select_dtypes(include=["number"])
            .columns
            .tolist()
        )

        datetime_cols = (
            df.select_dtypes(include=["datetime64[ns]"])
            .columns
            .tolist()
        )

        if datetime_cols and numeric_cols:
            return datetime_cols[0], numeric_cols[0]

        if text_cols and numeric_cols:
            return text_cols[0], numeric_cols[0]

        if len(numeric_cols) >= 2:
            return numeric_cols[0], numeric_cols[1]

        return None, None