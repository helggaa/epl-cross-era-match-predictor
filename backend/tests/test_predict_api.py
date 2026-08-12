import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings


def test_get_teams_endpoint(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/teams")
    assert response.status_code == 200
    teams = response.json()
    assert isinstance(teams, list)
    assert len(teams) > 0
    team_names = [t["team_name"] for t in teams]
    assert "Liverpool" in team_names or "Arsenal" in team_names


def test_get_team_seasons_endpoint(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/team-seasons")
    assert response.status_code == 200
    seasons = response.json()
    assert isinstance(seasons, list)
    assert len(seasons) > 100


def test_predict_endpoint_performance_and_accuracy(client: TestClient, db_session: Session):
    payload = {
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    }

    start_time = time.time()
    response = client.post(f"{settings.API_V1_STR}/predict", json=payload)
    elapsed_ms = (time.time() - start_time) * 1000.0

    assert response.status_code == 200
    data = response.json()

    # Performance requirement check (<200 ms)
    assert elapsed_ms < 200.0, f"Prediction API inference took {elapsed_ms:.2f} ms, exceeding 200 ms target"

    # Schema & probabilities sanity check
    assert "prediction_id" in data
    assert "hypothetical_id" in data
    assert pytest.approx(data["home_win_prob"] + data["draw_prob"] + data["away_win_prob"], abs=1e-3) == 1.0
    assert len(data["top_features"]) > 0

    # Verify DB persistence
    pred_id = data["prediction_id"]
    db_count = db_session.execute(text("SELECT COUNT(*) FROM predictions WHERE prediction_id = :id"), {"id": pred_id}).scalar()
    assert db_count == 1


def test_predict_same_team_same_season_rejected(client: TestClient):
    payload = {
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Liverpool",
        "team_b_season": "2019-2020"
    }
    response = client.post(f"{settings.API_V1_STR}/predict", json=payload)
    assert response.status_code == 400
    assert "same team in the same season" in response.json()["detail"]
