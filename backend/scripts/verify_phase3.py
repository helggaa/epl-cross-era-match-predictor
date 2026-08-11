import os
import sys
import time
import requests
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings

def main():
    print("=== Phase 3 End-to-End Flow Verification ===")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")

    base_url = "http://127.0.0.1:8000/api/v1"

    # 1. Test GET /teams
    print("\n1. Testing GET /teams...")
    t_res = requests.get(f"{base_url}/teams")
    assert t_res.status_code == 200, f"GET /teams failed: {t_res.status_code}"
    teams = t_res.json()
    print(f"✓ GET /teams returned {len(teams)} teams.")

    # 2. Test GET /team-seasons
    print("\n2. Testing GET /team-seasons...")
    ts_res = requests.get(f"{base_url}/team-seasons")
    assert ts_res.status_code == 200, f"GET /team-seasons failed: {ts_res.status_code}"
    seasons = ts_res.json()
    print(f"✓ GET /team-seasons returned {len(seasons)} team-seasons.")

    # 3. Test POST /predict
    print("\n3. Testing POST /predict (Liverpool 2019-2020 vs Arsenal 2025-2026)...")
    payload = {
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    }
    start = time.time()
    p_res = requests.post(f"{base_url}/predict", json=payload)
    elapsed = (time.time() - start) * 1000.0

    assert p_res.status_code == 200, f"POST /predict failed: {p_res.status_code} - {p_res.text}"
    pred_data = p_res.json()

    print(f"✓ POST /predict completed in {elapsed:.2f} ms.")
    print(f"  Prediction ID: {pred_data['prediction_id']}")
    print(f"  Home Win Prob: {pred_data['home_win_prob']*100:.1f}%")
    print(f"  Draw Prob: {pred_data['draw_prob']*100:.1f}%")
    print(f"  Away Win Prob: {pred_data['away_win_prob']*100:.1f}%")
    print(f"  Expected Scoreline: {pred_data['predicted_home_goals']} - {pred_data['predicted_away_goals']}")
    print(f"  Reduced Confidence Flag: {pred_data['reduced_confidence']}")
    print(f"  Top Features Count: {len(pred_data['top_features'])}")

    # 4. Test GET /predict/{id}/explanation
    pred_id = pred_data['prediction_id']
    print(f"\n4. Testing GET /predict/{pred_id}/explanation...")
    e_res = requests.get(f"{base_url}/predict/{pred_id}/explanation")
    assert e_res.status_code == 200, f"GET explanation failed: {e_res.status_code}"
    exp_data = e_res.json()

    print(f"✓ GET explanation completed.")
    print(f"  Narrative Available: {exp_data['narrative_available']}")
    print(f"  Status Message: {exp_data['status_message']}")

    print("\n=== Phase 3 End-to-End Verification Passed 100%! ===")

if __name__ == "__main__":
    main()
