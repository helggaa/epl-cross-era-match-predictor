# EPL Dataset — Organized Output

Built from your uploaded `datasetBola.zip` (three sources merged: FootyStats/Transfermarkt-style
team-season files, Football-Data.co.uk match+odds files, and Understat xG data).

## Files

### `matches.csv` (13,401 rows, 1993–94 to 2025–26, 33 seasons)
One row per EPL match. Core result fields, half-time score, referee, shots/corners/cards, and
headline odds (Bet365 + market average). Odds columns are empty before bookmakers were tracked
(early-to-mid 1990s) — that's a gap in the source data, not a parsing error.
Key fields: `match_id, season, date, home_team, away_team, home_goals, away_goals, result,
ht_home_goals, ht_away_goals, referee, home_shots, away_shots, home_shots_target,
away_shots_target, home_corners, away_corners, home_yellow, away_yellow, home_red, away_red,
odds_b365_home/draw/away, odds_avg_home/draw/away`

### `team_season_summary.csv` (664 rows)
Derived final-table stats per team per season (computed from `matches.csv`): played, wins, draws,
losses, goals for/against, goal diff, points. This is your quickest cross-era strength proxy —
e.g. filter to `team=Liverpool, season=2019-2020` vs `team=Arsenal, season=2025-2026` to compare
two different eras side by side.

### `player_team_seasons.csv` (24,541 rows, 706 team-season files, 1992–2026)
Squad list per club per season: player name, position, market value, nationality, age, DOB,
height, preferred foot, signed-from club, loan status. Market value is a common squad-strength
proxy for modeling. Note: market values are mostly populated from ~2004 onward; earlier seasons
have sparser Transfermarkt coverage.

### `team_match_xg.csv` (7,718 rows, EPL only, 2014–2024)
Understat xG per team per match: xG, xGA, npxG, deep completions, PPDA (pressing intensity),
result, points. This is the advanced-stats layer — only available from 2014-15 onward because
that's when Understat's xG tracking starts.

### `player_season_xg.csv` (5,864 rows, EPL only, 2014–2024)
Understat player-season aggregates: goals, shots, xG, assists, xA, key passes, minutes, cards.
Good for building `player_event_rates` (goals/90, cards/90) as discussed in the schema.

### `match_forecast_features.csv` (4,180 rows, 2014–2024)
Pre-match aggregated roster stats per match (total squad xG, xA, shots, cards for both sides) plus
Understat's own win/draw/loss forecast probabilities. Useful as a ready-made feature set for your
Layer 1 model or as a benchmark to beat.

### `player_match_stats.csv` (119,148 rows, 2014–2024)
Per-player, per-match stats: minutes played, shots, goals, xG, assists, xA, cards, substitution
in/out flags. **This is the closest thing to event-level data in your dataset — but it's match
totals per player, not a timestamped event log.** There is no minute-of-goal or minute-of-card
field, so you cannot reconstruct "Salah scores in minute 15" from this alone. If you want true
minute-by-minute simulation (Layer 3 from our earlier discussion), you'd still need StatsBomb open
data or a paid Opta/Wyscout feed layered on top of this.

### `teams.csv` (51 rows)
Team ID ↔ name lookup, deduplicated from the Transfermarkt-style club list.

## Known gaps
- **No minute-by-minute events.** Confirmed above — plan your Layer 3 simulator around this being
  a future addition, not something in the current files.
- **xG/advanced stats only cover 2014 onward.** Pre-2014 seasons in `matches.csv` and
  `player_team_seasons.csv` are still usable for a basic win/loss model, just without xG.
- **Odds are sparse before ~2000.** Early seasons in `matches.csv` will have blank odds columns.
- A few Transfermarkt fields (`jerseyNumber`, `status`, `ageAtSeasonStart`) were mostly blank in
  the source and are still included for completeness but expect a lot of missing values.
