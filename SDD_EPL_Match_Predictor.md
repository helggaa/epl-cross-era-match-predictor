# System Design Document (SDD)

# EPL Cross-Era Match Predictor with AI-Generated Explanations

**Author:** Helga Parama Zhafran
**Version:** 2.0
**Status:** Implementation-Ready
**Last Updated:** 2026-08-11

---

## 1. Overview

The EPL Cross-Era Match Predictor is a web application that allows a user to select two English Premier League team-seasons, such as:

* Liverpool 2019–20
* Arsenal 2025–26

and generate a hypothetical matchup between them, even when those team-seasons never actually played each other.

The system provides:

1. Home Win / Draw / Away Win probabilities.
2. A statistically grounded explanation of the prediction.
3. Optional AI-generated natural-language explanations based strictly on structured model output.
4. An approximated, randomized match simulation using the statistical model and available player-level data.
5. Optional LLM-generated commentary for simulated events.
6. Persistent storage of predictions, explanations, and simulation runs.

The system is explicitly designed as a **statistical cross-era comparison system**, not a historical reconstruction engine.

A matchup between two team-seasons is hypothetical. The system does not claim that a real match occurred or that the simulated events represent what would actually have happened.

---

# 2. Core Design Principles

The project follows these principles throughout implementation.

## 2.1 Data honesty

The system must never fabricate missing historical data.

If a statistic does not exist for a particular season:

* do not estimate it using invented values;
* do not silently replace it with a modern value;
* do not make the LLM fill the gap;
* explicitly represent the missing value as unavailable.

Known data gaps include:

* xG/advanced statistics beginning in 2014–15;
* sparse betting odds before approximately 2000;
* sparse market values before approximately 2004;
* absence of timestamped match events.

---

## 2.2 Free-by-design core system

The application must have **no mandatory paid dependency for its core prediction functionality**.

The following must work locally using open-source/free software:

* PostgreSQL
* FastAPI
* Python
* pandas
* scikit-learn
* scipy
* SQLAlchemy
* Alembic
* React
* Vite
* Docker
* Docker Compose
* pytest
* Ruff
* ESLint

The system must not require:

* a paid cloud database;
* paid hosting;
* paid model inference;
* paid vector databases;
* paid queue systems;
* proprietary machine-learning infrastructure.

Third-party free tiers may be used for demonstrations, but the application must not be architecturally dependent on them.

---

## 2.3 LLM is optional to core prediction

The statistical prediction engine must function without an LLM.

The LLM is an explanation/commentary layer.

Therefore:

```text
Prediction
    ↓
Statistical model
    ↓
Prediction result
    ↓
Stored in PostgreSQL
    ↓
Optional LLM explanation
```

The following must remain functional when the LLM provider is unavailable:

* team/season selection;
* Elo lookup;
* probability calculation;
* prediction persistence;
* feature explanations;
* simulation;
* raw simulation event log.

Only LLM-generated prose may become unavailable.

---

## 2.4 No unnecessary architecture

The project is intentionally a modular monolith.

Do not introduce:

* microservices;
* Kubernetes;
* GraphQL;
* Redis;
* Celery;
* Kafka;
* RabbitMQ;
* vector databases;
* RAG;
* service meshes;
* unnecessary authentication systems;
* unnecessary cloud infrastructure.

Every dependency must have a concrete technical reason.

---

## 2.5 Performance-first architecture

Performance optimization should come from good architecture rather than excessive infrastructure.

The system should:

* precompute historical Elo snapshots;
* precompute reusable model parameters;
* avoid loading CSV files during normal prediction requests;
* use indexed PostgreSQL lookups;
* cache LLM responses;
* reuse database connections;
* avoid repeated model fitting;
* avoid unnecessary frontend network calls;
* avoid recomputing deterministic values;
* keep API requests lightweight.

Target:

* ordinary team/season lookup: near-instant;
* normal prediction inference: target under 200 ms excluding LLM generation and cold-start effects;
* simulation: fast enough for interactive repeated execution;
* LLM latency must not block the core prediction endpoint.

---

# 3. Goals

## 3.1 Functional goals

The system must:

* compare arbitrary EPL team-seasons;
* calculate comparable cross-era Elo ratings;
* calculate outcome probabilities;
* provide top contributing prediction factors;
* persist predictions;
* generate grounded explanations;
* cache explanations;
* simulate hypothetical matches;
* attribute simulated events using available player data;
* provide visible simulation disclosure;
* provide reproducible model versions.

