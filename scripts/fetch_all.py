import sys
import os
import time

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
        from app.queries import get_team_stats
        from app.database import get_connection
        conn = get_connection()
        existing = get_team_stats(conn)
        conn.close()
        already_saved = set(existing["team_name"].tolist()) if not existing.empty else set()

        all_team_stats = []
        teams = df[["team_id", "team_name"]].drop_duplicates().values.tolist()
        pending = [(tid, tname) for tid, tname in teams if tname not in already_saved]
        print(f"Team stats: {len(already_saved)} already saved, {len(pending)} to fetch")
        if pending:
            print("Waiting 65s for per-minute rate limit to reset...")
            time.sleep(65)

        for i, (team_id, team_name) in enumerate(pending, start=1):
            try:
                raw_stats = fetch_team_stats(int(team_id))
                if not raw_stats:
                    print(f"  [{i}/{len(pending)}] {team_name}: empty API response (daily limit?), skipping")
                    continue
                df_stats = transform_team_stats(raw_stats, team_name)
                if not df_stats.empty:
                    all_team_stats.append(df_stats)
                    print(f"  [{i}/{len(pending)}] {team_name}: ok")
                else:
                    print(f"  [{i}/{len(pending)}] {team_name}: transform returned empty")
            except Exception as e:
                print(f"  [{i}/{len(pending)}] {team_name}: failed — {e}")
            time.sleep(7)

        if all_team_stats:
            newly_fetched = pd.concat(all_team_stats, ignore_index=True)
            if not existing.empty:
                existing_cols = [c for c in existing.columns if c != "fetched_at"]
                combined = pd.concat(
                    [existing[existing_cols], newly_fetched], ignore_index=True
                )
            else:
                combined = newly_fetched
            save_dataframe(combined, "team_stats")
            print(f"Team stats saved: {len(combined)} teams total ({len(newly_fetched)} new)")
        elif already_saved:
            print(f"No new teams fetched — {len(already_saved)} teams already in DB")
    else:
        print("Skipping team stats — standings not available")

    print("Done. Database ready at data/eredivisie.duckdb")


if __name__ == "__main__":
    run()
