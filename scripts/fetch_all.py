import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.database import init_db, save_dataframe
from app.fetcher import (
    fetch_standings,
    fetch_top_scorers,
    fetch_fixtures,
    fetch_team_stats,
)
from app.transformer import (
    transform_standings,
    transform_top_scorers,
    transform_fixtures,
    transform_team_stats,
)


def run():
    print("Initialising database...")
    init_db()

    try:
        print("Fetching standings...")
        raw = fetch_standings()
        df = transform_standings(raw)
        save_dataframe(df, "standings")
        print(f"Standings saved: {len(df)} teams")
    except Exception as e:
        print(f"Standings failed: {e}")
        df = pd.DataFrame()

    try:
        print("Fetching top scorers...")
        raw = fetch_top_scorers()
        df_scorers = transform_top_scorers(raw)
        save_dataframe(df_scorers, "top_scorers")
        print(f"Top scorers saved: {len(df_scorers)} players")
    except Exception as e:
        print(f"Top scorers failed: {e}")

    try:
        print("Fetching fixtures...")
        raw = fetch_fixtures()
        df_fixtures = transform_fixtures(raw)
        save_dataframe(df_fixtures, "fixtures")
        print(f"Fixtures saved: {len(df_fixtures)} matches")
    except Exception as e:
        print(f"Fixtures failed: {e}")

    if df is not None and not df.empty and "team_id" in df.columns:
        all_team_stats = []
        teams = df[["team_id", "team_name"]].drop_duplicates().values.tolist()
        for i, (team_id, team_name) in enumerate(teams, start=1):
            try:
                raw_stats = fetch_team_stats(int(team_id))
                df_stats = transform_team_stats(raw_stats, team_name)
                if not df_stats.empty:
                    all_team_stats.append(df_stats)
                if i % 3 == 0:
                    print(f"Team stats: {i}/{len(teams)} fetched...")
            except Exception as e:
                print(f"Stats failed for {team_name}: {e}")

        if all_team_stats:
            combined = pd.concat(all_team_stats, ignore_index=True)
            save_dataframe(combined, "team_stats")
            print(f"Team stats saved: {len(combined)} teams")
    else:
        print("Skipping team stats — standings not available")

    print("Done. Database ready at data/eredivisie.duckdb")


if __name__ == "__main__":
    run()
