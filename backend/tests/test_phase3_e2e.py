import pytest
from fastapi.testclient import TestClient
from app.core.config import settings


def test_phase3_full_frontend_flow_integration(client: TestClient):
    """
    Simulate complete frontend app flow:
    1. Load teams list (GET /teams)
    2. Load team seasons (GET /team-seasons)
    3. Trigger prediction (POST /predict)
    4. Fetch Layer 2 explanation (GET /predict/{id}/explanation)
    """
    # Step 1: Fetch teams
    res_teams = client.get(f"{settings.API_V1_STR}/teams")
    assert res_teams.status_code == 200
    teams = res_teams.json()
    assert len(teams) > 0

    # Step 2: Fetch team seasons
    res_seasons = client.get(f"{settings.API_V1_STR}/team-seasons")
    assert res_seasons.status_code == 200
    seasons = res_seasons.json()
    assert len(seasons) > 0

    # Step 3: Trigger prediction (Liverpool 2019-2020 vs Arsenal 2025-2026)
    pred_payload = {
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    }
    res_pred = client.post(f"{settings.API_V1_STR}/predict", json=pred_payload)
    assert res_pred.status_code == 200
    pred = res_pred.json()

    assert "prediction_id" in pred
    assert pred["home_win_prob"] > 0
    assert pred["draw_prob"] > 0
    assert pred["away_win_prob"] > 0
    assert pred["predicted_home_goals"] is not None
    assert pred["predicted_away_goals"] is not None
    assert "reduced_confidence" in pred
    assert len(pred["top_features"]) > 0

    # Step 4: Fetch Layer 2 explanation separately
    pred_id = pred["prediction_id"]
    res_exp = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
    assert res_exp.status_code == 200
    exp = res_exp.json()
    assert "narrative_available" in exp
