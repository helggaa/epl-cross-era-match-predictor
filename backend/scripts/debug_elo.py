import sqlite3
import pandas as pd
from pathlib import Path
import math

db_path = Path(__file__).resolve().parent.parent / "epl_predictor.db"
conn = sqlite3.connect(db_path)

query = """
    SELECT match_id, season, date, home_team, away_team, home_goals, away_goals, result
    FROM staging_matches
    WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
    ORDER BY season ASC, match_id ASC
"""
df = pd.read_sql(query, conn)

DEFAULT_ELO = 1500.0
HOME_ADVANTAGE = 65.0
K_FACTOR = 24.0
REGRESSION_FACTOR = 0.15  # 15% inter-season mean reversion

team_ratings = {}
season_snapshots = {}
team_season_history = {}

current_season = None

for _, match in df.iterrows():
    season = match["season"]
    home_team = match["home_team"]
    away_team = match["away_team"]
    home_goals = match["home_goals"]
    away_goals = match["away_goals"]
    result = match["result"]

    if current_season is not None and season != current_season:
        # Season regression
        for t in team_ratings:
            team_ratings[t] = (1.0 - REGRESSION_FACTOR) * team_ratings[t] + REGRESSION_FACTOR * DEFAULT_ELO

    current_season = season

    if home_team not in team_ratings:
        team_ratings[home_team] = DEFAULT_ELO
    if away_team not in team_ratings:
        team_ratings[away_team] = DEFAULT_ELO

    r_home = team_ratings[home_team]
    r_away = team_ratings[away_team]

    if result == 'H':
        s_home, s_away = 1.0, 0.0
    elif result == 'A':
        s_home, s_away = 0.0, 1.0
    else:
        s_home, s_away = 0.5, 0.5

    exp_home = 1.0 / (1.0 + math.pow(10.0, (r_away - (r_home + HOME_ADVANTAGE)) / 400.0))
    exp_away = 1.0 - exp_home

    goal_diff = abs(home_goals - away_goals)
    mov = math.log(1.0 + goal_diff) if goal_diff > 1 else 1.0

    new_r_home = r_home + K_FACTOR * mov * (s_home - exp_home)
    new_r_away = r_away + K_FACTOR * mov * (s_away - exp_away)

    team_ratings[home_team] = new_r_home
    team_ratings[away_team] = new_r_away

    key_h = (home_team, season)
    key_a = (away_team, season)
    if key_h not in team_season_history:
        team_season_history[key_h] = []
    if key_a not in team_season_history:
        team_season_history[key_a] = []

    team_season_history[key_h].append(new_r_home)
    team_season_history[key_a].append(new_r_away)

for (t, s), ratings in team_season_history.items():
    season_snapshots[(t, s)] = round(ratings[-1], 1)

print("\n--- SAMPLE TEAM ELO RATINGS ---")
test_keys = [
    ("Liverpool", "2019-2020"),
    ("Man City", "2017-2018"),
    ("Arsenal", "2003-2004"),
    ("Chelsea", "2004-2005"),
    ("Cardiff", "2013-2014"),
    ("Charlton", "1998-1999"),
    ("Arsenal", "2025-2026"),
]

for t, s in test_keys:
    print(f"{t} ({s}): {season_snapshots.get((t, s), 'N/A')}")