---

# 4. Non-Goals

The current system does not attempt to:

* reconstruct real historical matches;
* predict exact real-world future match events;
* provide live EPL fixture ingestion;
* model injuries automatically;
* model transfers automatically;
* model substitutions using real historical event data;
* model VAR events;
* model referee-specific tendencies;
* reconstruct real goal minutes;
* claim that simulated events happened historically;
* use deep learning for the prediction model.

---

# 5. Dataset

The system receives eight CSV datasets.

| Dataset                     | Approx. rows | Coverage          | Primary role                         |
| --------------------------- | -----------: | ----------------- | ------------------------------------ |
| matches.csv                 |       13,401 | 1993–94 → 2025–26 | Match results, Elo, goals/cards/odds |
| team_season_summary.csv     |          664 | 1993–94 → 2025–26 | Season strength/fallback             |
| player_team_seasons.csv     |       24,541 | 1992–93 → 2025–26 | Squad/player-season information      |
| team_match_xg.csv           |        7,718 | 2014–15 → 2023–24 | xG/xGA/advanced match features       |
| player_season_xg.csv        |        5,864 | 2014–15 → 2023–24 | Player attacking rates               |
| match_forecast_features.csv |        4,180 | 2014–15 → 2023–24 | Pre-match aggregates/benchmark data  |
| player_match_stats.csv      |      119,148 | 2014–15 → 2023–24 | Minutes, shots, xG, cards            |
| teams.csv                   |           51 | —                 | Team ID/name lookup                  |

The source dataset must be loaded without silently deleting records because fields are sparse.

---

# 6. Data Quality Rules

## 6.1 Missing values

Missing values must remain missing.

Examples:

```text
NULL
```

must be used instead of:

```text
0
average
estimated value
modern-era replacement
```

unless the source dataset itself explicitly provides such a value.

---

## 6.2 xG boundary

xG-dependent features are available from 2014–15 onward.

If either selected team-season lacks the necessary xG information:

```text
reduced_confidence = true
```

The model must fall back to the available historical goal-rate information.

---

## 6.3 Market value

Market-value information is sparse before approximately 2004.

Missing market-value fields must not be converted to zero.

If market value is unavailable, the feature is excluded from the prediction rather than fabricated.

---

## 6.4 Betting odds

Odds are sparse before approximately 2000.

Odds must never become a mandatory feature.

Missing odds must be represented as missing and excluded from calculations that require them.

---

# 7. System Architecture

```text
┌───────────────────────────┐
│      React + Vite         │
│                           │
│ Team/Season Selection     │
│ Prediction UI             │
│ Explanation UI            │
│ Simulation UI              │
└─────────────┬─────────────┘
              │ HTTP
              ▼
┌───────────────────────────┐
│         FastAPI           │
│                           │
│ REST API                  │
│ Validation                │
│ Prediction orchestration  │
│ Simulation orchestration  │
│ Explanation orchestration │
└──────┬────────┬───────────┘
       │        │
       │        └─────────────────┐
       ▼                          ▼
┌───────────────┐        ┌─────────────────┐
│ Model Layer   │        │ LLM Layer       │
│               │        │                 │
│ Elo           │        │ Anthropic API   │
│ Dixon-Coles   │        │ optional        │
│ Feature calc  │        │ cached          │
│ Simulation    │        │ server-side     │
└───────┬───────┘        └─────────────────┘
        │
        ▼
┌───────────────────────────┐
│       PostgreSQL          │
│                           │
│ Source staging tables     │
│ Elo/model data            │
│ Predictions               │
│ Explanations              │
│ Narratives                │
│ Simulation runs           │
└───────────────────────────┘
```

---

# 8. Backend Technology

Required:

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* pandas
* scikit-learn
* scipy

The prediction model must not use:

* TensorFlow
* PyTorch
* XGBoost
* other deep-learning frameworks

---

# 9. Elo Rating Engine

The system computes time-decayed Elo ratings from `matches.csv`.

The Elo engine:

1. processes matches chronologically;
2. maintains a rating for each team;
3. applies home advantage;
4. updates ratings after each match;
5. applies time decay where specified by the implementation;
6. creates season snapshots.

Each team-season receives one final/snapshot Elo value that can be compared with any other team-season.

Example:

