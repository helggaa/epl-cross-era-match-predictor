from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class ExplanationNarrative(BaseModel):
    why_team_a_wins: List[str]
    why_team_a_loses: List[str]
    why_team_b_wins: List[str]
    why_team_b_loses: List[str]


class ExplanationResponse(BaseModel):
    prediction_id: str
    narrative_available: bool
    llm_model: Optional[str] = None
    narratives: Optional[ExplanationNarrative] = None
    generated_at: Optional[datetime] = None
    status_message: Optional[str] = None
