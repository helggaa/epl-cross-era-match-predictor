# EPL Cross-Era Match Predictor

Production-oriented Premier League cross-era match predictor built with FastAPI, PostgreSQL, pandas/scikit-learn/scipy modeling, and React.

## Features
- **Cross-Era Elo & Dixon-Coles Predictor**: Predict home win, draw, and away win probabilities for any two EPL team-seasons (1993-94 to 2025-26).
- **Grounded AI Explanations**: Layer 2 LLM natural language explanations using Anthropic Claude API (completely optional - core prediction runs 100% free & offline).
- **Approximated Event Simulation**: Layer 3 minute-by-minute simulation using Dixon-Coles scoreline sampling and player event rates.
- **Zero Mandatory Paid Services**: 100% self-hostable via Docker Compose.

---

## Quick Start (Phase 0 Setup)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ & npm

### Local Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL via Docker Compose:
   ```bash
   docker-compose up db -d
   ```

3. Setup Python Virtual Environment:
   ```bash
   cd backend
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

4. Run Database Migrations (Alembic):
   ```bash
   alembic upgrade head
   ```

5. Ingest CSV Datasets into Staging Tables:
   ```bash
   python scripts/load_data.py
   ```

6. Run Backend Tests:
   ```bash
   pytest tests/
   ```

---

## Repository Structure
```text
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── migrations/
│   ├── scripts/
│   │   └── load_data.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
├── data/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```
