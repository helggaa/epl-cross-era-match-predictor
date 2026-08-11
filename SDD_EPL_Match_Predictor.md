# System Design Document (SDD)
## EPL Cross-Era Match Predictor with AI-Generated Explanations

**Author:** Helga Parama Zhafran
**Version:** 1.0
**Status:** Draft — scoped to available dataset

---

## 1. Overview

A web/mobile application that lets a user select two EPL team-seasons (e.g. *Liverpool
2019–20* vs *Arsenal 2025–26*) — including hypothetical cross-era matchups that never
actually happened — and returns:

1. A predicted outcome (Home Win / Draw / Away Win) with probabilities
2. An AI-generated natural-language explanation of *why* each side is favored or not
3. *(Future work, not covered by current dataset — see §9)* a minute-by-minute simulated
   match commentary with randomized events per re-run

This document scopes the system to what is actually buildable from the dataset already
organized (`epl_dataset_organized.zip`), and explicitly separates what is in-scope now vs.
deferred pending additional data.

---

## 2. Goals & Non-Goals

**Goals**
- Predict outcome probabilities for any two EPL team-seasons, including hypothetical
  cross-era pairings, using a rating system that is comparable across time (Elo)
- Generate a grounded, non-hallucinated natural-language explanation for each prediction
- Persist every prediction and its explanation for later inspection/calibration

**Non-Goals (current version)**
- Minute-by-minute event simulation ("Salah scores at 15′") — no event-timestamped data
  exists in the current dataset; this is deferred to §9 (Future Work)
- Live in-season fixture ingestion — dataset is a static export, not a live feed (can be
  added later via API-Football / football-data.org without changing this design)

---

## 3. Dataset Summary (input to this system)

All tables below come from `epl_dataset_organized.zip`, produced by merging Transfermarkt-
style squad data, Football-Data.co.uk results/odds, and Understat xG data.

| Table | Rows | Season coverage | Role in system |
|---|---|---|---|
| `matches.csv` | 13,401 | 1993–94 → 2025–26 | Elo rating engine input; Dixon-Coles training data |
| `team_season_summary.csv` | 664 | 1993–94 → 2025–26 | Season-level strength snapshot; fallback feature when xG unavailable |
| `player_team_seasons.csv` | 24,541 | 1992–93 → 2025–26 | Squad market-value strength proxy; injury/availability context (manual overlay) |
| `team_match_xg.csv` | 7,718 | 2014–15 → 2023–24 | xG/xGA/PPDA features for recent-era matches |
| `player_season_xg.csv` | 5,864 | 2014–15 → 2023–24 | Player-level goal/xG rates for explanation grounding |
| `match_forecast_features.csv` | 4,180 | 2014–15 → 2023–24 | Pre-match roster aggregates + Understat's own forecast (benchmark) |
| `player_match_stats.csv` | 119,148 | 2014–15 → 2023–24 | Per-player per-match minutes/shots/xG/cards (match-total granularity only) |
| `teams.csv` | 51 | — | ID↔name lookup |

**Known data gaps that shape this design (see full detail in dataset README):**
- No event timestamps anywhere → rules out Layer 3 without new data
- xG/advanced stats only from 2014–15 onward → pre-2014 predictions rely on
  goals/shots/odds only, with a corresponding drop in explanation richness
- Betting odds sparse before ~2000
- Market values sparsely populated before ~2004

---

## 4. System Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐
│   Frontend   │────▶│   Prediction API  │────▶│  Rating Engine     │
│ (team+season │     │  (FastAPI/Flask)  │     │  (Elo, per-season  │
│   picker)    │◀────│                   │◀────│   snapshots)       │
└─────────────┘     └────────┬──────────┘     └───────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Outcome Model     │
                     │ (Dixon-Coles /    │
                     │  gradient boosted │
                     │  classifier)      │
                     └────────┬──────────┘
                              │  probabilities + feature attribution
                              ▼
                     ┌──────────────────┐
                     │ Explanation Layer │
                     │ (LLM call, see    │
                     │  §7 + Prompt doc) │
                     └────────┬──────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Storage layer    │
                     │ (predictions +    │
                     │  explanations)    │
                     └──────────────────┘
