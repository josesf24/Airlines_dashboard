"""Best Airline Suggester visual components."""

from __future__ import annotations

from typing import Tuple

import pandas as pd
import streamlit as st


def render_visuals(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render interactive airline recommendations for a chosen route."""

    st.subheader("Route-specific performance ranking")
    if df.empty:
        st.info("No flight records available. Load data to unlock suggestions.")
        return

    origins = sorted(df["ORIGIN_AIRPORT"].dropna().unique())
    origin_choice = st.selectbox(
        "Origin airport",
        origins,
        index=0,
        key="best_airline_origin",
    )
    destinations = sorted(
        df.loc[df["ORIGIN_AIRPORT"] == origin_choice,
               "DEST_AIRPORT"].dropna().unique()
    )
    if not destinations:
        st.warning(
            "This origin currently has no destination records in the dataset.")
        return

    destination_choice = st.selectbox(
        "Destination airport",
        destinations,
        index=0,
        key="best_airline_destination",
    )

    recommendations, sample_size, weeks_observed = _get_route_recommendations(
        df, origin_choice, destination_choice
    )

    if sample_size == 0:
        st.warning("No flights found for the selected route.")
        return

    left, middle, right = st.columns(3)
    left.metric("Flights analyzed", f"{sample_size:,}")
    middle.metric("Weeks of data", weeks_observed if weeks_observed else "–")
    if not recommendations.empty:
        right.metric(
            "Best avg arrival delay",
            f"{recommendations.iloc[0]['Avg Arrival Delay (min)']:.1f} min",
        )
    else:
        right.metric("Best avg arrival delay", "–")

    if recommendations.empty:
        st.info(
            "Every airline on this route has very few flights in the selected period."
        )
        return

    total_weekly = recommendations['Flights / Week'].sum()
    st.write(
        f"Top {len(recommendations)} airlines for this route (about {total_weekly:.1f} flights/week combined)."
    )
    st.dataframe(recommendations, width="stretch")
    st.caption(
        "Avg delays below zero mean the airline typically arrives ahead of schedule. Flights/week reflects only the weeks present in the dataset."
    )


def _get_route_recommendations(
    df: pd.DataFrame,
    origin: str,
    destination: str,
) -> Tuple[pd.DataFrame, int, int]:
    """Return the best-performing airlines on the specified route."""

    route_df = df[(df["ORIGIN_AIRPORT"] == origin) & (
        df["DEST_AIRPORT"] == destination)].copy()
    if route_df.empty:
        return pd.DataFrame(), 0, 0

    if not pd.api.types.is_datetime64_any_dtype(route_df["FL_DATE"]):
        route_df["FL_DATE"] = pd.to_datetime(route_df["FL_DATE"])

    route_df["YearWeek"] = route_df["FL_DATE"].dt.to_period("W")
    weeks_observed = max(int(route_df["YearWeek"].nunique()), 1)

    grouped = (
        route_df.groupby(["AIRLINE_ID", "Airline_Name"], dropna=False)
        .aggregate(
            Flights=("ARR_DELAY", "size"),
            AvgArrivalDelay=("ARR_DELAY", "mean"),
            OnTimeRate=("ARR_DELAY", lambda s: (s <= 0).mean()),
        )
        .reset_index()
    )

    weeks_per_airline = (
        route_df.groupby("AIRLINE_ID")["YearWeek"].nunique(
        ).reset_index(name="WeeksWithFlights")
    )
    grouped = grouped.merge(weeks_per_airline, on="AIRLINE_ID", how="left")
    grouped["WeeksWithFlights"] = grouped["WeeksWithFlights"].clip(lower=1)
    grouped["FlightsPerWeek"] = (
        grouped["Flights"] / grouped["WeeksWithFlights"]).round(1)

    grouped = grouped.sort_values(
        by=["AvgArrivalDelay", "OnTimeRate"], ascending=[True, False]
    ).head(3)
    grouped["On-Time %"] = (grouped["OnTimeRate"] * 100).round(1)
    grouped = grouped.rename(
        columns={
            "Airline_Name": "Airline",
            "AvgArrivalDelay": "Avg Arrival Delay (min)",
        }
    )

    return (
        grouped[
            [
                "Airline",
                "FlightsPerWeek",
                "On-Time %",
                "Avg Arrival Delay (min)",
            ]
        ]
        .rename(columns={"FlightsPerWeek": "Flights / Week"})
        .reset_index(drop=True),
        len(route_df),
        weeks_observed,
    )
