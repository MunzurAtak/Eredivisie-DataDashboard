import plotly.graph_objects as go
import streamlit as st
from app.queries import get_team_stats

RADAR_AXES = ["shots_per_game", "possession_avg", "goals_scored", "corners_per_game"]
RADAR_LABELS = ["Shots/Game", "Possession %", "Goals Scored", "Corners/Game"]


def _normalise(df, axes):
    normed = {}
    for ax in axes:
        col_max = df[ax].max()
        normed[ax] = (df[ax] / col_max * 10) if col_max > 0 else df[ax] * 0
    return normed


def _radar_trace(row, normed, axes, labels, name, color):
    values = [round(normed[ax][row.name], 2) for ax in axes]
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]
    return go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        name=name,
        line=dict(color=color),
        opacity=0.7,
    )


def render_team_stats(conn):
    st.header("Team Statistics")
    df = get_team_stats(conn)
    if df.empty:
        st.warning("No team stats available. Run the seed script first.")
        return

    teams = sorted(df["team_name"].unique().tolist())
    selected = st.selectbox("Select a team", teams)

    compare = st.checkbox("Compare with another team")
    if compare:
        other_options = [t for t in teams if t != selected]
        selected_b = st.selectbox("Compare with", other_options)
    else:
        selected_b = None

    normed = _normalise(df, RADAR_AXES)
    row_a = df[df["team_name"] == selected].iloc[0]

    fig = go.Figure()
    fig.add_trace(_radar_trace(row_a, normed, RADAR_AXES, RADAR_LABELS, selected, "#1565C0"))

    if selected_b:
        row_b = df[df["team_name"] == selected_b].iloc[0]
        fig.add_trace(_radar_trace(row_b, normed, RADAR_AXES, RADAR_LABELS, selected_b, "#E65100"))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Goals Scored", int(row_a["goals_scored"]))
    c2.metric("Goals Conceded", int(row_a["goals_conceded"]))
    c3.metric("Yellow Cards", int(row_a["yellow_cards"]))
    c4.metric("Red Cards", int(row_a["red_cards"]))