```text
Liverpool 2019–20 → Elo 1987
Arsenal 2025–26  → Elo 1942
```

The rating engine must be deterministic.

Given the same dataset, configuration, and model version, it must produce the same Elo snapshots.

---

# 10. Outcome Model

The primary outcome model is Dixon-Coles.

If Dixon-Coles is not implemented at the beginning of Layer 1, an independent Poisson baseline may temporarily be used as an explicitly versioned intermediate implementation.

The final intended model is Dixon-Coles.

The model uses:

* team attack strength;
* team defensive strength;
* Elo;
* home advantage;
* available xG-derived information for 2014–15 onward;
* season-level goal rates for earlier seasons.

The model must produce:

```text
home_win_prob
draw_prob
away_win_prob
```

The probabilities must sum approximately to:

```text
1.0
```

within an explicitly defined floating-point tolerance.

---

# 11. Feature Availability

Feature engineering must be era-aware.

### Modern era

2014–15 onward may use:

* xG;
* xGA;
* PPDA;
* recent attacking output;
* recent defensive output;
* player-season information;
* market-value information where available.

### Earlier era

Use available:

* goals;
* goals against;
* Elo;
* season-level performance;
* other genuinely available source fields.

The system must not pretend that a pre-2014 team has modern xG statistics.

---

# 12. Prediction API

## POST `/predict`

Input:

```json
{
  "team_a": "Liverpool",
  "season_a": "2019-2020",
  "team_b": "Arsenal",
  "season_b": "2025-2026"
}
```

Response:

```json
{
  "prediction_id": "...",
  "hypothetical_id": "...",
  "team_a": {
    "name": "Liverpool",
    "season": "2019-2020"
  },
  "team_b": {
    "name": "Arsenal",
    "season": "2025-2026"
  },
  "prediction": {
    "home_win_prob": 0.52,
    "draw_prob": 0.26,
    "away_win_prob": 0.22
  },
  "reduced_confidence": false,
  "top_features": []
}
```

The endpoint must persist:

* hypothetical matchup;
* prediction;
* model version;
* contributing features.

---

# 13. Prediction Persistence

## hypothetical_matchups

```sql
CREATE TABLE hypothetical_matchups (
    hypothetical_id TEXT PRIMARY KEY,
    team_a_id TEXT NOT NULL,
    team_a_season TEXT NOT NULL,
    team_b_id TEXT NOT NULL,
    team_b_season TEXT NOT NULL,
    team_a_elo REAL,
    team_b_elo REAL,
    created_at TIMESTAMP NOT NULL
);
```

## predictions

```sql
CREATE TABLE predictions (
    prediction_id TEXT PRIMARY KEY,
    hypothetical_id TEXT NOT NULL
        REFERENCES hypothetical_matchups(hypothetical_id),
    model_version TEXT NOT NULL,
    home_win_prob REAL NOT NULL,
    draw_prob REAL NOT NULL,
    away_win_prob REAL NOT NULL,
    predicted_home_goals REAL,
    predicted_away_goals REAL,
    created_at TIMESTAMP NOT NULL
);
```

## prediction_explanations

```sql
CREATE TABLE prediction_explanations (
    prediction_id TEXT NOT NULL
        REFERENCES predictions(prediction_id),
    feature_name TEXT NOT NULL,
    feature_value REAL,
    shap_value REAL,
    favors TEXT NOT NULL
);
```

`shap_value` is retained because it is part of the existing SDD data contract. If the final model does not use SHAP, the implementation must document what contribution metric is stored instead rather than pretending it is SHAP.

---

# 14. LLM Explanation Layer

The LLM receives structured JSON only.

It must not:

* calculate the prediction;
* invent statistics;
* invent injuries;
* invent transfers;
* invent tactics;
* invent historical facts;
* infer missing information as fact.

The LLM is called server-side.

The API key must never reach React.

---

# 15. LLM Cost and Availability Strategy

The LLM layer is optional.

The application must implement:

```text
prediction → prediction_narratives cache → LLM only if missing
```

The same `prediction_id` must not cause repeated LLM calls.

If a narrative exists:

```text
GET /predict/{prediction_id}/explanation
```

returns the cached narrative.

If the provider is unavailable:

* prediction remains valid;
* cached narrative remains available;
* API returns an explicit unavailable status;
* no fabricated fallback narrative is generated.

The system must never use an LLM to fill missing statistical data.

