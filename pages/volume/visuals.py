"""Flight volume visual components."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from theme import COLOR_SEQUENCE, PRIMARY_COLOR

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


def render_visuals(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render flight volume charts."""

    if df.empty:
        st.info("No flight records available to analyze volumes.")
        return

    work_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work_df["FL_DATE"]):
        work_df["FL_DATE"] = pd.to_datetime(work_df["FL_DATE"])

    st.subheader("Top airports & airlines")
    airports_col, airlines_col = st.columns(2)
    with airports_col:
        _render_busiest_airports(work_df, airports_us)
    with airlines_col:
        _render_airline_snapshot(work_df)

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
            color_discrete_sequence=[PRIMARY_COLOR],
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Airline & state comparison")
    airlines_data = _build_airline_comparison(work_df)
    states_data = _build_state_comparison(work_df, airports_us)
    if airlines_data.empty and states_data.empty:
        st.info(
            "Need August 2018 and January 2020 data to compare airlines and states.")
    else:
        left, right = st.columns(2)
        with left:
            _render_airline_period_chart(airlines_data)
        with right:
            _render_state_period_chart(states_data)

    st.subheader("Airline volume shift Sankey")
    sankey_result = _build_airline_sankey_data(work_df)
    if sankey_result is None:
        st.info("Need both August 2018 and January 2020 data to build the Sankey view.")
    else:
        fig = _render_airline_sankey(*sankey_result)
        st.plotly_chart(fig, use_container_width=True)


