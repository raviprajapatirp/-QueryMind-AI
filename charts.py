"""
charts.py
A library of reusable Plotly chart builders. Every function takes a
DataFrame plus column selections and returns a Plotly figure styled to
match the app's dark/light theme. app.py's Charts page uses these to let
users pick a chart type and columns interactively; dashboard.py uses a
subset automatically for the auto-generated dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

TEMPLATE = "plotly_dark"


def _apply_layout(fig, title=""):
    fig.update_layout(
        template=TEMPLATE,
        title=title,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def bar_chart(df, x, y, color=None, title="Bar Chart"):
    fig = px.bar(df, x=x, y=y, color=color)
    return _apply_layout(fig, title)


def line_chart(df, x, y, color=None, title="Line Chart"):
    fig = px.line(df, x=x, y=y, color=color, markers=True)
    return _apply_layout(fig, title)


def pie_chart(df, names, values, title="Pie Chart"):
    fig = px.pie(df, names=names, values=values, hole=0)
    return _apply_layout(fig, title)


def donut_chart(df, names, values, title="Donut Chart"):
    fig = px.pie(df, names=names, values=values, hole=0.55)
    return _apply_layout(fig, title)


def scatter_plot(df, x, y, color=None, size=None, title="Scatter Plot"):
    fig = px.scatter(df, x=x, y=y, color=color, size=size)
    return _apply_layout(fig, title)


def histogram(df, x, bins=30, title="Histogram"):
    fig = px.histogram(df, x=x, nbins=bins)
    return _apply_layout(fig, title)


def box_plot(df, x=None, y=None, title="Box Plot"):
    fig = px.box(df, x=x, y=y)
    return _apply_layout(fig, title)


def violin_plot(df, x=None, y=None, title="Violin Plot"):
    fig = px.violin(df, x=x, y=y, box=True)
    return _apply_layout(fig, title)


def heatmap(df, title="Heatmap"):
    numeric_df = df.select_dtypes(include=np.number)
    fig = px.imshow(numeric_df.corr(), text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r")
    return _apply_layout(fig, title)


def correlation_matrix(df, title="Correlation Matrix"):
    return heatmap(df, title)


def area_chart(df, x, y, color=None, title="Area Chart"):
    fig = px.area(df, x=x, y=y, color=color)
    return _apply_layout(fig, title)


def treemap(df, path, values, title="Treemap"):
    fig = px.treemap(df, path=path, values=values)
    return _apply_layout(fig, title)


def sunburst(df, path, values, title="Sunburst"):
    fig = px.sunburst(df, path=path, values=values)
    return _apply_layout(fig, title)


def waterfall(df, x, y, title="Waterfall Chart"):
    fig = go.Figure(go.Waterfall(x=df[x], y=df[y]))
    return _apply_layout(fig, title)


def bubble_chart(df, x, y, size, color=None, title="Bubble Chart"):
    fig = px.scatter(df, x=x, y=y, size=size, color=color)
    return _apply_layout(fig, title)


def funnel_chart(df, x, y, title="Funnel Chart"):
    fig = px.funnel(df, x=x, y=y)
    return _apply_layout(fig, title)


def gauge_chart(value, min_val=0, max_val=100, title="Gauge"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={"axis": {"range": [min_val, max_val]}},
        title={"text": title},
    ))
    return _apply_layout(fig, title)


def geo_map(df, locations, color, location_mode="country names", title="Geo Map"):
    fig = px.choropleth(df, locations=locations, color=color, locationmode=location_mode)
    return _apply_layout(fig, title)


def time_series(df, x, y, color=None, title="Time Series"):
    fig = px.line(df, x=x, y=y, color=color)
    return _apply_layout(fig, title)


def distribution_plot(df, x, title="Distribution Plot"):
    fig = px.histogram(df, x=x, marginal="box", nbins=40)
    return _apply_layout(fig, title)


def pair_plot(df, dimensions, color=None, title="Pair Plot"):
    fig = px.scatter_matrix(df, dimensions=dimensions, color=color)
    return _apply_layout(fig, title)


CHART_REGISTRY = {
    "Bar Chart": bar_chart,
    "Line Chart": line_chart,
    "Pie Chart": pie_chart,
    "Donut Chart": donut_chart,
    "Scatter Plot": scatter_plot,
    "Histogram": histogram,
    "Box Plot": box_plot,
    "Violin Plot": violin_plot,
    "Heatmap": heatmap,
    "Correlation Matrix": correlation_matrix,
    "Area Chart": area_chart,
    "Treemap": treemap,
    "Sunburst": sunburst,
    "Waterfall Chart": waterfall,
    "Bubble Chart": bubble_chart,
    "Funnel Chart": funnel_chart,
    "Geo Map": geo_map,
    "Time Series": time_series,
    "Distribution Plot": distribution_plot,
    "Pair Plot": pair_plot,
}
