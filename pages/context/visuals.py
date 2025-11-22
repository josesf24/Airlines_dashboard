"""Understanding page visual components."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


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
    unique_routes = (work_df["ORIGIN_AIRPORT"] +
                     " → " + work_df["DEST_AIRPORT"]).nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total flights", f"{total_flights:,}")
    col2.metric("Unique airlines", unique_airlines)
    col3.metric("Unique routes", unique_routes)

    st.subheader("Top airlines by flight count")
    flights_by_airline = (
        work_df.groupby("Airline_Name").size().reset_index(
            name="Flights").sort_values("Flights", ascending=False)
    )
    top_airlines = flights_by_airline.head(10)
    if top_airlines.empty:
        st.info("Not enough records to chart airline coverage yet.")
    else:
        fig = px.bar(
            top_airlines,
            x="Flights",
            y="Airline_Name",
            orientation="h",
            text="Flights",
            color="Flights",
            color_continuous_scale="Blues",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sampler of raw records")
    st.dataframe(work_df.head(50))
