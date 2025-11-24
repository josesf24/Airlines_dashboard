"""Global styling helpers for the Streamlit app."""

from __future__ import annotations

from copy import deepcopy
from typing import Sequence

import plotly.express as px
import plotly.io as pio
import streamlit as st

PRIMARY_COLOR = "#60A5FA"
ACCENT_BLUE = "#38BDF8"
ACCENT_GREEN = "#34D399"
ACCENT_ORANGE = "#F97316"
ACCENT_PINK = "#F472B6"
ACCENT_YELLOW = "#FACC15"
TEXT_COLOR = "#E2E8F0"
MUTED_TEXT_COLOR = "#94A3B8"
APP_BACKGROUND = "#0F172A"
CARD_BACKGROUND = "#14213D"
SIDEBAR_BACKGROUND = "#0B1120"

COLOR_SEQUENCE = [
    PRIMARY_COLOR,
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_ORANGE,
    ACCENT_PINK,
    ACCENT_YELLOW,
]
BLUE_GRADIENT = [
    "#001933",
    "#00264D",
    "#003366",
    "#004080",
    "#004C99",
    "#0059B3",
    "#0066CC",
    "#3385D6",
    "#66A3E0",
    "#99C2EB",
    "#CCE0F5",
]


def init_theme() -> None:
    """Apply Plotly defaults and inject global CSS for a cohesive UI."""

    _configure_plotly()
    _inject_streamlit_css()


def _configure_plotly() -> None:
    """Create and register a custom Plotly template."""

    template = deepcopy(pio.templates["plotly_white"])
    layout = template.layout
    layout.paper_bgcolor = APP_BACKGROUND
    layout.plot_bgcolor = "rgba(0, 0, 0, 0)"
    layout.font.color = TEXT_COLOR
    layout.font.family = "Inter, 'Segoe UI', sans-serif"
    layout.title.font.color = TEXT_COLOR
    layout.legend.font.color = TEXT_COLOR
    layout.colorway = COLOR_SEQUENCE
    layout.margin = dict(l=40, r=30, t=60, b=40)

    pio.templates["airline_theme"] = template
    pio.templates.default = "airline_theme"
    px.defaults.template = "airline_theme"
    px.defaults.color_discrete_sequence = COLOR_SEQUENCE
    px.defaults.color_continuous_scale = BLUE_GRADIENT


def _inject_streamlit_css() -> None:
    """Inject custom CSS to align Streamlit widgets with the dashboard theme."""

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {APP_BACKGROUND};
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        header {{
            background: transparent;
        }}
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BACKGROUND};
            color: {TEXT_COLOR};
            padding-top: 2rem;
        }}
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] span {{
            color: {TEXT_COLOR};
        }}
        [data-testid="stSidebar"] .sidebar-subtext {{
            color: {MUTED_TEXT_COLOR};
            font-size: 0.9rem;
            margin-bottom: 1.2rem;
            display: block;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {{
            display: none;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] > label {{
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0.75rem;
            padding: 0.55rem 0.65rem;
            margin-bottom: 0.35rem;
            background: rgba(255, 255, 255, 0.02);
            transition: all 0.2s ease;
            display: block;
            position: relative;
            overflow: hidden;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{
            display: none;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] > label:not(:has(input:checked)):hover {{
            border-color: {PRIMARY_COLOR};
            background: rgba(96, 165, 250, 0.15);
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
            border-color: {ACCENT_BLUE};
            background: rgba(56, 189, 248, 0.45);
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.08);
            transform: translateX(2px);
            color: {TEXT_COLOR};
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)::before {{
            content: "";
            position: absolute;
            inset: 0;
            border-left: 3px solid {PRIMARY_COLOR};
            border-radius: inherit;
            pointer-events: none;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) span,
        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {{
            color: {TEXT_COLOR};
            font-weight: 600;
        }}
        .active-nav-label {{
            color: {ACCENT_BLUE};
            font-weight: 600;
            margin-bottom: 0.15rem;
        }}
        .themed-metric div[data-testid="stMetricValue"],
        .themed-metric div[data-testid="stMetricLabel"] {{
            color: {TEXT_COLOR};
        }}
        .themed-metric {{
            background: {CARD_BACKGROUND};
            border-radius: 1rem;
            padding: 0.85rem 1rem;
        }}
        .stDataFrame, .stTable {{
            color: {TEXT_COLOR};
        }}
        .themed-caption {{
            color: {MUTED_TEXT_COLOR};
            font-size: 0.9rem;
            margin-top: 0.3rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


__all__: Sequence[str] = [
    "init_theme",
    "PRIMARY_COLOR",
    "ACCENT_BLUE",
    "ACCENT_GREEN",
    "ACCENT_ORANGE",
    "ACCENT_PINK",
    "ACCENT_YELLOW",
    "COLOR_SEQUENCE",
    "BLUE_GRADIENT",
]
