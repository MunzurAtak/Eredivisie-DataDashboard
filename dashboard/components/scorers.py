import plotly.express as px
import streamlit as st
from app.queries import get_top_scorers


def render_scorers(conn):
    st.header("Top Scorers")
    df = get_top_scorers(conn, limit=20)
    if df.empty:
        st.warning("No scorer data available. Run the seed script first.")
        return

    top_n = st.slider("Show top N players", min_value=5, max_value=20, value=10)
    df_top = df.head(top_n).sort_values("goals", ascending=True)

    fig = px.bar(
        df_top,
        x="goals",
        y="player_name",
        color="team_name",
        orientation="h",
        hover_data={"player_name": True, "team_name": True, "goals": True, "assists": True},
        labels={"goals": "Goals", "player_name": "Player", "team_name": "Team"},
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Goals",
        legend_title="Team",
        height=max(300, top_n * 35),
    )
    st.plotly_chart(fig, use_container_width=True)
