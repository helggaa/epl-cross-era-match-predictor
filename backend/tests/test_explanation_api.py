import json
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.models.app_models import PredictionNarrative


def test_predict_works_without_llm_key(client: TestClient):
    """Test that POST /predict works 100% without any LLM key configured"""
    with patch.object(settings, "GEMINI_API_KEY", None), \
         patch.object(settings, "GOOGLE_API_KEY", None), \
         patch.object(settings, "ANTHROPIC_API_KEY", None):
        payload = {
            "team_a_id": "Liverpool",
            "team_a_season": "2019-2020",
            "team_b_id": "Arsenal",
            "team_b_season": "2025-2026"
        }
        response = client.post(f"{settings.API_V1_STR}/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction_id" in data
        assert data["home_win_prob"] > 0


def test_explanation_unconfigured_fallback(client: TestClient):
    """Test that GET /explanation returns graceful fallback when API key is missing"""
    payload = {
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    }
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json=payload)
    pred_id = pred_res.json()["prediction_id"]

    with patch.object(settings, "GEMINI_API_KEY", None), \
         patch.object(settings, "GOOGLE_API_KEY", None), \
         patch.object(settings, "ANTHROPIC_API_KEY", None):
        exp_res = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
        assert exp_res.status_code == 200
        data = exp_res.json()
        assert data["narrative_available"] is False
        assert "unconfigured or unavailable" in data["status_message"]


def test_explanation_gemini_generation_and_persistence(client: TestClient, db_session: Session):
    """Test mock Google Gemini API generation with bullet-point list format"""
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json={
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    })
    pred_id = pred_res.json()["prediction_id"]

    mock_json_str = json.dumps({
        "why_team_a_wins": [
            "Liverpool's title squad carried a dominant Elo advantage.",
            "Klopp's pressing system suffocated mid-table and top-tier opponents alike.",
            "The front three of Salah, Mane, and Firmino averaged over 2 goals per game.",
            "Home advantage at Anfield is worth an extra 10% in win probability."
        ],
        "why_team_a_loses": [
            "Arsenal's xG-efficient attack can capitalize on transition opportunities.",
            "Liverpool's high defensive line can be exposed by pace on the counter."
        ],
        "why_team_b_wins": [
            "Arsenal carry significant individual talent in the final third.",
            "Set-piece proficiency gives Arsenal an edge in tight matches."
        ],
        "why_team_b_loses": [
            "Away at Anfield is historically one of the hardest fixtures in football.",
            "Arsenal's defensive frailties in this season left them vulnerable."
        ]
    })

    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": mock_json_str}]
                }
            }
        ]
    }

    with patch.object(settings, "GEMINI_API_KEY", "mock_gemini_key"):
        with patch("httpx.Client.post", return_value=mock_http_response) as mock_post:
            exp_res = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert exp_res.status_code == 200
            data = exp_res.json()

            assert data["narrative_available"] is True
            # Narratives should be lists
            assert isinstance(data["narratives"]["why_team_a_wins"], list)
            assert len(data["narratives"]["why_team_a_wins"]) == 4
            assert "Liverpool's title squad" in data["narratives"]["why_team_a_wins"][0]

            # Check DB persistence
            db_row = db_session.query(PredictionNarrative).filter(PredictionNarrative.prediction_id == pred_id).first()
            assert db_row is not None
            stored = json.loads(db_row.narrative_team_a_win)
            assert isinstance(stored, list)
            assert len(stored) == 4


def test_explanation_database_cache_reuse(client: TestClient, db_session: Session):
    """Test repeat request reuses database record with zero network/LLM API calls"""
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json={
        "team_a_id": "Chelsea",
        "team_a_season": "2004-2005",
        "team_b_id": "Man United",
        "team_b_season": "1998-1999"
    })
    pred_id = pred_res.json()["prediction_id"]

    mock_json_str = json.dumps({
        "why_team_a_wins": ["Chelsea's 04-05 defense record was historic.", "Mourinho's bus was parked perfectly."],
        "why_team_a_loses": ["United's treble-winning attack had peak threat."],
        "why_team_b_wins": ["United's midfield control can dictate tempo."],
        "why_team_b_loses": ["Breaking down Chelsea's low block is nearly impossible."]
    })

    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": mock_json_str}]}}]
    }

    with patch.object(settings, "GEMINI_API_KEY", "mock_gemini_key"):
        with patch("httpx.Client.post", return_value=mock_http_response) as mock_post:
            # First request -> calls Gemini API and stores in DB
            res1 = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert res1.json()["narrative_available"] is True
            assert mock_post.call_count == 1

            # Second request -> MUST hit DB cache and NOT call API again
            res2 = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert res2.json()["narrative_available"] is True
            assert res2.json()["status_message"] == "Retrieved stored narrative from database record."
            assert mock_post.call_count == 1


def test_explanation_api_failure_resilience(client: TestClient):
    """Test that Gemini API exception/timeout returns graceful fallback without crashing"""
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json={
        "team_a_id": "Arsenal",
        "team_a_season": "2003-2004",
        "team_b_id": "Liverpool",
        "team_b_season": "2019-2020"
    })
    pred_id = pred_res.json()["prediction_id"]

    with patch.object(settings, "GEMINI_API_KEY", "mock_gemini_key"):
        with patch("httpx.Client.post", side_effect=Exception("Gemini API Timeout or Quota Exceeded")):
            exp_res = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert exp_res.status_code == 200
            data = exp_res.json()
            assert data["narrative_available"] is False
            assert "unavailable or timed out" in data["status_message"]
