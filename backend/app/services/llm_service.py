import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

import anthropic

from app.core.config import settings
from app.models.app_models import Prediction, HypotheticalMatchup, PredictionExplanation, PredictionNarrative
from app.schemas.explanation import ExplanationResponse, ExplanationNarrative

logger = logging.getLogger("llm_explanation_service")

SYSTEM_PROMPT = """You are a football match-analysis assistant. You will be given structured data about a predicted matchup between two Premier League team-seasons, including the model's win/draw/loss probabilities and a ranked list of the statistical factors that drove the prediction.

RULES — follow these exactly:
1. Use ONLY the facts given in the input JSON. Do not invent statistics, injuries, transfers, tactical details, or historical facts that are not present in the input.
2. If a fact is missing (e.g. no xG data because the season predates 2014-15), do not guess or fill the gap with plausible-sounding football knowledge — simply omit that angle.
3. Write in plain, confident sports-analysis prose — no hedging phrases like "the model suggests" in every sentence; state the grounded facts directly.
4. Produce exactly four short sections as specified in the OUTPUT FORMAT below. Each section is 2-4 sentences.
5. Do not mention "SHAP", "feature importance", or any modeling terminology in the output — translate feature names into natural football language (e.g. "elo_diff" -> "overall squad strength", "home_xg_avg_last5" -> "recent attacking output at home").
6. If the input marks the prediction as "reduced_confidence": true, add one final sentence noting that this era of data has less detailed statistics available, without being apologetic about it.

OUTPUT FORMAT (return as JSON):
{
  "why_team_a_wins": "...",
  "why_team_a_loses": "...",
  "why_team_b_wins": "...",
  "why_team_b_loses": "..."
}"""


class LLMExplanationService:
    def __init__(self):
        pass

    def get_or_generate_explanation(self, prediction_id: str, db: Session) -> ExplanationResponse:
        # 1. Check prediction_narratives database cache
        existing = db.query(PredictionNarrative).filter(PredictionNarrative.prediction_id == prediction_id).first()
        if existing:
            logger.info(f"✓ Cache hit for prediction_id {prediction_id} in prediction_narratives database table.")
            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=True,
                llm_model=existing.llm_model,
                narratives=ExplanationNarrative(
                    why_team_a_wins=existing.narrative_team_a_win or "",
                    why_team_a_loses=existing.narrative_team_a_lose or "",
                    why_team_b_wins=existing.narrative_team_b_win or "",
                    why_team_b_loses=existing.narrative_team_b_lose or "",
                ),
                generated_at=existing.generated_at,
                status_message="Retrieved stored narrative from database record."
            )

        # Fetch prediction record
        pred = db.query(Prediction).filter(Prediction.prediction_id == prediction_id).first()
        if not pred:
            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=False,
                status_message=f"Prediction ID '{prediction_id}' not found."
            )

        # 2. Check if Anthropic API Key is configured
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key or not api_key.strip():
            logger.info(f"Anthropic API key unconfigured. Returning unconfigured status for prediction_id {prediction_id}.")
            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=False,
                status_message="LLM explanation service is unconfigured or unavailable. Statistical prediction remains fully valid."
            )

        # 3. Build payload for Anthropic API
        hyp = db.query(HypotheticalMatchup).filter(HypotheticalMatchup.hypothetical_id == pred.hypothetical_id).first()
        exps = db.query(PredictionExplanation).filter(PredictionExplanation.prediction_id == prediction_id).all()

        try:
            start_a = int(hyp.team_a_season.split("-")[0]) if hyp and hyp.team_a_season else 2000
            start_b = int(hyp.team_b_season.split("-")[0]) if hyp and hyp.team_b_season else 2000
        except Exception:
            start_a, start_b = 2000, 2000

        reduced_confidence = (start_a < 2014) or (start_b < 2014)

        top_features = [
            {
                "feature": exp.feature_name,
                "value": exp.feature_value,
                "favors": exp.favors,
                "description": exp.feature_name.replace("_", " ")
            }
            for exp in exps
        ]

        user_payload = {
            "team_a": {
                "name": hyp.team_a_id if hyp else "Team A",
                "season": hyp.team_a_season if hyp else "",
                "elo_rating": hyp.team_a_elo if hyp else 1500.0,
            },
            "team_b": {
                "name": hyp.team_b_id if hyp else "Team B",
                "season": hyp.team_b_season if hyp else "",
                "elo_rating": hyp.team_b_elo if hyp else 1500.0,
            },
            "prediction": {
                "home_win_prob": pred.home_win_prob,
                "draw_prob": pred.draw_prob,
                "away_win_prob": pred.away_win_prob
            },
            "top_features": top_features,
            "reduced_confidence": reduced_confidence
        }

        # 4. Invoke Anthropic API safely
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": json.dumps(user_payload, indent=2)}
                ]
            )

            response_text = response.content[0].text.strip()
            # Handle markdown fenced block stripping
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            narrative_json = json.loads(response_text)

            why_a_win = narrative_json.get("why_team_a_wins", "")
            why_a_lose = narrative_json.get("why_team_a_loses", "")
            why_b_win = narrative_json.get("why_team_b_wins", "")
            why_b_lose = narrative_json.get("why_team_b_loses", "")

            # 5. Persist into prediction_narratives database table
            now = datetime.utcnow()
            narrative_db = PredictionNarrative(
                prediction_id=prediction_id,
                llm_model=settings.LLM_MODEL,
                narrative_team_a_win=why_a_win,
                narrative_team_a_lose=why_a_lose,
                narrative_team_b_win=why_b_win,
                narrative_team_b_lose=why_b_lose,
                generated_at=now
            )
            db.add(narrative_db)
            db.commit()

            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=True,
                llm_model=settings.LLM_MODEL,
                narratives=ExplanationNarrative(
                    why_team_a_wins=why_a_win,
                    why_team_a_loses=why_a_lose,
                    why_team_b_wins=why_b_win,
                    why_team_b_loses=why_b_lose
                ),
                generated_at=now,
                status_message="Successfully generated and stored narrative."
            )
        except Exception as err:
            logger.warning(f"Anthropic API call failed or timed out: {err}. Graceful fallback activated.")
            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=False,
                status_message="LLM service unavailable or timed out. Statistical prediction remains fully valid."
            )


llm_explanation_service = LLMExplanationService()
