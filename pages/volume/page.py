"""Flight volume analysis page layout."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .visuals import render_visuals


def render_page(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render the Flight Volume Analysis page."""

    st.subheader("Flight Volume Analysis")
    st.write(
        "Explore how traffic fluctuates over time and which airports handle the heaviest loads."
    )
    render_visuals(df, airports_us)
