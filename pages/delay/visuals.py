"""Delay Analysis visual components."""

from __future__ import annotations

from typing import List, Sequence, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_visuals(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render the Delay Analysis visuals in Streamlit."""

    st.plotly_chart(create_delay_map(df, airports_us), width="stretch")
    dep_fig, arr_fig, meta = create_delay_period_comparison(df)
    st.subheader("Daily Average Delays: August 2018 vs January 2020")
    if dep_fig is None or arr_fig is None:
        st.info("Insufficient records for the selected months to draw a comparison.")
        return

    left, right = st.columns(2)
    left.plotly_chart(dep_fig, width="stretch")
    right.plotly_chart(arr_fig, width="stretch")
    st.caption(
        f"Derived from {meta['records']:,} flights across {meta['days']} observed days."
    )


def create_delay_map(
    df: pd.DataFrame,
    airports_us: pd.DataFrame,
    marker_multiplier: int = 450,
) -> go.Figure:
    """Build a geospatial view comparing weather vs non-weather delays."""

    df = df.copy()
    df["WEATHER_DELAY"] = df["WEATHER_DELAY"].fillna(0)
    df["ARR_DELAY"] = df["ARR_DELAY"].fillna(0)

    df_weather = df[df["WEATHER_DELAY"] > 0].copy()
    stats_weather = (
        df_weather.groupby("ORIGIN_AIRPORT")["WEATHER_DELAY"]
        .agg(["sum", "mean", "median"])
        .reset_index()
    )
    stats_weather.columns = ["ORIGIN_AIRPORT", "Total", "Avg", "Median"]
    map_weather = stats_weather.merge(
        airports_us[["IATA", "Latitude", "Longitude", "Airport_Name"]],
        left_on="ORIGIN_AIRPORT",
        right_on="IATA",
    )

    df_other = df[(df["ARR_DELAY"] > 0) & (df["WEATHER_DELAY"] == 0)].copy()
    stats_other = (
        df_other.groupby("ORIGIN_AIRPORT")["ARR_DELAY"]
        .agg(["sum", "mean", "median"])
        .reset_index()
    )
    stats_other.columns = ["ORIGIN_AIRPORT", "Total", "Avg", "Median"]
    map_other = stats_other.merge(
        airports_us[["IATA", "Latitude", "Longitude", "Airport_Name"]],
        left_on="ORIGIN_AIRPORT",
        right_on="IATA",
    )

    def get_size_list(dataset: pd.DataFrame, col: str, multiplier: int) -> List[float]:
        if dataset.empty:
            return []
        values = dataset[col]
        return (values / values.max() * multiplier).fillna(0).tolist()

    w_lon = map_weather["Longitude"].tolist()
    w_lat = map_weather["Latitude"].tolist()
    w_txt = (map_weather["Airport_Name"] + "<br>Code: " +
             map_weather["ORIGIN_AIRPORT"]).tolist()
    w_custom = map_weather[["Total", "Avg", "Median"]].values
    w_size_tot = get_size_list(map_weather, "Total", marker_multiplier)
    w_size_avg = get_size_list(map_weather, "Avg", marker_multiplier)
    w_size_med = get_size_list(map_weather, "Median", marker_multiplier)

    o_lon = map_other["Longitude"].tolist()
    o_lat = map_other["Latitude"].tolist()
    o_txt = (map_other["Airport_Name"] + "<br>Code: " +
             map_other["ORIGIN_AIRPORT"]).tolist()
    o_custom = map_other[["Total", "Avg", "Median"]].values
    o_size_tot = get_size_list(map_other, "Total", marker_multiplier)
    o_size_avg = get_size_list(map_other, "Avg", marker_multiplier)
    o_size_med = get_size_list(map_other, "Median", marker_multiplier)

    fig = go.Figure()

    def _get_theme_color(key: str, fallback: str) -> str:
        try:
            return st.get_option(key) or fallback
        except RuntimeError:
            return fallback

    bg_color = _get_theme_color("theme.backgroundColor", "#0e1117")
    plot_color = _get_theme_color("theme.secondaryBackgroundColor", "#1c1f24")

    fig.add_trace(
        go.Scattergeo(
            lon=w_lon,
            lat=w_lat,
            text=w_txt,
            visible=True,
            name="Weather Delays",
            marker=dict(
                size=w_size_tot,
                color="#F4A261",
                opacity=0.55,
                sizemode="area",
                line_width=0.4,
                line_color="#6D6875",
            ),
            customdata=w_custom,
            hovertemplate="<b>%{text}</b><br>Total: %{customdata[0]:,.0f}m\n<br>Avg: %{customdata[1]:.1f}m\n<br>Med: %{customdata[2]:.1f}m<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scattergeo(
            lon=o_lon,
            lat=o_lat,
            text=o_txt,
            visible=False,
            name="Non-Weather Delays",
            marker=dict(
                size=o_size_tot,
                color="#87A8A4",
                opacity=0.55,
                sizemode="area",
                line_width=0.4,
                line_color="#6D6875",
            ),
            customdata=o_custom,
            hovertemplate="<b>%{text}</b><br>Total: %{customdata[0]:,.0f}m\n<br>Avg: %{customdata[1]:.1f}m\n<br>Med: %{customdata[2]:.1f}m<extra></extra>",
        )
    )

    fig.update_layout(
        height=600,
        title=dict(text="Delay Analysis", y=0.98, x=0.5, xanchor="center"),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="rgb(230, 230, 230)",
            bgcolor=plot_color,
        ),
        margin=dict(t=30, l=0, r=0, b=0),
        paper_bgcolor=bg_color,
        plot_bgcolor=plot_color,
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.01,
                y=1.0,
                xanchor="left",
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.9)",
                font=dict(color="black"),
                buttons=[
                    dict(
                        label="Weather Only",
                        method="update",
                        args=[{"visible": [True, False]}, {
                            "title": "Analysis: Weather Delays"}],
                    ),
                    dict(
                        label="Non-Weather",
                        method="update",
                        args=[{"visible": [False, True]}, {
                            "title": "Analysis: Non-Weather Arrival Delays"}],
                    ),
                ],
            ),
            dict(
                type="buttons",
                direction="left",
                x=0.01,
                y=0.01,
                xanchor="left",
                yanchor="bottom",
                bgcolor="rgba(255, 255, 255, 0.9)",
                active=2,
                font=dict(color="black"),
                buttons=[
                    dict(
                        label="Median",
                        method="restyle",
                        args=[{"marker.size": [w_size_med, o_size_med]}, [0, 1]],
                    ),
                    dict(
                        label="Average",
                        method="restyle",
                        args=[{"marker.size": [w_size_avg, o_size_avg]}, [0, 1]],
                    ),
                    dict(
                        label="Total",
                        method="restyle",
                        args=[{"marker.size": [w_size_tot, o_size_tot]}, [0, 1]],
                    ),
                ],
            ),
        ],
    )

    return fig


def create_delay_period_comparison(
    df: pd.DataFrame,
    periods: Sequence[str] = ("2018-08", "2020-01"),
) -> Tuple[go.Figure | None, go.Figure | None, dict]:
    """Return line charts comparing daily departure/arrival delays for given months."""

    if df.empty:
        return None, None, {"records": 0, "days": 0}

    work_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work_df["FL_DATE"]):
        work_df["FL_DATE"] = pd.to_datetime(work_df["FL_DATE"])

    work_df["Period"] = work_df["FL_DATE"].dt.to_period("M").astype(str)
    work_df["day_of_month"] = work_df["FL_DATE"].dt.day
    filtered = work_df[work_df["Period"].isin(periods)]
    if filtered.empty:
        return None, None, {"records": 0, "days": 0}

    daily = (
        filtered.groupby(["Period", "day_of_month"], dropna=False)
        .aggregate(
            DEP_DELAY=("DEP_DELAY", "mean"),
            ARR_DELAY=("ARR_DELAY", "mean"),
        )
        .reset_index()
    )

    color_map = {periods[0]: "skyblue", periods[-1]: "salmon"}

    dep_fig = px.line(
        daily,
        x="day_of_month",
        y="DEP_DELAY",
        color="Period",
        color_discrete_map=color_map,
        title="Daily Average Departure Delay",
        labels={"day_of_month": "Day of Month",
                "DEP_DELAY": "Avg Departure Delay (min)"},
    )
    dep_fig.update_layout(xaxis=dict(
        tickmode="linear", dtick=1, range=[0.5, 31.5]))

    arr_fig = px.line(
        daily,
        x="day_of_month",
        y="ARR_DELAY",
        color="Period",
        color_discrete_map=color_map,
        title="Daily Average Arrival Delay",
        labels={"day_of_month": "Day of Month",
                "ARR_DELAY": "Avg Arrival Delay (min)"},
    )
    arr_fig.update_layout(xaxis=dict(
        tickmode="linear", dtick=1, range=[0.5, 31.5]))

    return dep_fig, arr_fig, {
        "records": len(filtered),
        "days": daily["day_of_month"].nunique(),
    }