def _build_airline_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Return airline totals for August 2018 vs January 2020."""

    if df.empty:
        return pd.DataFrame()

    aug_2018 = df[(df["FL_DATE"].dt.year == 2018)
                  & (df["FL_DATE"].dt.month == 8)]
    jan_2020 = df[(df["FL_DATE"].dt.year == 2020)
                  & (df["FL_DATE"].dt.month == 1)]
    if aug_2018.empty and jan_2020.empty:
        return pd.DataFrame()

    def _summarize(data: pd.DataFrame, label: str) -> pd.DataFrame:
        counts = data.groupby("Airline_Name").size(
        ).reset_index(name="Total_Flights")
        counts["Period"] = label
        return counts

    frames = []
    if not aug_2018.empty:
        frames.append(_summarize(aug_2018, "August 2018"))
    if not jan_2020.empty:
        frames.append(_summarize(jan_2020, "January 2020"))

    combined = pd.concat(frames, ignore_index=True)
    top_airlines = (
        combined.groupby("Airline_Name")[
            "Total_Flights"].sum().nlargest(10).index
    )
    return combined[combined["Airline_Name"].isin(top_airlines)]


def _render_airline_period_chart(data: pd.DataFrame) -> None:
    """Plot grouped bar chart for airline volume comparison."""

    if data.empty:
        st.info("Missing data for August 2018 or January 2020 airline comparison.")
        return

    contrast_colors = [COLOR_SEQUENCE[0], COLOR_SEQUENCE[-1]]
    fig = px.bar(
        data,
        x="Airline_Name",
        y="Total_Flights",
        color="Period",
        barmode="group",
        title="Top airlines: Aug 2018 vs Jan 2020",
        labels={"Total_Flights": "Total flights"},
        category_orders={"Period": ["August 2018", "January 2020"]},
        color_discrete_sequence=contrast_colors,
    )
    fig.update_layout(xaxis_title="Airline", yaxis_title="Total flights")
    st.plotly_chart(fig, use_container_width=True)


def _render_busiest_airports(df: pd.DataFrame, airports_us: pd.DataFrame) -> None:
    """Render bar chart for busiest origin airports."""

    if df.empty:
        st.info("No flight records available to rank airports.")
        return
    if airports_us.empty:
        st.info("Airport metadata missing; cannot show names.")
        return

    column = "ORIGIN_AIRPORT"
    top_airports = (
        df.groupby(column)
        .size()
        .reset_index(name="Flights")
        .sort_values("Flights", ascending=False)
        .head(10)
    )
    if top_airports.empty:
        st.info("Not enough airport records to rank volume.")
        return

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
        title="Top 10 origin airports by flights",
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)


def _render_airline_snapshot(df: pd.DataFrame) -> None:
    """Show top airlines by total flights in current dataset."""

    if df.empty:
        st.info("No flights available to rank airlines.")
        return

    flights_by_airline = (
        df.groupby("Airline_Name")
        .size()
        .reset_index(name="Flights")
        .sort_values("Flights", ascending=False)
        .head(10)
    )
    if flights_by_airline.empty:
        st.info("Not enough airline records to visualize volume.")
        return

    fig = px.bar(
        flights_by_airline,
        x="Flights",
        y="Airline_Name",
        orientation="h",
        text="Flights",
        title="Top airlines by flight count",
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)


def _build_state_comparison(df: pd.DataFrame, airports_us: pd.DataFrame) -> pd.DataFrame:
    """Return flights per state for the two target periods."""

    if df.empty or airports_us.empty:
        return pd.DataFrame()

    airport_states = airports_us[["IATA", "State"]].dropna()
    merged = df.merge(airport_states, left_on="ORIGIN_AIRPORT",
                      right_on="IATA", how="left")
    merged = merged.dropna(subset=["State"])

    aug_2018 = merged[(merged["FL_DATE"].dt.year == 2018)
                      & (merged["FL_DATE"].dt.month == 8)]
    jan_2020 = merged[(merged["FL_DATE"].dt.year == 2020)
                      & (merged["FL_DATE"].dt.month == 1)]
    if aug_2018.empty and jan_2020.empty:
        return pd.DataFrame()

    def _summarize(data: pd.DataFrame, label: str) -> pd.DataFrame:
        counts = data.groupby("State").size().reset_index(name="Total_Flights")
        counts["Period"] = label
        return counts

    frames = []
    if not aug_2018.empty:
        frames.append(_summarize(aug_2018, "August 2018"))
    if not jan_2020.empty:
        frames.append(_summarize(jan_2020, "January 2020"))

    combined = pd.concat(frames, ignore_index=True)
    top_states = (
        combined.groupby("State")["Total_Flights"].sum().nlargest(10).index
    )
    return combined[combined["State"].isin(top_states)]


def _render_state_period_chart(data: pd.DataFrame) -> None:
    """Plot grouped bar chart for state-level flight comparison."""

    if data.empty:
        st.info("Missing data for August 2018 or January 2020 state comparison.")
        return

    contrast_colors = [COLOR_SEQUENCE[0], COLOR_SEQUENCE[-1]]
    fig = px.bar(
        data,
        x="State",
        y="Total_Flights",
        color="Period",
        barmode="group",
        title="Top states: Aug 2018 vs Jan 2020",
        labels={"Total_Flights": "Total flights"},
        category_orders={"Period": ["August 2018", "January 2020"]},
        color_discrete_sequence=contrast_colors,
    )
    fig.update_layout(xaxis_title="State", yaxis_title="Total flights")
    st.plotly_chart(fig, use_container_width=True)


def _build_airline_sankey_data(df: pd.DataFrame):
    """Prepare node labels and links for airline Sankey comparing 2018 vs 2020."""

    aug = df[(df["FL_DATE"].dt.year == 2018) & (df["FL_DATE"].dt.month == 8)]
    jan = df[(df["FL_DATE"].dt.year == 2020) & (df["FL_DATE"].dt.month == 1)]
    if aug.empty or jan.empty:
        return None

    def summarize(data: pd.DataFrame) -> pd.DataFrame:
        counts = data.groupby("Airline_Name").size(
        ).reset_index(name="Flight_Count")
        counts = counts.sort_values("Flight_Count", ascending=False)
        top = counts.head(10)
        others = pd.DataFrame(
            [{"Airline_Name": "Others",
                "Flight_Count": counts["Flight_Count"].iloc[10:].sum()}]
        )
        return pd.concat([top, others], ignore_index=True)

    data_2018 = summarize(aug)
    data_2020 = summarize(jan)

    node_labels_2018 = [f"2018: {name}" for name in data_2018["Airline_Name"]]
    node_labels_2020 = [f"2020: {name}" for name in data_2020["Airline_Name"]]
    all_labels = node_labels_2018 + node_labels_2020
    node_to_id = {label: idx for idx, label in enumerate(all_labels)}

    def get_count(data: pd.DataFrame, airline: str) -> int:
        return int(data.loc[data["Airline_Name"] == airline, "Flight_Count"].iloc[0])

    airlines_2018 = [
        name for name in data_2018["Airline_Name"] if name != "Others"]
    airlines_2020 = [
        name for name in data_2020["Airline_Name"] if name != "Others"]

    links = []
    for airline in set(airlines_2018) & set(airlines_2020):
        source = node_to_id[f"2018: {airline}"]
        target = node_to_id[f"2020: {airline}"]
        count_2018 = get_count(data_2018, airline)
        count_2020 = get_count(data_2020, airline)
        links.append({"source": source, "target": target, "value": count_2020})
        if count_2018 > count_2020:
            links.append(
                {
                    "source": source,
                    "target": node_to_id["2020: Others"],
                    "value": count_2018 - count_2020,
                }
            )

    for airline in set(airlines_2020) - set(airlines_2018):
        links.append(
            {
                "source": node_to_id["2018: Others"],
                "target": node_to_id[f"2020: {airline}"],
                "value": get_count(data_2020, airline),
            }
        )

    for airline in set(airlines_2018) - set(airlines_2020):
        links.append(
            {
                "source": node_to_id[f"2018: {airline}"],
                "target": node_to_id["2020: Others"],
                "value": get_count(data_2018, airline),
            }
        )

    others_flow = get_count(data_2020, "Others") - sum(
        l["value"] for l in links if l["source"] == node_to_id["2018: Others"]
    )
    links.append(
        {
            "source": node_to_id["2018: Others"],
            "target": node_to_id["2020: Others"],
            "value": max(others_flow, 0),
        }
    )

    return node_labels_2018, node_labels_2020, all_labels, links


def _render_airline_sankey(
    node_labels_2018: list[str],
    node_labels_2020: list[str],
    all_node_labels: list[str],
    links: list[dict],
) -> go.Figure:
    """Build Sankey figure with sorted nodes and fixed layout."""

    left_indices = list(range(len(node_labels_2018)))
    right_indices = list(range(len(node_labels_2018), len(all_node_labels)))

    totals_left = {i: 0 for i in left_indices}
    totals_right = {i: 0 for i in right_indices}
    for link in links:
        if link["source"] in totals_left:
            totals_left[link["source"]] += link["value"]
        if link["target"] in totals_right:
            totals_right[link["target"]] += link["value"]

    def sort_indices(indices: list[int], totals: dict[int, int]) -> list[int]:
        others = [idx for idx in indices if "Others" in all_node_labels[idx]]
        regular = [idx for idx in indices if idx not in others]
        regular.sort(key=lambda idx: totals.get(idx, 0), reverse=True)
        return regular + others

    left_sorted = sort_indices(left_indices, totals_left)
    right_sorted = sort_indices(right_indices, totals_right)
    new_order = left_sorted + right_sorted
    index_map = {old: new for new, old in enumerate(new_order)}
    remapped_links = [
        {"source": index_map[l["source"]],
            "target": index_map[l["target"]], "value": l["value"]}
        for l in links
    ]

    def coordinates(count: int, x_pos: float) -> tuple[list[float], list[float]]:
        if count == 0:
            return [], []
        y = np.linspace(0.05, 0.95, count).tolist() if count > 1 else [0.5]
        return [x_pos] * count, y

    left_x, left_y = coordinates(len(left_sorted), 0.05)
    right_x, right_y = coordinates(len(right_sorted), 0.95)
    node_x = left_x + right_x
    node_y = left_y + right_y

    palette = (BLUE_GRADIENT *
               ((len(new_order) // len(BLUE_GRADIENT)) + 1))[: len(new_order)]

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=30,
                    thickness=35,
                    line=dict(color="black", width=0.5),
                    label=[all_node_labels[idx] for idx in new_order],
                    color=palette,
                    x=node_x,
                    y=node_y,
                ),
                link=dict(
                    source=[l["source"] for l in remapped_links],
                    target=[l["target"] for l in remapped_links],
                    value=[l["value"] for l in remapped_links],
                ),
            )
        ]
    )
    fig.update_layout(
        title="Airline flight volume shift: 2018 vs 2020", height=800)
    return fig
