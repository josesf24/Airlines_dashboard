"""Understanding page visual components."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from theme import ACCENT_GREEN, ACCENT_ORANGE, PRIMARY_COLOR
except ModuleNotFoundError:  # Standalone execution fallback
    PRIMARY_COLOR = "#60A5FA"
    ACCENT_GREEN = "#34D399"
    ACCENT_ORANGE = "#F97316"


def render_visuals(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Show overview cards and a quick look at airline coverage."""

    if df.empty:
        st.info("Load the dataset to explore its structure and coverage.")
        return

    work_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work_df["FL_DATE"]):
        work_df["FL_DATE"] = pd.to_datetime(work_df["FL_DATE"])

    total_flights = len(work_df)
    unique_airlines = work_df["Airline_Name"].nunique()
    unique_routes = (work_df["ORIGIN_AIRPORT"] + " → " +
                     work_df["DEST_AIRPORT"]).nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total flights", _format_int(total_flights))
    col2.metric("Unique airlines", _format_int(unique_airlines))
    col3.metric("Unique routes", _format_int(unique_routes))

    st.subheader("Overall performance snapshot")
    waterfall_data = _build_performance_waterfall_data(work_df)
    if waterfall_data is None:
        st.info("Need August 2018 and January 2020 data to compute performance totals.")
    else:
        st.plotly_chart(
            _render_performance_waterfall(*waterfall_data),
            use_container_width=True,
        )

    st.caption("Metrics reflect the currently loaded dataset slice.")


def _build_performance_waterfall_data(df: pd.DataFrame):
    """Return chart inputs for combined on-time vs delayed waterfall."""

    aug = df[(df["FL_DATE"].dt.year == 2018) & (df["FL_DATE"].dt.month == 8)]
    jan = df[(df["FL_DATE"].dt.year == 2020) & (df["FL_DATE"].dt.month == 1)]
    if aug.empty and jan.empty:
        return None

    frames = []
    if not aug.empty:
        frames.append(_calculate_period_metrics(aug, "August 2018"))
    if not jan.empty:
        frames.append(_calculate_period_metrics(jan, "January 2020"))

    if not frames:
        return None

    combined = pd.concat(frames, ignore_index=True)
    totals = combined.groupby("Category")["Count"].sum()
    categories = {
        "On Time/Early Flights": totals.get("Total On Time/Early", 0),
        "Delayed Flights": totals.get("Total Delayed", 0),
        "Total Flights": totals.get("Total Flights", 0),
    }
    if categories["Total Flights"] == 0:
        return None

    x = list(categories.keys())
    y = list(categories.values())
    measures = ["relative", "relative", "total"]
    return x, y, measures


def _calculate_period_metrics(data_df: pd.DataFrame, period_name: str) -> pd.DataFrame:
    """Return delayed vs on-time counts for a period."""

    total_flights = len(data_df)
    delayed = (data_df["DEP_DELAY"] > 0).sum()
    on_time = (data_df["DEP_DELAY"] <= 0).sum()
    return pd.DataFrame(
        {
            "Period": [period_name] * 3,
            "Category": ["Total Flights", "Total Delayed", "Total On Time/Early"],
            "Count": [total_flights, delayed, on_time],
        }
    )


def _render_performance_waterfall(
    x: list[str],
    y: list[int],
    measures: list[str],
) -> go.Figure:
    """Create the performance waterfall figure using the original layout."""

    fig = go.Figure(
        go.Waterfall(
            name="Overall Flight Performance",
            orientation="v",
            measure=measures,
            x=x,
            y=y,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": ACCENT_GREEN}},
            decreasing={"marker": {"color": ACCENT_ORANGE}},
            totals={"marker": {"color": PRIMARY_COLOR}},
        )
    )
    fig.update_layout(
        title_text="Overall Flight Performance (August 2018 & January 2020 Combined)",
        xaxis_title="Category",
        yaxis_title="Number of Flights",
        showlegend=False,
    )
    return fig


def _format_int(value: int) -> str:
    """Return integer formatted with periods as thousand separators."""

    return f"{value:,}".replace(",", ".")
