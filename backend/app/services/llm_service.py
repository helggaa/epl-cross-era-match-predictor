import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import httpx

try:
    import anthropic
except ImportError:
    anthropic = None

from app.core.config import settings
from app.models.app_models import Prediction, HypotheticalMatchup, PredictionExplanation, PredictionNarrative
from app.schemas.explanation import ExplanationResponse, ExplanationNarrative

logger = logging.getLogger("llm_explanation_service")

SYSTEM_PROMPT = """You are a legendary football pundit with deep Premier League knowledge, sharp tactical insight, and a dry sense of humor. You will be given structured data about a predicted cross-era matchup between two Premier League team-seasons, including probabilities and the statistical factors that drove the prediction.

RULES — follow these exactly:
1. Use the facts given in the input JSON as your statistical foundation. You MAY enrich the analysis with well-known historical facts about that specific team-season (e.g. trophy wins, famous players, iconic tactics, manager identity, league position) — but NEVER fabricate statistics or numbers that aren't in the input.
2. If xG data is missing (pre-2014 seasons), do not invent xG numbers — talk about what IS available.
3. Write in confident, entertaining sports-pundit prose. Mix sharp tactical analysis with occasional humor, pop-culture references, or football memes where they fit naturally. Don't force jokes — let them land when the matchup calls for it.
4. Produce exactly four sections. Each section MUST be a JSON array of 4-11 bullet-point strings. No more than 11 bullets per section. Each bullet is one distinct reason or angle — be specific, not generic.
5. Do NOT mention "SHAP", "feature importance", or modeling terminology. Translate features into natural football language (e.g. "elo_diff" → "overall squad pedigree", "gf_per_game" → "goals-per-game average").
6. Each bullet should feel like a standalone insight a pundit would make on TV — punchy, specific, and grounded.
7. If "reduced_confidence" is true, include one bullet noting the era has sparser data, framed naturally.

OUTPUT FORMAT (return as valid JSON — each value is an ARRAY of strings, maximum 11 items each):
{
  "why_team_a_wins": ["reason 1", "reason 2", "...", "reason N (max 11)"],
  "why_team_a_loses": ["reason 1", "reason 2", "...", "reason N (max 11)"],
  "why_team_b_wins": ["reason 1", "reason 2", "...", "reason N (max 11)"],
  "why_team_b_loses": ["reason 1", "reason 2", "...", "reason N (max 11)"]
}"""


MAX_REASONS = 11


def _ensure_list(val) -> list:
    """Convert string or list narrative value to a list of strings, capped at MAX_REASONS."""
    if isinstance(val, list):
        return val[:MAX_REASONS]
    if isinstance(val, str) and val.strip():
        return [val]
    return []


def _list_to_str(val: list) -> str:
    """Serialize a list of reasons to a JSON string for DB storage."""
    return json.dumps(val, ensure_ascii=False)


def _str_to_list(val: str | None) -> list:
    """Deserialize a DB-stored JSON string back to a list."""
    if not val:
        return []
    try:
        parsed = json.loads(val)
        if isinstance(parsed, list):
            return parsed
        return [str(parsed)]
    except (json.JSONDecodeError, TypeError):
        return [val] if val.strip() else []


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
                    why_team_a_wins=_str_to_list(existing.narrative_team_a_win),
                    why_team_a_loses=_str_to_list(existing.narrative_team_a_lose),
                    why_team_b_wins=_str_to_list(existing.narrative_team_b_win),
                    why_team_b_loses=_str_to_list(existing.narrative_team_b_lose),
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

        # 2. Check available API keys
        gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        anthropic_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")

        if not gemini_key and not anthropic_key:
            logger.info(f"LLM API key unconfigured. Returning unconfigured status for prediction_id {prediction_id}.")
            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=False,
                status_message="LLM explanation service is unconfigured or unavailable. Statistical prediction remains fully valid."
            )

        # 3. Build structured payload
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

        # 4. Invoke LLM Provider (Google Gemini preferred, Anthropic fallback)
        try:
            narrative_json = None
            used_model = settings.LLM_MODEL

            if gemini_key:
                # Model fallback chain — if primary is overloaded (503), try alternatives
                primary = settings.LLM_MODEL if ("gemini" in settings.LLM_MODEL and "2.0" not in settings.LLM_MODEL) else "gemini-flash-latest"
                fallback_models = [primary, "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"]
                # Deduplicate while preserving order
                seen = set()
                models_to_try = []
                for m in fallback_models:
                    if m not in seen:
                        seen.add(m)
                        models_to_try.append(m)

                prompt_text = f"{SYSTEM_PROMPT}\n\nINPUT DATA:\n{json.dumps(user_payload, indent=2)}"

                request_body = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt_text}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "responseMimeType": "application/json"
                    }
                }

                last_error = None
                with httpx.Client(timeout=30.0) as client:
                    for model_name in models_to_try:
                        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key.strip()}"
                        try:
                            resp = client.post(gemini_url, json=request_body)
                            if resp.status_code == 200:
                                data = resp.json()
                                candidates = data.get("candidates", [])
                                if candidates:
                                    response_text = candidates[0]["content"]["parts"][0]["text"].strip()
                                    narrative_json = json.loads(response_text)
                                    used_model = model_name
                                    logger.info(f"✓ Gemini model '{model_name}' returned successfully.")
                                    break
                            else:
                                last_error = f"{model_name} returned {resp.status_code}"
                                logger.warning(f"Gemini model '{model_name}' returned {resp.status_code}, trying next fallback...")
                        except Exception as model_err:
                            last_error = str(model_err)
                            logger.warning(f"Gemini model '{model_name}' failed: {model_err}, trying next fallback...")

                if not narrative_json and last_error:
                    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

            elif anthropic_key and anthropic:
                used_model = settings.LLM_MODEL if "claude" in settings.LLM_MODEL else "claude-3-5-haiku-20241022"
                client = anthropic.Anthropic(api_key=anthropic_key)
                response = client.messages.create(
                    model=used_model,
                    max_tokens=2000,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": json.dumps(user_payload, indent=2)}
                    ]
                )
                response_text = response.content[0].text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                narrative_json = json.loads(response_text)

            if not narrative_json:
                raise RuntimeError("Failed to parse LLM response JSON")

            why_a_win = _ensure_list(narrative_json.get("why_team_a_wins", []))
            why_a_lose = _ensure_list(narrative_json.get("why_team_a_loses", []))
            why_b_win = _ensure_list(narrative_json.get("why_team_b_wins", []))
            why_b_lose = _ensure_list(narrative_json.get("why_team_b_loses", []))

            # 5. Persist into prediction_narratives database table (stored as JSON strings)
            now = datetime.utcnow()
            narrative_db = PredictionNarrative(
                prediction_id=prediction_id,
                llm_model=used_model,
                narrative_team_a_win=_list_to_str(why_a_win),
                narrative_team_a_lose=_list_to_str(why_a_lose),
                narrative_team_b_win=_list_to_str(why_b_win),
                narrative_team_b_lose=_list_to_str(why_b_lose),
                generated_at=now
            )
            db.add(narrative_db)
            db.commit()

            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=True,
                llm_model=used_model,
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
            logger.warning(f"LLM API call failed or timed out: {err}. Graceful fallback activated.")
            return ExplanationResponse(
                prediction_id=prediction_id,
                narrative_available=False,
                status_message="LLM service unavailable or timed out. Statistical prediction remains fully valid."
            )


llm_explanation_service = LLMExplanationService()
