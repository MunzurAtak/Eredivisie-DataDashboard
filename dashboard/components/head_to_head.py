import plotly.graph_objects as go
import streamlit as st
from app.queries import get_head_to_head, get_standings


def render_head_to_head(conn):
    st.header("Head to Head")
    standings = get_standings(conn)
    if standings.empty:
        st.warning("No standings data available. Run the seed script first.")
        return

    teams = standings["team_name"].tolist()
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team A", teams, index=0)
    with col2:
        default_b = 1 if teams[0] == team_a else 0
        team_b = st.selectbox("Team B", teams, index=default_b)

    if team_a == team_b:
        st.info("Select two different teams.")
        return

    df = get_head_to_head(conn, team_a, team_b)
    if df.empty:
        st.info("No head-to-head fixtures found between these teams.")
        return

    a_wins = int(
        ((df["home_team"] == team_a) & (df["home_goals"] > df["away_goals"])).sum()
        + ((df["away_team"] == team_a) & (df["away_goals"] > df["home_goals"])).sum()
    )
    b_wins = int(
        ((df["home_team"] == team_b) & (df["home_goals"] > df["away_goals"])).sum()
        + ((df["away_team"] == team_b) & (df["away_goals"] > df["home_goals"])).sum()
    )
    draws = int(len(df)) - a_wins - b_wins

    m1, m2, m3 = st.columns(3)
    m1.metric(f"{team_a} wins", a_wins)
    m2.metric("Draws", draws)
    m3.metric(f"{team_b} wins", b_wins)

    def goal_diff(row):
        if row["home_team"] == team_a:
            return row["home_goals"] - row["away_goals"]
        return row["away_goals"] - row["home_goals"]

    df = df.copy()
    df["goal_diff"] = df.apply(goal_diff, axis=1)
    df["color"] = df["goal_diff"].apply(
        lambda x: "#2e7d32" if x > 0 else ("#757575" if x == 0 else "#c62828")
    )
    df["result_label"] = df["goal_diff"].apply(
        lambda x: f"{team_a} win" if x > 0 else ("Draw" if x == 0 else f"{team_b} win")
    )

    fig = go.Figure()
    for _, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["date"]],
                y=[row["goal_diff"]],
                mode="markers",
                marker=dict(color=row["color"], size=12),
                name=row["result_label"],
                showlegend=False,
                hovertemplate=(
                    f"{row['home_team']} {row['home_goals']} – "
                    f"{row['away_goals']} {row['away_team']}<br>"
                    f"{row['date']}<extra></extra>"
                ),
            )
        )

    fig.add_hline(y=0, line_dash="dot", line_color="grey")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=f"Goal difference (+ = {team_a})",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("All fixtures")
    st.dataframe(
        df[["date", "home_team", "home_goals", "away_goals", "away_team"]],
        use_container_width=True,
        hide_index=True,
    )