---

# 16. Simulation Layer

Simulation is an approximation.

The system must clearly distinguish:

### Data-derived/model-derived

* total scoreline distribution;
* player goal shares;
* player card shares;
* team card rates.

### Approximated

* goal timing;
* card timing;
* event sequence.

### Unavailable

* real historical event reconstruction;
* injuries;
* VAR;
* referee-specific behavior;
* real substitutions.

---

# 17. player_event_rates

```sql
CREATE TABLE player_event_rates (
    player_id TEXT NOT NULL,
    season TEXT NOT NULL,
    team_id TEXT NOT NULL,
    goals_per_90 REAL,
    assists_per_90 REAL,
    share_of_team_goals REAL,
    share_of_team_cards REAL,
    minutes_played_total INTEGER
);
```

This table is derived from the available player datasets.

Low-minute players must receive appropriate reliability handling and must not automatically dominate sampling because of unstable rates.

---

# 18. simulation_runs

```sql
CREATE TABLE simulation_runs (
    sim_id TEXT PRIMARY KEY,
    hypothetical_id TEXT NOT NULL
        REFERENCES hypothetical_matchups(hypothetical_id),
    run_number INTEGER NOT NULL,
    final_score_team_a INTEGER NOT NULL,
    final_score_team_b INTEGER NOT NULL,
    event_log JSON NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

---

# 19. Simulation Algorithm

1. Generate a scoreline from the outcome model.
2. Draw goal minutes from the fixed published timing distribution.
3. Select scorers according to player goal-share data.
4. Select assists using available assist-related player rates.
5. Sample cards using team/player card rates.
6. Sort events chronologically.
7. Persist the event log.
8. Optionally send the finalized event log to the Layer 3 LLM.
9. Never allow the LLM to modify the event log.

Every rerun must use fresh random draws.

---

# 20. Simulation Disclosure

Every simulation screen must visibly display a statement equivalent to:

> **Simulated result — scoreline is modeled from historical statistics, while event timing is statistically approximated. This is not a prediction or reconstruction of real match events.**

The disclosure must exist in the actual frontend.

---

# 21. LLM Commentary Layer

The Layer 3 LLM receives:

* Team A;
* Team B;
* finalized event log;
* final score.

It may only transform those events into readable commentary.

It may not:

* add events;
* change minutes;
* change players;
* change score;
* invent tactics;
* invent crowd reactions;
* invent weather;
* invent shots;
* imply that the simulated event was historical fact.

---

# 22. Team APIs

Required:

```text
GET /teams
GET /team-seasons
```

These endpoints populate the React selectors.

Responses should be optimized for lightweight frontend consumption.

---

# 23. Frontend

React + Vite.

Required screens:

### Prediction

* Team A selector
* Team A season selector
* Team B selector
* Team B season selector
* Predict button
* probability display
* confidence/data-coverage display
* explanation sections

### Simulation

* simulation disclosure;
* final score;
* event timeline;
* optional commentary;
* Re-run button.

No state management library is required.

Use:

* `useState`
* `useEffect`

where appropriate.

---

# 24. Database Performance

Important lookup fields must be indexed.

Recommended indexes include:

```text
team_id
season
team_id + season
prediction_id
hypothetical_id
player_id + season
```

The implementation should avoid unnecessary indexes on extremely large staging tables unless profiling shows they are useful.

---

# 25. Data Loading

A single script:

```text
backend/scripts/load_data.py
```

must load all eight source CSVs.

It must:

* validate expected files;
* preserve missing values;
* preserve source rows;
* provide useful error messages;
* support repeatable loading;
* avoid silently dropping malformed rows;
* report rejected rows if rejection is unavoidable;
* provide a summary after loading.

The source CSVs are loaded into staging tables before application-level derived tables are generated.

---

# 26. Derived Data Workflow

The intended workflow is:

```text
CSV files
   ↓
PostgreSQL staging tables
   ↓
Data validation
   ↓
Elo computation
   ↓
Feature preparation
   ↓
Outcome model preparation
   ↓
player_event_rates
   ↓
