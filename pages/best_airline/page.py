"""Best Airline Suggester page layout and content."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .visuals import render_visuals


def render_page(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render the Best Airline Suggester page."""

    st.subheader("Best Airline Suggester")
    st.write(
        "Pick a route to see which carriers deliver the most reliable arrival performance."
    )
    render_visuals(df, airports_us)
