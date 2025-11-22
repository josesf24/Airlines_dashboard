"""Flight volume visual components."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_visuals(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render flight volume charts."""

    if df.empty:
        st.info("No flight records available to analyze volumes.")
        return

    work_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work_df["FL_DATE"]):
        work_df["FL_DATE"] = pd.to_datetime(work_df["FL_DATE"])

    monthly = (
        work_df.assign(Month=work_df["FL_DATE"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month")
        .size()
        .reset_index(name="Flights")
    )

    st.subheader("Flights per month")
    if monthly.empty:
        st.info("Unable to compute monthly totals for the selected data.")
    else:
        fig = px.line(
            monthly,
            x="Month",
            y="Flights",
            markers=True,
            title="Monthly flight volume",
        )
        fig.update_traces(line_color="#3772FF")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Busiest airports")
    mode = st.selectbox("Rank by", ("Origin", "Destination"), key="volume_rank_mode")
    column = "ORIGIN_AIRPORT" if mode == "Origin" else "DEST_AIRPORT"
    top_airports = (
        work_df.groupby(column)
        .size()
        .reset_index(name="Flights")
        .sort_values("Flights", ascending=False)
        .head(10)
    )
    if top_airports.empty:
        st.info("Not enough airport records to rank volume.")
    else:
        merged = top_airports.merge(
            airports_us[["IATA", "Airport_Name", "City"]],
            left_on=column,
            right_on="IATA",
            how="left",
        )
        merged["Label"] = merged["Airport_Name"].fillna(merged[column])
        fig = px.bar(
            merged,
            x="Flights",
            y="Label",
            orientation="h",
            text="Flights",
            title=f"Top 10 {mode.lower()} airports by flights",
            color="Flights",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Day-of-week distribution")
    work_df["Day"] = work_df["FL_DATE"].dt.day_name()
    day_counts = (
        work_df.groupby("Day").size().reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
    )
    day_counts = day_counts.dropna().reset_index(name="Flights")
    if day_counts.empty:
        st.info("Cannot compute day-of-week distribution for this slice of data.")
    else:
        fig = px.area(
            day_counts,
            x="Day",
            y="Flights",
            title="Flights by day of week",
            color_discrete_sequence=["#FFA630"],
        )
        st.plotly_chart(fig, use_container_width=True)
