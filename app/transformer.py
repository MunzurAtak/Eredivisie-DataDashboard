import pandas as pd


def transform_standings(raw):
    rows = []
    for entry in raw:
        team = entry.get("team", {})
        all_stats = entry.get("all", {})
        goals = all_stats.get("goals", {})
        rows.append(
            {
                "position": entry.get("rank", 0),
                "team_name": team.get("name", ""),
                "team_id": team.get("id", 0),
                "played": all_stats.get("played", 0),
                "wins": all_stats.get("win", 0),
                "draws": all_stats.get("draw", 0),
                "losses": all_stats.get("lose", 0),
                "goals_for": goals.get("for", 0),
                "goals_against": goals.get("against", 0),
                "goal_diff": entry.get("goalsDiff", 0),
                "points": entry.get("points", 0),
                "form": entry.get("form", ""),
            }
        )
    return pd.DataFrame(rows)


def transform_top_scorers(raw):
    rows = []
    for i, entry in enumerate(raw, start=1):
        player = entry.get("player", {})
        stats = entry.get("statistics", [{}])[0]
        goals_data = stats.get("goals", {})
        penalty_data = stats.get("penalty", {})
        rows.append(
            {
                "rank": i,
                "player_name": player.get("name", ""),
                "team_name": stats.get("team", {}).get("name", ""),
                "goals": goals_data.get("total", 0) or 0,
                "assists": goals_data.get("assists", 0) or 0,
                "penalties": penalty_data.get("scored", 0) or 0,
            }
        )
    return pd.DataFrame(rows)


def transform_fixtures(raw):
    rows = []
    for entry in raw:
        fixture = entry.get("fixture", {})
        teams = entry.get("teams", {})
        score = entry.get("goals", {})
        status = fixture.get("status", {}).get("short", "")
        if status != "FT":
            continue
        rows.append(
            {
                "fixture_id": fixture.get("id", 0),
                "date": fixture.get("date", "")[:10],
                "home_team": teams.get("home", {}).get("name", ""),
                "away_team": teams.get("away", {}).get("name", ""),
                "home_goals": score.get("home", 0) or 0,
                "away_goals": score.get("away", 0) or 0,
                "status": status,
            }
        )
    return pd.DataFrame(rows)


def transform_team_stats(raw, team_name):
    if not raw:
        return pd.DataFrame()

    games = raw.get("fixtures", {})
    played = games.get("played", {}).get("total", 1) or 1

    shots = raw.get("shots", {})
    total_shots = (shots.get("total", {}).get("total") or 0)

    possession_raw = raw.get("fixture", {})
    poss_list = raw.get("possession", None)
    if isinstance(poss_list, list):
        poss_values = [int(p) for p in poss_list if p is not None]
        possession_avg = sum(poss_values) / len(poss_values) if poss_values else 0.0
    else:
        possession_avg = 0.0

    cards = raw.get("cards", {})
    yellow_total = sum(
        int(v.get("total") or 0)
        for v in cards.get("yellow", {}).values()
        if isinstance(v, dict)
    )
    red_total = sum(
        int(v.get("total") or 0)
        for v in cards.get("red", {}).values()
        if isinstance(v, dict)
    )

    corners = raw.get("corners", None)
    if isinstance(corners, dict):
        corner_values = []
        for period in corners.values():
            if isinstance(period, dict):
                t = period.get("total")
                if t is not None:
                    corner_values.append(int(t))
        total_corners = sum(corner_values)
    else:
        total_corners = 0

    goals_info = raw.get("goals", {})
    goals_scored = goals_info.get("for", {}).get("total", {}).get("total", 0) or 0
    goals_conceded = goals_info.get("against", {}).get("total", {}).get("total", 0) or 0

    row = {
        "team_name": team_name,
        "shots_per_game": round(total_shots / played, 2),
        "possession_avg": round(possession_avg, 2),
        "yellow_cards": yellow_total,
        "red_cards": red_total,
        "corners_per_game": round(total_corners / played, 2),
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,
    }
    return pd.DataFrame([row])
