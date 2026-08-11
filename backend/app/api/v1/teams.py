from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.predict import TeamResponse, TeamSeasonResponse
from app.services.predictor import predictor_service

router = APIRouter()


@router.get("/teams", response_model=List[TeamResponse])
def get_teams(db: Session = Depends(get_db)):
    """Return all unique Premier League clubs"""
    return predictor_service.get_teams(db)


@router.get("/team-seasons", response_model=List[TeamSeasonResponse])
def get_team_seasons(db: Session = Depends(get_db)):
    """Return all available team-seasons with Elo ratings and season stats"""
    return predictor_service.get_team_seasons(db)
