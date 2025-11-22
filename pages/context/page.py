"""Understanding page layout and content."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .visuals import render_visuals


def render_page(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render the Understanding page."""

    st.subheader("Understanding the Dataset")
    st.write(
        "Start here to understand the size of the dataset, the carriers represented, and to peek at the raw rows."
    )
    render_visuals(df, airports_us)