```

**Components**

1. **Data layer** — the 8 CSVs above, loaded into a relational store (SQLite for
   prototype, Postgres for production) using the table names as-is.
2. **Rating Engine** — computes a time-decayed Elo rating per team, updated match-by-match
   from `matches.csv`, snapshotted per season so any two team-seasons can be compared even
   if they never played each other.
3. **Outcome Model** — takes the two Elo snapshots (+ supplementary features from
   `team_season_summary.csv` / `team_match_xg.csv` where available) and outputs
   Home/Draw/Away probabilities. Dixon-Coles gives a full scoreline distribution if needed
   later for Layer 3 prep.
4. **Explanation Layer** — packages the model's output + top contributing features into a
   structured JSON payload, sends it to an LLM with the grounding prompt (see companion
   Prompt document), returns "why Team A wins / why Team A loses" narrative for both sides.
5. **Storage layer** — persists every prediction request and its explanation for
   calibration tracking and re-display without recomputation.

---

## 5. Data Model (prediction/explanation tables — new, not in source dataset)

```sql
-- One row per user-generated hypothetical matchup
CREATE TABLE hypothetical_matchups (
    hypothetical_id   TEXT PRIMARY KEY,
    team_a_id         TEXT,
    team_a_season     TEXT,
    team_b_id         TEXT,
    team_b_season     TEXT,
    team_a_elo        REAL,
    team_b_elo        REAL,
    created_at        TIMESTAMP
);

-- One row per prediction run
CREATE TABLE predictions (
    prediction_id      TEXT PRIMARY KEY,
    hypothetical_id     TEXT REFERENCES hypothetical_matchups(hypothetical_id),
    model_version        TEXT,
    home_win_prob         REAL,
    draw_prob              REAL,
    away_win_prob           REAL,
    predicted_home_goals    REAL,   -- optional, from Dixon-Coles
    predicted_away_goals    REAL,
    created_at              TIMESTAMP
);

-- One row per contributing feature per prediction (feeds the LLM prompt)
CREATE TABLE prediction_explanations (
    prediction_id     TEXT REFERENCES predictions(prediction_id),
    feature_name       TEXT,   -- e.g. "elo_diff", "home_xg_avg_last5", "squad_value_diff"
    feature_value        REAL,
    shap_value             REAL,
    favors                  TEXT   -- 'team_a' | 'team_b' | 'neutral'
);

-- Cached LLM output, keyed to a prediction so it isn't regenerated on every view
CREATE TABLE prediction_narratives (
    prediction_id     TEXT REFERENCES predictions(prediction_id),
    llm_model            TEXT,
    narrative_team_a_win  TEXT,
    narrative_team_a_lose TEXT,
    narrative_team_b_win  TEXT,
    narrative_team_b_lose TEXT,
    generated_at            TIMESTAMP
);
```

---

## 6. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | User selects Team A + season and Team B + season from dropdowns populated by `teams.csv` × available seasons |
| FR2 | System computes/retrieves Elo rating for each team-season from `matches.csv` |
| FR3 | System returns Home/Draw/Away probabilities for the matchup |
| FR4 | System returns top contributing features (feature name + direction) for the prediction |
| FR5 | System calls the LLM to generate grounded win/lose narratives for both teams |
| FR6 | System persists the prediction, features, and narrative so repeat views don't recompute |
| FR7 | System flags reduced confidence / reduced explanation detail for pre-2014 matchups (no xG available) |

---

## 7. Explanation Layer Design (Layer 2)

Per the earlier discussion in this conversation: the LLM is **never** given free rein to
invent football narratives. It receives only:

- The three predicted probabilities
- A ranked list of the top 5–8 contributing features (name, value, direction) from
  `prediction_explanations`
- Basic team-season context (season, final league position/points from
  `team_season_summary.csv`, and — if 2014+ — xG figures from `team_match_xg.csv`)

The full system prompt and output-format contract for this call is defined in the
companion document **`llm_prompt_layer2.md`** in this same package — see that file for the
exact prompt template.

---

## 8. Non-Functional Requirements

- **Reproducibility:** Elo/outcome model version is stored with every prediction so
  historical predictions remain explainable even after the model is retrained.
- **Latency:** Elo lookup + outcome model should be near-instant (<200ms); LLM call is the
  bottleneck and should be cached per `prediction_id` (FR6) so repeat views are free.
- **Transparency:** every LLM narrative must be traceable back to the specific
  `prediction_explanations` rows that generated it — no ungrounded claims.
- **Data honesty:** UI must visibly indicate when a matchup involves a pre-2014 season
  (xG-free prediction) vs. 2014+ (full-feature prediction).

---

## 9. Layer 3 — Approximated Minute-by-Minute Simulation

**Honesty constraint:** no table in the current dataset has a timestamped event log (goal
minute, card minute, substitution minute), and none can be derived from what exists. This
section therefore describes an **approximated simulator** — it produces the experience the
user asked for (randomized, re-runnable, minute-stamped events) using real per-player rates
from the dataset combined with published, well-established goal-timing research in place of
match-specific timing data. This must be labeled as simulated/statistical in the UI, not
presented as a reconstruction of how a real match would unfold.

### 9.1 What's real vs. approximated

| Element | Source | Real or approximated |
|---|---|---|
| Total goals per side | Dixon-Coles model on `matches.csv` / `team_match_xg.csv` | Real (modeled) |
| Which player scores/assists | `player_season_xg.csv` — each player's share of team goals/xG that season | Real (data-derived) |
| Which player is carded | `player_match_stats.csv` — player's cards/90 rate that season | Real (data-derived) |
| Referee card tendency | Not in dataset | **Not available** — omit, or use a flat league-average rate as a placeholder |
| *When* in the match events happen | Not in dataset | **Approximated** — generic published goal-timing curve (goals skew toward the last ~15 minutes of each half; this is public football research, not from your data) |
| Red cards / injuries / VAR | Not in dataset | **Not available** — out of scope for this version |

### 9.2 New tables required (not in source dataset — build these)

```sql
-- Precomputed per player, derived from player_season_xg.csv + player_match_stats.csv
CREATE TABLE player_event_rates (
    player_id        TEXT,
    season            TEXT,
    team_id             TEXT,
    goals_per_90         REAL,
    assists_per_90          REAL,
    share_of_team_goals        REAL,   -- this player's goals / team's total goals that season
    share_of_team_cards           REAL,
    minutes_played_total             INTEGER  -- for reliability weighting; low-minute players get wider uncertainty
);

