import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
SEASON = os.getenv("SEASON", "2024")
LEAGUE_ID = os.getenv("LEAGUE_ID", "88")
BASE_URL = "https://v3.football.api-sports.io"


def _get(endpoint, params=None):
    headers = {"x-apisports-key": API_KEY}
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(
            f"API request failed: {response.status_code} — {response.text}"
        )
    return response.json().get("response", [])


def fetch_standings():
    data = _get("/standings", params={"league": LEAGUE_ID, "season": SEASON})
    if not data:
        return []
    return data[0]["league"]["standings"][0]


def fetch_top_scorers():
    return _get("/players/topscorers", params={"league": LEAGUE_ID, "season": SEASON})


def fetch_fixtures():
    return _get("/fixtures", params={"league": LEAGUE_ID, "season": SEASON})


def fetch_team_stats(team_id):
    data = _get(
        "/teams/statistics",
        params={"league": LEAGUE_ID, "season": SEASON, "team": team_id},
    )
    return data if isinstance(data, dict) else {}


def rate_limit_remaining():
    headers = {"x-apisports-key": API_KEY}
    response = requests.get(f"{BASE_URL}/status", headers=headers)
    if response.status_code != 200:
        return -1
    account = response.json().get("response", {}).get("requests", {})
    limit = account.get("limit_day", 0)
    used = account.get("current", 0)
    return limit - used
