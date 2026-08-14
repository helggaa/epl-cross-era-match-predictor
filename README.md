# EPL Cross-Era Match Predictor ⚽⚡

A statistical machine-learning prediction engine and broadcast-grade simulation interface for hypothetical cross-era Premier League matchups across 34 seasons of English football (1992–93 to 2025–26).

---

## 🌟 Key Features

- **Cross-Era Elo & Dixon-Coles Probability Engine**: Bivariate Poisson model calibrated with chronological Elo ratings to simulate match outcomes, win/draw/loss probabilities, and modeled expected scorelines.
- **TV Studio AI Pundit Breakdown**: Layer 2 tactical analysis powered by Google Gemini (Free Tier) generating multi-bullet pundit breakdowns with tactical micro-tags and football cultural context.
- **Broadcast-Grade UI/UX**: Premier League stadium dark theme with authentic club colors, iconic clash presets (*Invincibles vs Centurions*, *Treble Royale*), and digital LED scoreboards.
- **100% Free & Offline-Resilient**: Core statistical predictions run 100% offline and free without requiring any API keys.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- PostgreSQL (or local SQLite)

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# Run migrations & seed data
alembic upgrade head
python scripts/load_data.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit **`http://localhost:5173`** in your browser.

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

---

## 📁 Architecture

```text
/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # FastAPI endpoint routers (predict, teams, explanation)
│   │   ├── core/           # Configuration & environment settings
│   │   ├── db/             # Database session & models
│   │   ├── ml/             # Dixon-Coles model & Elo rating engine
│   │   └── services/       # Predictor & LLM explanation services
│   ├── migrations/         # Alembic database migrations
│   └── tests/              # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── components/     # MatchupSelector, ProbabilityDisplay, PunditBoard
│   │   ├── services/       # Axios/fetch API layer
│   │   └── utils/          # Team metadata & clash presets
│   └── index.html
├── data/                   # 34 seasons match & player statistics datasets
└── README.md
```

---

## 📄 License
MIT License.
