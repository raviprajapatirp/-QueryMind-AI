"""
cleaning.py
One-click data cleaning operations used by the Data Cleaning page. Every
function takes a DataFrame and returns a new cleaned DataFrame (originals
are never mutated in place) so the UI can offer an undo/preview flow.
"""

import pandas as pd
import numpy as np


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def drop_nulls(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    return df.dropna(subset=columns).reset_index(drop=True)


def fill_nulls(df: pd.DataFrame, strategy: str = "mean", columns=None, fill_value=None) -> pd.DataFrame:
    out = df.copy()
    cols = columns or out.columns.tolist()
    for col in cols:
        if col not in out.columns:
            continue
        if strategy == "mean" and pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].fillna(out[col].mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].fillna(out[col].median())
        elif strategy == "mode":
            mode_val = out[col].mode()
            if not mode_val.empty:
                out[col] = out[col].fillna(mode_val[0])
        elif strategy == "constant":
            out[col] = out[col].fillna(fill_value)
        elif strategy == "ffill":
            out[col] = out[col].ffill()
        elif strategy == "bfill":
            out[col] = out[col].bfill()
    return out


def convert_dtype(df: pd.DataFrame, column: str, new_type: str) -> pd.DataFrame:
    out = df.copy()
    try:
        if new_type == "datetime":
            out[column] = pd.to_datetime(out[column], errors="coerce")
        elif new_type == "numeric":
            out[column] = pd.to_numeric(out[column], errors="coerce")
        elif new_type == "string":
            out[column] = out[column].astype(str)
        elif new_type == "category":
            out[column] = out[column].astype("category")
        elif new_type == "boolean":
            out[column] = out[column].astype(bool)
    except Exception as e:
        raise ValueError(f"Could not convert '{column}' to {new_type}: {e}")
    return out


def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    return df.rename(columns=mapping)


def normalize_text(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    out = df.copy()
    cols = columns or out.select_dtypes(include=["object"]).columns.tolist()
    for col in cols:
        out[col] = out[col].astype(str).str.strip().str.lower()
    return out


def standardize_numeric(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    """Z-score standardization for selected numeric columns."""
    out = df.copy()
    cols = columns or out.select_dtypes(include=np.number).columns.tolist()
    for col in cols:
        std = out[col].std()
        if std and std != 0:
            out[col] = (out[col] - out[col].mean()) / std
    return out


def drop_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    return df.drop(columns=[c for c in columns if c in df.columns])


def remove_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return df
    q1, q3 = df[column].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - factor * iqr, q3 + factor * iqr
    return df[(df[column] >= lower) & (df[column] <= upper)].reset_index(drop=True)