Prediction-ready data
```

Expensive operations should not happen on every HTTP request.

---

# 27. Reproducibility

Every prediction stores:

```text
model_version
```

The model version must identify the statistical implementation/configuration that generated the result.

A future retraining must not mutate the interpretation of an old prediction.

Instead:

```text
old prediction → old model_version
new prediction → new model_version
```

---

# 28. Randomness

Simulation randomness must be separated from deterministic prediction.

Prediction:

```text
deterministic
```

Simulation:

```text
randomized
```

For debugging/tests, the simulator must support a deterministic seed.

For normal user reruns, fresh randomness should be used.

---

# 29. Error Handling

The API must distinguish:

* invalid team;
* invalid season;
* unavailable team-season;
* missing required prediction data;
* database error;
* model error;
* LLM provider error;
* malformed LLM response.

The system must never return HTTP 200 with fabricated prediction data when the model failed.

---

# 30. Docker

The repository must contain:

```text
docker-compose.yml
```

with:

```text
api
postgres
```

The API must be able to communicate with PostgreSQL using environment variables.

No paid cloud infrastructure is required to run the stack locally.

---

# 31. Configuration

Configuration must be environment-based.

Required examples:

```text
DATABASE_URL
ANTHROPIC_API_KEY
LLM_MODEL
APP_ENV
```

Secrets must never be committed.

`.env.example` must contain placeholders only.

---

# 32. Testing

Backend tests must cover:

* Elo update logic;
* season snapshot logic;
* missing-data behavior;
* probability normalization;
* prediction endpoint;
* invalid team/season;
* prediction persistence;
* simulation reproducibility with a seed;
* simulation event ordering;
* LLM JSON validation;
* LLM failure handling.

Frontend tests may be added where useful.

---

# 33. CI

GitHub Actions must run on every push.

Minimum:

```text
Python lint → Ruff
Python tests → pytest
Frontend lint → ESLint
```

The CI process must fail on errors.

---

# 34. Security

The system must:

* keep API keys server-side;
* validate API inputs;
* use parameterized SQL through SQLAlchemy;
* never expose database credentials;
* never expose the Anthropic key to React;
* avoid logging secrets;
* avoid storing unnecessary user data.

---

# 35. Performance Targets

The primary performance targets are:

| Operation                  | Target                              |
| -------------------------- | ----------------------------------- |
| Team/season lookup         | <100 ms typical                     |
| Prediction inference       | <200 ms target excluding cold start |
| Database prediction lookup | near-instant                        |
| Cached explanation         | near-instant relative to API        |
| Simulation                 | interactive                         |
| LLM generation             | provider-dependent                  |

These are engineering targets, not guarantees across arbitrary hardware.

Performance must be measured rather than claimed.

---

# 36. Free Operation Strategy

The system must be fully runnable using:

```text
Docker Compose
+
PostgreSQL
+
FastAPI
+
React
+
local statistical models
```

No subscription is required to calculate predictions.

The LLM is an optional external capability.

The project must not assume that a particular hosting company's free tier will exist forever.

For permanent zero-cost operation, the documented baseline is:

```text
user-owned/local machine
or
self-hosted hardware
```

rather than dependence on a commercial free tier.

---

# 37. Deployment

A deployment README may document free-tier options where currently available, but such services are considered optional conveniences.

The canonical deployment must remain Docker-based.

The application should therefore be portable to:

* local development;
* a personal server;
* a VPS;
* a cloud VM;
* a container-compatible hosting service.

---

# 38. Limitations

The system has several important limitations:

1. Cross-era Elo assumes the rating scale remains reasonably comparable across eras.
2. Pre-2014 explanations are less detailed because xG/advanced statistics are unavailable.
3. Market values are sparse before approximately 2004.
4. Betting odds are sparse before approximately 2000.
5. Layer 3 is an approximation.
6. Simulated event timing is not derived from this dataset.
7. Player attribution is based on season-level rates rather than event-level shot data.
8. The LLM can fail or become unavailable.
9. Hosted free tiers can change independently of this application.

These limitations must be communicated honestly.

---

# 39. Definition of Done

The project is considered complete only when:

* all eight datasets load successfully;
* PostgreSQL schema is migrated through Alembic;
* Elo is calculated and tested;
* outcome model is implemented and tested;
* `/predict` works;
* predictions persist;
* top contributing features persist;
* Layer 2 explanation works and caches;
* frontend prediction flow works;
* simulation works;
* simulation disclosure is visible;
* Layer 3 commentary works and is grounded;
* Docker Compose runs the stack;
* CI passes;
* README provides reproducible setup instructions;
* the core prediction system works without the LLM provider;
* no required component depends on a paid service.
