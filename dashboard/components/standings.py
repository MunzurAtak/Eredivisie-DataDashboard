import streamlit as st
from app.queries import get_standings


def _form_badges(form_str):
    badges = []
    colors = {"W": "#2e7d32", "D": "#757575", "L": "#c62828"}
    for char in str(form_str):
        if char in colors:
            badges.append(
                f'<span style="background:{colors[char]};color:white;'
                f'padding:2px 6px;border-radius:3px;margin:1px;'
                f'font-weight:bold;font-size:12px;">{char}</span>'
            )
    return "".join(badges)


def render_standings(conn):
    st.header("League Table")
    df = get_standings(conn)
    if df.empty:
        st.warning("No standings data available. Run the seed script first.")
        return

    display_cols = [
        "position", "team_name", "played", "wins", "draws",
        "losses", "goal_diff", "points", "form",
    ]
    df_display = df[display_cols].copy()

    form_html = df_display["form"].apply(_form_badges)
    df_no_form = df_display.drop(columns=["form"])

    styled = df_no_form.style.background_gradient(
        subset=["points"], cmap="Greens"
    ).format(precision=0)

    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("**Recent form (last 5)**")
    for _, row in df_display.iterrows():
        col1, col2 = st.columns([2, 3])
        with col1:
            st.write(f"{int(row['position'])}. {row['team_name']}")
        with col2:
            st.markdown(_form_badges(row["form"]), unsafe_allow_html=True)

    home_away_cols = {"home_wins", "away_wins", "home_draws", "away_draws"}
    if home_away_cols.issubset(set(df.columns)):
        show_split = st.toggle("Show home/away split")
        if show_split:
            split_cols = ["team_name"] + list(home_away_cols)
            st.dataframe(df[split_cols], use_container_width=True, hide_index=True)
