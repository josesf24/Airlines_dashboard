"""Delay Analysis page layout and content."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .visuals import render_visuals


def render_page(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render the Delay Analysis page."""

    st.subheader("Delay Analysis")
    st.write(
        "Track where and when delays emerge, and compare weather-driven disruptions with other causes."
    )
    render_visuals(df, airports_us)
