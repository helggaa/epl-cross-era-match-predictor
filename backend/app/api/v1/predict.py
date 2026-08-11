from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.predict import PredictRequest, PredictResponse
from app.services.predictor import predictor_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK)
def predict_matchup(request: PredictRequest, db: Session = Depends(get_db)):
    """
    Generate cross-era match outcome probabilities, expected scoreline, and feature attributions
    for any two Premier League team-seasons.
    """
    try:
        response = predictor_service.predict_matchup(db, request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {str(e)}"
        )
