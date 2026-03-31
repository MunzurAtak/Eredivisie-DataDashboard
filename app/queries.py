import pandas as pd


def get_standings(conn):
    return conn.execute(
        "SELECT * FROM standings ORDER BY position ASC"
    ).df()


def get_top_scorers(conn, limit=10):
    return conn.execute(
        "SELECT * FROM top_scorers ORDER BY goals DESC LIMIT ?", [limit]
    ).df()


def get_team_stats(conn):
    return conn.execute("SELECT * FROM team_stats").df()


def get_fixtures(conn):
    return conn.execute(
        "SELECT * FROM fixtures ORDER BY date DESC"
    ).df()


def get_head_to_head(conn, team_a, team_b):
    return conn.execute(
        """
        SELECT * FROM fixtures
        WHERE (home_team = ? AND away_team = ?)
           OR (home_team = ? AND away_team = ?)
        ORDER BY date DESC
        """,
        [team_a, team_b, team_b, team_a],
    ).df()


def get_form_table(conn):
    return conn.execute(
        "SELECT team_name, form, points FROM standings ORDER BY position ASC"
    ).df()
