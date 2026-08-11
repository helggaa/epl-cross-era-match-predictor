from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.explanation import ExplanationResponse
from app.services.llm_service import llm_explanation_service

router = APIRouter()


@router.get("/predict/{prediction_id}/explanation", response_model=ExplanationResponse)
def get_prediction_explanation(prediction_id: str, db: Session = Depends(get_db)):
    """
    Retrieve or generate Layer 2 grounded natural language explanations for a prediction.
    Reuses database records for repeat requests. Gracefully falls back if Anthropic API is unconfigured/unavailable.
    """
    return llm_explanation_service.get_or_generate_explanation(prediction_id, db)