-- One row per simulated re-run of a hypothetical matchup
CREATE TABLE simulation_runs (
    sim_id             TEXT PRIMARY KEY,
    hypothetical_id      TEXT REFERENCES hypothetical_matchups(hypothetical_id),
    run_number             INTEGER,
    final_score_team_a        INTEGER,
    final_score_team_b           INTEGER,
    event_log                       JSON,  -- ordered [{minute, team, player, event_type}]
    created_at                         TIMESTAMP
);
```

### 9.3 Simulation algorithm

1. **Get the scoreline distribution.** Run Dixon-Coles (or the simpler independent-Poisson
   fallback if Dixon-Coles isn't implemented yet) using each team-season's attack/defense
   strength from `team_match_xg.csv` (2014+) or `team_season_summary.csv` goals-for/against
   rate (pre-2014). Sample one final score for this run, e.g. Liverpool 2–1 Arsenal.

2. **Place goals in time.** For each of the sampled goals, draw a minute from a fixed,
   published goal-timing weight curve (heavier weight in minutes 40–45 and 75–90+). This
   curve is the same for every match — it is not derived from your dataset and should be
   documented in-app as a modeling assumption, not a data-backed fact about these specific
   teams.

3. **Assign the scorer.** For the team that scored, sample a player from that team's
   `player_event_rates.share_of_team_goals` for that season (weighted random choice). Assign
   an assist the same way from `share_of_team_goals`-equivalent for assists, excluding the
   scorer.

4. **Place cards.** Independently sample a small number of yellow cards per team (Poisson
   with rate = team's average cards/match that season from `matches.csv` home_yellow/
   away_yellow columns), assign each to a player via `share_of_team_cards`, and give each a
   random minute (uniform distribution is acceptable here — no strong real-world skew to
   model). Red cards: omit by default, or offer as a rare, clearly-labeled toggle using a
   flat low probability — do not present red-card minute as data-grounded.

5. **Write the event log.** Store the ordered `{minute, team, player, event_type}` list in
   `simulation_runs.event_log`. Each call to "re-run the match" repeats steps 1–4 with fresh
   random draws — same two team-seasons, different sampled outcome, exactly the
   re-run-and-get-something-different behavior requested.

6. **(Optional) LLM commentary pass.** Feed the finished event log to the LLM to turn the
   raw `{minute, team, player, event_type}` list into readable match commentary. This reuses
   the grounding pattern from Layer 2 — the LLM narrates only the events actually in the
   log, it does not invent additional match incidents.

### 9.4 UI/UX requirement

Every simulated match view must carry a visible label such as *"Simulated result — scoreline
is modeled from historical stats, event timing is statistically approximated, not a
prediction of real match events."* This is a direct consequence of §9.1 — the timing model
is not real data, and users should not mistake it for one.

### 9.5 Upgrade path

If real event data is later sourced (StatsBomb open data or a paid Opta/Wyscout feed), step
2 (goal-timing curve) and step 4 (card timing) can be replaced with distributions fitted
directly to that data, and steps 3–4 (player attribution) get more accurate with real
minute-level shot maps instead of season-level share-of-goals. No other part of this design
needs to change — the `simulation_runs` table and algorithm shape stay the same.

---

## 10. Technology Stack

Chosen for two constraints: (1) it has to actually work for a solo student project, and
(2) every piece should be something a hiring manager recognizes and can ask you real
questions about in an interview — not an exotic or AI-buzzword stack picked to sound
impressive.

| Layer | Choice | Why this one, specifically |
|---|---|---|
| **Backend API** | Python + **FastAPI** | Python is required anyway for the modeling (pandas, scikit-learn); FastAPI is the standard choice for ML-serving APIs in industry right now (async, auto-generated OpenAPI docs, type-checked with Pydantic) — strong signal on a CV, not just "I used Flask because it's simple" |
| **Database** | **PostgreSQL** | Matches the relational schema in §5/§9.2 directly. Postgres (not SQLite) is what real backend/internship postings ask for — practice with actual constraints, indexes, migrations (Alembic) |
| **Modeling** | **scikit-learn** (Elo is hand-rolled, ~50 lines) + **XGBoost** or a Dixon-Coles implementation in `scipy.optimize` | These are the tools actually used for tabular sports/finance prediction in industry — not TensorFlow. Reserve TensorFlow (your existing strength) for a clearly separate concern if you want one, but don't force a neural net onto a tabular classification problem just to use it |
| **Frontend** | **React** (plain React + Vite, not Next.js, unless you want SSR) | Directly matches the AXA Mandiri internship's stated stack (".NET and React JS") — this project doubles as React practice for that interview, not just a portfolio piece |
| **Mobile (optional, later)** | **Kotlin** (Jetpack Compose) hitting the same FastAPI backend | Reuses your existing Kotlin experience; only worth doing after the web version is solid |
| **LLM integration** | Anthropic API (or OpenAI) called from the FastAPI backend, never from the frontend | Keeps the API key server-side (a real security requirement, and a thing interviewers check for) |
| **Containerization** | **Docker** + docker-compose (API + Postgres) | This is the single highest-leverage "looks professional" addition — a `docker-compose up` that a recruiter or reviewer can actually run is worth more on a CV than most feature additions |
| **CI** | GitHub Actions — lint + test on push | Cheap to add, directly demonstrates you understand a real dev workflow, not just "code that runs on my machine" |
| **Hosting (for a live demo link)** | Backend: Railway or Render (free tier) · Frontend: Vercel · DB: Railway/Supabase Postgres | Free tier is enough for a portfolio project; a live link beats a GitHub repo alone in almost every internship screening |

**Deliberately excluded, and why:**
- **No microservices** — this is a single small API; splitting it into services would be
  resume-padding, not good engineering, and is a common interviewer red flag when asked
  "why did you split it this way?" and the honest answer is "no reason."
- **No Kubernetes** — same reasoning; Docker + a PaaS is the right scale for this project.
- **No vector database / RAG** — Layer 2's LLM call is a structured-JSON-in, prose-out call
  (see `llm_prompt_layer2.md`). Adding a vector DB here would be complexity with no real
  purpose, which is exactly the kind of "AI slop" pattern to avoid — tech should be there
  because the problem needs it, not because it's trendy.
- **No GraphQL** — the API surface here is small and REST maps to it cleanly; GraphQL would
  add complexity without a corresponding benefit for this project's size.

## 11. Risks & Limitations

- Pre-2014 predictions will have visibly thinner explanations (no xG/PPDA) — communicate
  this to the user rather than papering over it
- Cross-era Elo comparison assumes rating scale stays roughly comparable over 30+ years,
  which is a modeling assumption worth validating (e.g. against known era-strength
  consensus) before presenting predictions as authoritative
- Squad market-value data has sparse pre-2004 coverage, limiting its usefulness as a
  strength feature for older seasons
