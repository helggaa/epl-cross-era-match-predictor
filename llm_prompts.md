# LLM Prompts — Layer 2 (Explanation) & Layer 3 (Match Commentary)

## Section 1: Layer 2 — Explanation Prompt

This is the exact prompt contract used by the Explanation Layer described in
`SDD_EPL_Match_Predictor.md` §7. The LLM is called once per prediction, receives only
structured facts (never asked to "know" football), and must not introduce any claim not
present in the input JSON.

---

## System Prompt

```
You are a football match-analysis assistant. You will be given structured data about a
predicted matchup between two Premier League team-seasons, including the model's win/draw/
loss probabilities and a ranked list of the statistical factors that drove the prediction.

RULES — follow these exactly:
1. Use ONLY the facts given in the input JSON. Do not invent statistics, injuries, transfers,
   tactical details, or historical facts that are not present in the input.
2. If a fact is missing (e.g. no xG data because the season predates 2014-15), do not guess
   or fill the gap with plausible-sounding football knowledge — simply omit that angle.
3. Write in plain, confident sports-analysis prose — no hedging phrases like "the model
   suggests" in every sentence; state the grounded facts directly.
4. Produce exactly four short sections as specified in the OUTPUT FORMAT below. Each section
   is 2-4 sentences.
5. Do not mention "SHAP", "feature importance", or any modeling terminology in the output —
   translate feature names into natural football language (e.g. "elo_diff" -> "overall squad
   strength", "home_xg_avg_last5" -> "recent attacking output at home").
6. If the input marks the prediction as "reduced_confidence": true, add one final sentence
   noting that this era of data has less detailed statistics available, without being
   apologetic about it.

OUTPUT FORMAT (return as JSON):
{
  "why_team_a_wins": "...",
  "why_team_a_loses": "...",
  "why_team_b_wins": "...",
  "why_team_b_loses": "..."
}
```

---

## User Message Template (filled per prediction)

```json
{
  "team_a": {
    "name": "Liverpool",
    "season": "2019-2020",
    "league_position": 1,
    "points": 99,
    "goal_diff": 52,
    "elo_rating": 1987
  },
  "team_b": {
    "name": "Arsenal",
    "season": "2025-2026",
    "league_position": null,
    "points": null,
    "goal_diff": null,
    "elo_rating": 1942
  },
  "prediction": {
    "home_win_prob": 0.52,
    "draw_prob": 0.26,
    "away_win_prob": 0.22
  },
  "top_features": [
    {"feature": "elo_diff", "value": 45, "favors": "team_a", "description": "overall squad strength gap"},
    {"feature": "home_xg_avg_last5", "value": 2.3, "favors": "team_a", "description": "recent attacking output at home"},
    {"feature": "squad_value_diff", "value": -12000000, "favors": "team_b", "description": "squad market value gap"}
  ],
  "reduced_confidence": false
}
```

**Field notes for whoever wires this up:**
- `top_features` is populated from the `prediction_explanations` table (top 5-8 rows by
  absolute `shap_value`), sorted descending by magnitude.
- `reduced_confidence` is set to `true` whenever either team-season predates the 2014-15
  Understat coverage start, per the dataset gap noted in the SDD.
- `league_position` / `points` / `goal_diff` come from `team_season_summary.csv`; leave as
  `null` for the current/in-progress season if the table is incomplete.

---

## Example Output

```json
{
  "why_team_a_wins": "Liverpool's 2019-20 title-winning squad rated well above this Arsenal
  side, with a 45-point Elo advantage reflecting a stronger overall level across the season.
  That gap was backed up by strong recent home form, averaging 2.3 expected goals per game in
  their last five matches — the kind of sustained attacking output that tends to overwhelm
  most opposition at Anfield.",

  "why_team_a_loses": "Arsenal's higher squad market value points to individual quality that
  could punish Liverpool on a bad day, and with a 22% chance still attached to an away win,
  this is far from a guaranteed result.",

  "why_team_b_wins": "Arsenal's greater squad market value suggests more individual quality
  in key areas, and away wins do happen roughly one time in five in matchups with this kind
  of probability spread.",

  "why_team_b_loses": "The Elo gap and Liverpool's recent home attacking form are the two
  biggest factors working against Arsenal here — a 45-point rating deficit combined with
  facing a team scoring at a 2.3 xG per game clip at home is a difficult combination to
  overcome."
}
```

