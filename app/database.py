import os
from datetime import datetime

import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/eredivisie.duckdb")


def get_connection():
    return duckdb.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS standings (
            position INTEGER,
            team_name VARCHAR,
            team_id INTEGER,
            played INTEGER,
            wins INTEGER,
            draws INTEGER,
            losses INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            goal_diff INTEGER,
            points INTEGER,
            form VARCHAR,
            fetched_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS top_scorers (
            rank INTEGER,
            player_name VARCHAR,
            team_name VARCHAR,
            goals INTEGER,
            assists INTEGER,
            penalties INTEGER,
            fetched_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fixtures (
            fixture_id INTEGER,
            date VARCHAR,
            home_team VARCHAR,
            away_team VARCHAR,
            home_goals INTEGER,
            away_goals INTEGER,
            status VARCHAR,
            fetched_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_stats (
            team_name VARCHAR,
            shots_per_game DOUBLE,
            possession_avg DOUBLE,
            yellow_cards INTEGER,
            red_cards INTEGER,
            corners_per_game DOUBLE,
            goals_scored INTEGER,
            goals_conceded INTEGER,
            fetched_at TIMESTAMP
        )
    """)
    conn.close()


def save_dataframe(df, table):
    df = df.copy()
    df["fetched_at"] = datetime.utcnow()
    conn = get_connection()
    conn.execute(f"DELETE FROM {table}")
    conn.register("_df", df)
    conn.execute(f"INSERT INTO {table} SELECT * FROM _df")
    conn.close()


def load_table(table):
    conn = get_connection()
    df = conn.execute(f"SELECT * FROM {table}").df()
    conn.close()
    return df


def last_updated(table):
    try:
        conn = get_connection()
        result = conn.execute(
            f"SELECT MAX(fetched_at) FROM {table}"
        ).fetchone()
        conn.close()
        if result and result[0]:
            return str(result[0])[:19]
        return "Never"
    except Exception:
        return "Never"
