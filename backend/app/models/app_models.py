from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class HypotheticalMatchup(Base):
    __tablename__ = "hypothetical_matchups"

    hypothetical_id = Column(String, primary_key=True, index=True)
    team_a_id = Column(String, index=True)
    team_a_season = Column(String, index=True)
    team_b_id = Column(String, index=True)
    team_b_season = Column(String, index=True)
    team_a_elo = Column(Float, nullable=True)
    team_b_elo = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    predictions = relationship("Prediction", back_populates="hypothetical_matchup", cascade="all, delete-orphan")
    simulation_runs = relationship("SimulationRun", back_populates="hypothetical_matchup", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(String, primary_key=True, index=True)
    hypothetical_id = Column(String, ForeignKey("hypothetical_matchups.hypothetical_id"), index=True)
    model_version = Column(String)
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    predicted_home_goals = Column(Float, nullable=True)
    predicted_away_goals = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hypothetical_matchup = relationship("HypotheticalMatchup", back_populates="predictions")
    explanations = relationship("PredictionExplanation", back_populates="prediction", cascade="all, delete-orphan")
    narrative = relationship("PredictionNarrative", back_populates="prediction", uselist=False, cascade="all, delete-orphan")


class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(String, ForeignKey("predictions.prediction_id"), index=True)
    feature_name = Column(String)
    feature_value = Column(Float, nullable=True)
    shap_value = Column(Float, nullable=True)
    favors = Column(String)  # 'team_a' | 'team_b' | 'neutral'

    # Relationships
    prediction = relationship("Prediction", back_populates="explanations")


class PredictionNarrative(Base):
    __tablename__ = "prediction_narratives"

    prediction_id = Column(String, ForeignKey("predictions.prediction_id"), primary_key=True)
    llm_model = Column(String)
    narrative_team_a_win = Column(String, nullable=True)
    narrative_team_a_lose = Column(String, nullable=True)
    narrative_team_b_win = Column(String, nullable=True)
    narrative_team_b_lose = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction = relationship("Prediction", back_populates="narrative")


class PlayerEventRate(Base):
    __tablename__ = "player_event_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, index=True)
    season = Column(String, index=True)
    team_id = Column(String, index=True)
    goals_per_90 = Column(Float, nullable=True)
    assists_per_90 = Column(Float, nullable=True)
    share_of_team_goals = Column(Float, nullable=True)
    share_of_team_cards = Column(Float, nullable=True)
    minutes_played_total = Column(Integer, nullable=True)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    sim_id = Column(String, primary_key=True, index=True)
    hypothetical_id = Column(String, ForeignKey("hypothetical_matchups.hypothetical_id"), index=True)
    run_number = Column(Integer)
    final_score_team_a = Column(Integer)
    final_score_team_b = Column(Integer)
    event_log = Column(JSON)  # list of [{minute, team, player, event_type}]
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hypothetical_matchup = relationship("HypotheticalMatchup", back_populates="simulation_runs")
