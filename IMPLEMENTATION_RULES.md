# EPL Match Predictor

# Implementation Rules

**Version:** 1.0

---

# 1. Purpose

This document defines the engineering rules that must be followed while implementing the EPL Cross-Era Match Predictor.

These rules override convenience.

The goal is a project that is:

* production-oriented;
* performant;
* reproducible;
* inexpensive to operate;
* understandable to recruiters/interviewers;
* statistically honest;
* maintainable;
* free of unnecessary architectural complexity.

---

# 2. Mandatory Technology Stack

Use only:

```text
Backend:
Python
FastAPI
SQLAlchemy
Alembic
PostgreSQL

Modeling:
pandas
scikit-learn
scipy

Frontend:
React
Vite
JavaScript/TypeScript as appropriate
fetch or axios

Infrastructure:
Docker
docker-compose

CI:
GitHub Actions
Ruff
pytest
ESLint

LLM:
Anthropic API
```

Do not add another technology without explicit approval.

---

# 3. Explicitly Forbidden Additions

Do not introduce:

* Next.js
* TensorFlow
* PyTorch
* XGBoost
* Redis
* Celery
* Kafka
* RabbitMQ
* Kubernetes
* GraphQL
* RAG
* vector databases
* LangChain
* unnecessary authentication
* unnecessary microservices

---

# 4. Free-Forever Principle

The core application must remain usable without paying for:

* database hosting;
* backend hosting;
* frontend hosting;
* ML inference;
* queues;
* caches;
* proprietary infrastructure.

The canonical deployment must work through Docker Compose.

Third-party free hosting is optional.

Do not design around a provider's promise that a free tier will exist permanently.

---

# 5. LLM Independence

Prediction must not depend on the LLM.

The following must work without Anthropic:

```text
team selection
season selection
Elo
prediction
feature attribution
prediction storage
simulation
simulation event log
```

Only:

```text
natural-language explanation
natural-language commentary
```

may depend on the LLM.

---

# 6. Never Fabricate Data

Never convert:

```text
missing
```

into:

```text
0
average
estimated
modern equivalent
```

unless explicitly defined by the statistical methodology.

Missing data must remain missing.

---

# 7. Preserve Existing Architecture

Do not rewrite complete modules merely to make them shorter.

Before modifying code:

1. inspect the existing implementation;
2. identify the actual problem;
3. make the smallest correct architectural change;
4. preserve existing functionality;
5. preserve compatibility.

---

# 8. Performance

Do not perform expensive work inside ordinary request paths.

Bad:

```text
POST /predict
    ↓
read 13,401 matches from CSV
    ↓
recalculate Elo
    ↓
fit model
    ↓
predict
```

Good:

```text
data preparation
    ↓
precompute Elo/model state
    ↓
PostgreSQL/local model artifacts
    ↓
POST /predict
    ↓
fast lookup + inference
```

---

# 9. Determinism

Prediction calculations should be deterministic.

Simulation should be random but seedable.

Testing must be able to reproduce simulation behavior.

---

# 10. Database

Use PostgreSQL in production architecture.

Use SQLAlchemy for database access.

Use Alembic for schema changes.

Never manually modify the production schema without a migration.

---

# 11. Indexing

Index fields used repeatedly for:

* team lookup;
* season lookup;
* team-season lookup;
* prediction lookup;
* hypothetical matchup lookup;
* player-season lookup.

Do not create indexes blindly.

---

# 12. API

FastAPI endpoints must:

* validate inputs;
* return appropriate HTTP status codes;
* use typed request/response schemas;
* avoid leaking internal exceptions;
* avoid exposing secrets;
* return useful error messages.

---

# 13. LLM

LLM requests must happen only on the backend.

Never:

```text
React → Anthropic
```

Always:

```text
React → FastAPI → Anthropic
```

API keys must never appear in frontend source code.

---

# 14. LLM Caching

Never repeatedly call the LLM for the same stored prediction narrative.

Layer 2:

```text
prediction_id → cached narrative
```

Layer 3:

```text
simulation_id → commentary
```

---

# 15. LLM Validation

LLM output must be parsed and validated.

Malformed output must not be stored as a successful response.

---

# 16. Statistical Integrity

Do not optimize prediction performance by:

* data leakage;
* future information;
* post-match information;
* fabricated values;
* using outcome information as a pre-match feature.

Cross-era predictions must use only information legitimately available to the selected team-season.

---

# 17. Testing

Every important statistical function needs tests.

At minimum:

```text
Elo update
Elo snapshot
probability normalization
prediction endpoint
invalid input
missing data
simulation seed
event ordering
LLM schema validation
LLM failure
```

---

# 18. CI

Every push must run:

```text
ruff
pytest
eslint
```

The project must not intentionally allow CI failures.

---

# 19. Docker

`docker-compose up` must provide:

```text
api
postgres
```

The API must connect to PostgreSQL through environment configuration.

---

# 20. Environment Variables

Use:

```text
DATABASE_URL
ANTHROPIC_API_KEY
LLM_MODEL
APP_ENV
```

Never commit:

```text
.env
```

Only:

```text
.env.example
```

may be committed.

---

# 21. Logging

Logs must be useful but must not contain:

* API keys;
* database passwords;
* unnecessary personal data;
* entire LLM prompts containing secrets.

---

# 22. Frontend

Keep the frontend intentionally simple.

Use:

```text
useState
useEffect
fetch/axios
```

unless a real need appears.

Do not install a state-management framework simply because the project is a portfolio project.

---

# 23. Simulation Honesty

The UI must visibly state that simulation is approximated.

Never present:

```text
Liverpool 2-1 Arsenal
15' Salah scored
```

as a historical fact.

Present it as:

```text
Simulated result
```

and clearly explain that event timing is statistically approximated.

---

# 24. Phase Discipline

Build in this order:

```text
Phase 0
↓
STOP
↓
User approval
↓
Phase 1
↓
STOP
↓
User approval
↓
Phase 2
↓
STOP
↓
User approval
↓
Phase 3
↓
STOP
↓
User approval
↓
Phase 4
↓
STOP
↓
User approval
↓
Phase 5
```

Never silently continue into the next phase.

---

# 25. Definition of Production Quality

Code is not considered complete merely because it runs.

A completed feature must have:

* correct implementation;
* validation;
* tests;
* useful errors;
* documentation where necessary;
* no obvious data leakage;
* no unnecessary dependency;
* no hard-coded secrets;
* acceptable performance;
* reproducible behavior.

---

# 26. Definition of Free Operation

The project is considered free-by-design when:

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

can run without a paid subscription.

External LLM usage is explicitly outside the guarantee of unlimited free operation because provider pricing is externally controlled.

---

# 27. Engineering Priority

When choosing between alternatives, prioritize:

1. Correctness
2. Data integrity
3. Reproducibility
4. Performance
5. Simplicity
6. Maintainability
7. Cost
8. Additional features

Do not sacrifice correctness merely to make the project appear more impressive.
