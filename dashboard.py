"""
dashboard.py
Builds the auto-generated "Executive Dashboard": KPI cards derived from
analysis.py, plus a curated set of charts (trend, top categories,
correlation heatmap) chosen automatically based on the dataset's column
types. Also renders interactive filters (date/category/region/etc.).
"""

import streamlit as st
import pandas as pd
import numpy as np

from analysis import basic_profile, statistical_summary, detect_time_column
from utils import kpi_card, human_number
import charts as ch


def render_kpi_row(df: pd.DataFrame):
    profile = basic_profile(df)
    numeric_cols = profile["numeric_columns"]

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Total Rows", human_number(profile["rows"]))
    with cols[1]:
        kpi_card("Total Columns", str(profile["columns"]))
    with cols[2]:
        kpi_card("Missing Values", human_number(profile["missing_values"]))
    with cols[3]:
        kpi_card("Duplicate Rows", human_number(profile["duplicate_rows"]))

    if numeric_cols:
        primary = numeric_cols[0]
        stats = statistical_summary(df)
        if primary in stats.index:
            row = stats.loc[primary]
            cols2 = st.columns(4)
            with cols2[0]:
                kpi_card(f"Sum ({primary})", human_number(row["sum"]))
            with cols2[1]:
                kpi_card(f"Average ({primary})", human_number(row["mean"]))
            with cols2[2]:
                kpi_card(f"Min ({primary})", human_number(row["min"]))
            with cols2[3]:
                kpi_card(f"Max ({primary})", human_number(row["max"]))


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders sidebar-style filters and returns the filtered DataFrame."""
    filtered = df.copy()
    with st.expander("🔎 Interactive Filters", expanded=False):
        time_col = detect_time_column(df)
        cat_cols = [c for c in df.select_dtypes(include=["object", "category"]).columns]

        cols = st.columns(min(4, max(1, len(cat_cols) + (1 if time_col else 0))))
        idx = 0

        if time_col:
            try:
                parsed = pd.to_datetime(df[time_col], errors="coerce")
                min_d, max_d = parsed.min(), parsed.max()
                with cols[idx % len(cols)]:
                    date_range = st.date_input(f"Date filter ({time_col})", (min_d, max_d))
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    mask = (pd.to_datetime(filtered[time_col], errors="coerce") >= pd.Timestamp(date_range[0])) & \
                           (pd.to_datetime(filtered[time_col], errors="coerce") <= pd.Timestamp(date_range[1]))
                    filtered = filtered[mask]
                idx += 1
            except Exception:
                pass

        for c in cat_cols[:3]:
            with cols[idx % len(cols)]:
                options = ["All"] + sorted(df[c].dropna().astype(str).unique().tolist())[:200]
                choice = st.selectbox(f"Filter: {c}", options, key=f"filter_{c}")
            if choice != "All":
                filtered = filtered[filtered[c].astype(str) == choice]
            idx += 1

    return filtered


def render_auto_charts(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    time_col = detect_time_column(df)

    c1, c2 = st.columns(2)

    with c1:
        if time_col and numeric_cols:
            try:
                work = df[[time_col, numeric_cols[0]]].copy()
                work[time_col] = pd.to_datetime(work[time_col], errors="coerce")
                work = work.dropna().groupby(time_col)[numeric_cols[0]].sum().reset_index()
                st.plotly_chart(ch.time_series(work, time_col, numeric_cols[0],
                                                title=f"{numeric_cols[0]} Over Time"),
                                 use_container_width=True)
            except Exception:
                st.info("Could not build a time trend for this dataset.")
        elif len(numeric_cols) >= 2:
            st.plotly_chart(ch.scatter_plot(df, numeric_cols[0], numeric_cols[1],
                                             title=f"{numeric_cols[0]} vs {numeric_cols[1]}"),
                             use_container_width=True)

    with c2:
        if cat_cols and numeric_cols:
            grouped = df.groupby(cat_cols[0])[numeric_cols[0]].sum().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(ch.bar_chart(grouped, cat_cols[0], numeric_cols[0],
                                          title=f"Top {cat_cols[0]} by {numeric_cols[0]}"),
                             use_container_width=True)
        elif numeric_cols:
            st.plotly_chart(ch.histogram(df, numeric_cols[0], title=f"Distribution of {numeric_cols[0]}"),
                             use_container_width=True)

    if len(numeric_cols) >= 2:
        st.plotly_chart(ch.correlation_matrix(df, title="Correlation Matrix"), use_container_width=True)


def render_dashboard(df: pd.DataFrame):
    st.subheader("📊 Executive Dashboard")
    filtered = render_filters(df)
    render_kpi_row(filtered)
    st.divider()
    render_auto_charts(filtered)
    return filtered
