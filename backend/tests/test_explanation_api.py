import json
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.models.app_models import PredictionNarrative


def test_predict_works_without_anthropic_key(client: TestClient):
    """Test that POST /predict works 100% without Anthropic key configured"""
    with patch.object(settings, "ANTHROPIC_API_KEY", None):
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
    # 1. Create prediction
    payload = {
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    }
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json=payload)
    pred_id = pred_res.json()["prediction_id"]

    # 2. Get explanation with unconfigured API key
    with patch.object(settings, "ANTHROPIC_API_KEY", None):
        exp_res = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
        assert exp_res.status_code == 200
        data = exp_res.json()
        assert data["narrative_available"] is False
        assert "unconfigured or unavailable" in data["status_message"]


def test_explanation_generation_and_persistence(client: TestClient, db_session: Session):
    """Test mock Anthropic generation, JSON validation, and DB persistence"""
    # Create prediction
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json={
        "team_a_id": "Liverpool",
        "team_a_season": "2019-2020",
        "team_b_id": "Arsenal",
        "team_b_season": "2025-2026"
    })
    pred_id = pred_res.json()["prediction_id"]

    mock_json_str = json.dumps({
        "why_team_a_wins": "Liverpool's title squad rates well above Arsenal with strong home attack.",
        "why_team_a_loses": "Arsenal has individual quality to exploit counter-attacks.",
        "why_team_b_wins": "Arsenal can capitalize on high line errors.",
        "why_team_b_loses": "Defensive deficit against Liverpool's press makes an away win tough."
    })

    # Mock Anthropic client
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=mock_json_str)]

    with patch.object(settings, "ANTHROPIC_API_KEY", "mock_key"):
        with patch("anthropic.Anthropic") as MockAnthropic:
            instance = MockAnthropic.return_value
            instance.messages.create.return_value = mock_msg

            exp_res = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert exp_res.status_code == 200
            data = exp_res.json()

            assert data["narrative_available"] is True
            assert data["narratives"]["why_team_a_wins"].startswith("Liverpool's title squad")

            # Check DB persistence in prediction_narratives table
            db_row = db_session.query(PredictionNarrative).filter(PredictionNarrative.prediction_id == pred_id).first()
            assert db_row is not None
            assert db_row.narrative_team_a_win.startswith("Liverpool's title squad")


def test_explanation_database_cache_reuse(client: TestClient, db_session: Session):
    """Test repeat request reuses database record with zero network/LLM API calls"""
    # Create prediction
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json={
        "team_a_id": "Chelsea",
        "team_a_season": "2004-2005",
        "team_b_id": "Man United",
        "team_b_season": "1998-1999"
    })
    pred_id = pred_res.json()["prediction_id"]

    mock_json_str = json.dumps({
        "why_team_a_wins": "Chelsea's 04-05 defense record was historic.",
        "why_team_a_loses": "United's treble-winning attack has peak threat.",
        "why_team_b_wins": "United's midfield control can dictate tempo.",
        "why_team_b_loses": "Breaking down Chelsea's low block is difficult."
    })

    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=mock_json_str)]

    with patch.object(settings, "ANTHROPIC_API_KEY", "mock_key"):
        with patch("anthropic.Anthropic") as MockAnthropic:
            instance = MockAnthropic.return_value
            instance.messages.create.return_value = mock_msg

            # First request -> calls Anthropic and stores in DB
            res1 = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert res1.json()["narrative_available"] is True
            assert instance.messages.create.call_count == 1

            # Second request -> MUST hit DB cache and NOT call Anthropic again
            res2 = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert res2.json()["narrative_available"] is True
            assert res2.json()["status_message"] == "Retrieved stored narrative from database record."
            # Verify call_count is STILL 1
            assert instance.messages.create.call_count == 1


def test_explanation_api_failure_resilience(client: TestClient):
    """Test that Anthropic API exception/timeout returns graceful fallback without crashing"""
    pred_res = client.post(f"{settings.API_V1_STR}/predict", json={
        "team_a_id": "Arsenal",
        "team_a_season": "2003-2004",
        "team_b_id": "Liverpool",
        "team_b_season": "2019-2020"
    })
    pred_id = pred_res.json()["prediction_id"]

    with patch.object(settings, "ANTHROPIC_API_KEY", "mock_key"):
        with patch("anthropic.Anthropic") as MockAnthropic:
            instance = MockAnthropic.return_value
            instance.messages.create.side_effect = Exception("Anthropic API Timeout or Credit Exhausted")

            exp_res = client.get(f"{settings.API_V1_STR}/predict/{pred_id}/explanation")
            assert exp_res.status_code == 200
            data = exp_res.json()
            assert data["narrative_available"] is False
            assert "unavailable or timed out" in data["status_message"]
