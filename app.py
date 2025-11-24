"""Streamlit entrypoint for the airline visualization project."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Tuple

import pandas as pd
import streamlit as st

from preprocess import load_preprocessed_data
from pages.context import render_page as render_context_page
from pages.volume import render_page as render_volume_page
from pages.delay import render_page as render_delay_page
from pages.best_airline import render_page as render_best_airline_page
from theme import init_theme

st.set_page_config(
    page_title="US Airline Operations",
    page_icon="✈️",
    layout="wide",
)


@st.cache_data(show_spinner="Loading flight and airport data...")
def get_data(dataset_path: str | Path = "Airline_dataset.csv") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Cache the preprocessing step so Streamlit reloads stay fast."""

    return load_preprocessed_data(dataset_path)


PAGE_DEFINITIONS: Tuple[Tuple[str, str, str, Callable[[pd.DataFrame, pd.DataFrame], None]], ...] = (
    ("📘", "Understanding the Dataset",
     "Explore coverage, scale, and on-time performance.", render_context_page),
    ("📊", "Flight Volume Analysis",
     "Track volumes by airport, state, and year-over-year shifts.", render_volume_page),
    ("⏱️", "Delay Analysis",
     "Compare temporal delay patterns and magnitude by airline.", render_delay_page),
    ("🛫", "Best Airline Suggester",
     "Get carrier recommendations for any origin-destination pair.", render_best_airline_page),
)


def main() -> None:
    init_theme()
    df, airports_us = get_data()

    st.title("Flight Reliability & Resilience Dashboard")
    options = [f"{icon}  {title}" for icon, title, _, _ in PAGE_DEFINITIONS]
    choice = st.sidebar.radio(
        label="", options=options, index=0, key="page_selector")

    icon, title, description, renderer = next(
        item for item in PAGE_DEFINITIONS if f"{item[0]}  {item[1]}" == choice
    )
    st.sidebar.markdown(
        f"<div class='active-nav-label'>{title}</div>", unsafe_allow_html=True)
    st.sidebar.caption(description)

    renderer(df, airports_us)


if __name__ == "__main__":
    main()