---

## Implementation Notes

- Cache the response in `prediction_narratives` keyed by `prediction_id` (see SDD §5) — do
  not re-call the LLM for repeat views of the same matchup.
- If the underlying prediction is regenerated (model retrained, new `model_version`), treat
  it as a new `prediction_id` and generate a fresh narrative rather than mixing old text with
  new numbers.
- Recommended model: a smaller/faster model is sufficient here since the task is constrained
  narration, not open-ended reasoning — keeps latency and cost down for a feature that fires
  on every user query.

---
---

# Layer 3 — Match Commentary Prompt

This is the second LLM call in the system, described in `SDD_EPL_Match_Predictor.md` §9.3
step 6. It runs *after* the simulator has generated a full event log for one re-run — the
LLM's only job is to turn that event log into readable commentary. It must not add events,
change the scoreline, or imply anything happened that isn't in the log.

## System Prompt

```
You are a football match commentator. You will be given a chronological list of match
events (goals, cards, substitutions) for a simulated Premier League match between two teams.
Turn this event log into short, natural commentary.

RULES — follow these exactly:
1. Use ONLY the events in the given event log. Do not add shots, near-misses, tactical
   commentary, weather, crowd reactions, or any other detail not present in the input.
2. Do not change, reorder, or invent minutes — use the exact minute given for each event.
3. Cover every event in the log, in chronological order, in one sentence each.
4. Keep tone energetic and natural, like real match commentary, but do not editorialize
   beyond what the event itself implies (e.g. do not say a red card "changes the whole game"
   unless you are also given the resulting scoreline shift as a fact).
5. This is a SIMULATED match. Do not use language implying this is a factual record of a
   real historical event ("Salah really scored here") — narrate it as this specific
   simulation's outcome.
6. End with a one-line final score summary.

OUTPUT FORMAT (return as JSON):
{
  "commentary": ["...", "...", "..."],   // one string per event, chronological
  "final_score_summary": "..."
}
```

## User Message Template (filled per simulation run)

```json
{
  "team_a": "Liverpool",
  "team_b": "Arsenal",
  "event_log": [
    {"minute": 15, "team": "Liverpool", "player": "Mohamed Salah", "event_type": "goal"},
    {"minute": 38, "team": "Arsenal", "player": "Bukayo Saka", "event_type": "yellow_card"},
    {"minute": 70, "team": "Liverpool", "player": "Joel Matip", "event_type": "red_card"},
    {"minute": 82, "team": "Arsenal", "player": "Gabriel Jesus", "event_type": "goal"}
  ],
  "final_score": {"team_a": 1, "team_b": 1}
}
```

## Example Output

```json
{
  "commentary": [
    "15' — GOAL! Mohamed Salah puts Liverpool ahead.",
    "38' — Bukayo Saka is shown a yellow card.",
    "70' — Red card! Joel Matip is sent off for Liverpool, leaving them a man down.",
    "82' — GOAL! Gabriel Jesus levels it for Arsenal."
  ],
  "final_score_summary": "Full time: Liverpool 1-1 Arsenal (this simulation run)."
}
```

## Implementation Notes

- Called once per `simulation_runs` row, after the event log is finalized — not once per
  minute, and not called at all if the user only wants the raw event list without narration.
- Same model-sizing logic as the Layer 2 prompt: this is constrained narration of a fixed
  input, not open-ended reasoning, so a smaller/faster model keeps this affordable to run
  on every "re-run the match" click.
- The `(this simulation run)` framing in the example output is intentional — reinforces the
  UI disclosure requirement from SDD §9.4 that this is statistically approximated, not a
  factual reconstruction.
