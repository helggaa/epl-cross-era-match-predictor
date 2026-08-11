from pydantic import BaseModel, Field
from typing import List, Optional


class PredictRequest(BaseModel):
    team_a_id: str = Field(..., json_schema_extra={"example": "Liverpool"}, description="Team A ID or name")
    team_a_season: str = Field(..., json_schema_extra={"example": "2019-2020"}, description="Team A Season (e.g. '2019-2020')")
    team_b_id: str = Field(..., json_schema_extra={"example": "Arsenal"}, description="Team B ID or name")
    team_b_season: str = Field(..., json_schema_extra={"example": "2025-2026"}, description="Team B Season (e.g. '2025-2026')")


class FeatureAttribution(BaseModel):
    feature_name: str
    feature_value: Optional[float] = None
    shap_value: Optional[float] = None
    favors: str  # 'team_a' | 'team_b' | 'neutral'
    description: Optional[str] = None


class TeamContext(BaseModel):
    name: str
    season: str
    league_position: Optional[int] = None
    points: Optional[int] = None
    goal_diff: Optional[float] = None
    elo_rating: float


class PredictResponse(BaseModel):
    prediction_id: str
    hypothetical_id: str
    model_version: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_home_goals: float
    predicted_away_goals: float
    reduced_confidence: bool
    team_a: TeamContext
    team_b: TeamContext
    top_features: List[FeatureAttribution]


class TeamResponse(BaseModel):
    team_id: str
    team_name: str


class TeamSeasonResponse(BaseModel):
    team_id: str
    team_name: str
    season: str
    elo: float
    league_position: Optional[int] = None
    points: Optional[int] = None
    has_xg: bool = False
