"""
analysis.py
Automatic exploratory data analysis: statistical summaries, correlation
analysis, outlier detection, trend/time-series detection, and category
breakdowns. Pure pandas/numpy/sklearn - no LLM calls - so it's fast and
deterministic; ai_engine.py then narrates these numbers into insights.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def basic_profile(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": list(df.select_dtypes(include=np.number).columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
        "datetime_columns": list(df.select_dtypes(include=["datetime64[ns]"]).columns),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2),
    }


def statistical_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.empty:
        return pd.DataFrame()
    summary = numeric_df.describe().T
    summary["median"] = numeric_df.median()
    summary["mode"] = numeric_df.mode().iloc[0] if not numeric_df.mode().empty else np.nan
    summary["sum"] = numeric_df.sum()
    summary["skew"] = numeric_df.skew()
    return summary


def correlation_analysis(df: pd.DataFrame, threshold: float = 0.6) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return pd.DataFrame(columns=["feature_1", "feature_2", "correlation"])
    corr = numeric_df.corr()
    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.iloc[i, j]
            if abs(val) >= threshold:
                pairs.append({"feature_1": cols[i], "feature_2": cols[j], "correlation": round(val, 3)})
    return pd.DataFrame(pairs).sort_values("correlation", ascending=False) if pairs else pd.DataFrame(
        columns=["feature_1", "feature_2", "correlation"])


def detect_outliers(df: pd.DataFrame, contamination: float = 0.03) -> pd.DataFrame:
    """Isolation Forest based multivariate outlier detection on numeric columns."""
    numeric_df = df.select_dtypes(include=np.number).dropna()
    if numeric_df.shape[0] < 10 or numeric_df.shape[1] == 0:
        return pd.DataFrame()
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(numeric_df)
    outlier_idx = numeric_df.index[preds == -1]
    return df.loc[outlier_idx]


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isna().sum()
    pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({"missing_count": missing, "missing_pct": pct})
    return report[report["missing_count"] > 0].sort_values("missing_count", ascending=False)


def find_duplicate_records(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.duplicated(keep=False)].sort_values(list(df.columns))


def detect_time_column(df: pd.DataFrame):
    """Best-effort guess at which column represents a date/time axis."""
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower() or "year" in col.lower() or "month" in col.lower():
            return col
    for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
        return col
    return None


def trend_detection(df: pd.DataFrame, value_col: str, time_col: str = None) -> pd.DataFrame:
    time_col = time_col or detect_time_column(df)
    if time_col is None or value_col not in df.columns:
        return pd.DataFrame()
    work = df[[time_col, value_col]].copy()
    work[time_col] = pd.to_datetime(work[time_col], errors="coerce")
    work = work.dropna(subset=[time_col])
    work = work.groupby(pd.Grouper(key=time_col, freq="ME"))[value_col].sum().reset_index()
    work["growth_pct"] = work[value_col].pct_change().round(4) * 100
    return work


def category_breakdown(df: pd.DataFrame, category_col: str, value_col: str, top_n: int = 10) -> pd.DataFrame:
    if category_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    grouped = df.groupby(category_col)[value_col].sum().sort_values(ascending=False).head(top_n)
    return grouped.reset_index()


def feature_importance(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """Quick Random Forest feature importance for a numeric target."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder

    if target_col not in df.columns:
        return pd.DataFrame()
    work = df.dropna().copy()
    if work.empty:
        return pd.DataFrame()
    y = work[target_col]
    X = work.drop(columns=[target_col])
    for col in X.select_dtypes(include=["object", "category"]).columns:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))
    if not np.issubdtype(y.dtype, np.number):
        return pd.DataFrame()
    if X.empty:
        return pd.DataFrame()
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    importance = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)
    return importance


def build_text_summary(df: pd.DataFrame) -> str:
    """Compact text summary of the dataset, fed to the LLM for insight generation."""
    profile = basic_profile(df)
    stats = statistical_summary(df)
    corr = correlation_analysis(df)
    missing = missing_value_report(df)

    lines = [
        f"Rows: {profile['rows']}, Columns: {profile['columns']}",
        f"Missing values: {profile['missing_values']}, Duplicate rows: {profile['duplicate_rows']}",
        f"Numeric columns: {', '.join(profile['numeric_columns']) or 'none'}",
        f"Categorical columns: {', '.join(profile['categorical_columns']) or 'none'}",
    ]
    if not stats.empty:
        lines.append("Key stats (mean/median/min/max) for top numeric columns:")
        for col in stats.index[:8]:
            row = stats.loc[col]
            lines.append(
                f"  {col}: mean={row['mean']:.2f}, median={row['median']:.2f}, "
                f"min={row['min']:.2f}, max={row['max']:.2f}"
            )
    if not corr.empty:
        lines.append("Strong correlations:")
        for _, r in corr.head(5).iterrows():
            lines.append(f"  {r['feature_1']} vs {r['feature_2']}: {r['correlation']}")
    if not missing.empty:
        lines.append("Columns with missing data:")
        for col, r in missing.head(5).iterrows():
            lines.append(f"  {col}: {r['missing_pct']}% missing")
    return "\n".join(lines)
