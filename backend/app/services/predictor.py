import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.ml.elo import elo_engine, DEFAULT_ELO
from app.ml.dixon_coles import dixon_coles_model
from app.ml.features import extract_top_features
from app.models.app_models import HypotheticalMatchup, Prediction, PredictionExplanation
from app.schemas.predict import (
    PredictRequest,
    PredictResponse,
    TeamContext,
    FeatureAttribution,
    TeamResponse,
    TeamSeasonResponse,
)

MODEL_VERSION = "v1.0.0-elo-dixoncoles"


class PredictorService:
    def __init__(self):
        pass

    def ensure_elo_computed(self, db: Session):
        if not elo_engine.is_computed:
            elo_engine.compute_all_elos(db)

    def _resolve_team_name(self, db: Session, input_name: str) -> str:
        """Resolve team name to match team_season_summary naming"""
        self.ensure_elo_computed(db)
        
        # Direct check in team_season_summary
        query = text("SELECT DISTINCT team FROM staging_team_season_summary WHERE LOWER(team) = LOWER(:name) LIMIT 1")
        res = db.execute(query, {"name": input_name}).scalar()
        if res:
            return res

        # Try stripped/alias match (e.g. "Arsenal FC" -> "Arsenal", "Manchester United" -> "Man United")
        clean_name = input_name.replace(" FC", "").replace(" AFC", "").strip()
        query2 = text("SELECT DISTINCT team FROM staging_team_season_summary WHERE LOWER(team) LIKE LOWER(:name) LIMIT 1")
        res2 = db.execute(query2, {"name": f"%{clean_name}%"}).scalar()
        if res2:
            return res2

        return input_name

    def get_teams(self, db: Session) -> List[TeamResponse]:
        query = text("""
            SELECT DISTINCT team 
            FROM staging_team_season_summary 
            ORDER BY team ASC
        """)
        rows = db.execute(query).scalars().all()
        return [TeamResponse(team_id=t, team_name=t) for t in rows]

    def get_team_seasons(self, db: Session) -> List[TeamSeasonResponse]:
        self.ensure_elo_computed(db)

        # Get final table summary per team season
        query = text("""
            SELECT season, team, played, wins, draws, losses, goals_for, goals_against, points
            FROM staging_team_season_summary
            ORDER BY season DESC, points DESC
        """)
        rows = db.execute(query).mappings().all()

        # Compute rank per season
        season_groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            s = r["season"]
            if s not in season_groups:
                season_groups[s] = []
            season_groups[s].append(dict(r))

        results: List[TeamSeasonResponse] = []
        for season, teams in season_groups.items():
            # Determine starting year
            try:
                start_year = int(season.split("-")[0])
            except Exception:
                start_year = 2000

            has_xg = start_year >= 2014

            for rank, team_data in enumerate(teams, start=1):
                t_name = team_data["team"]
                elo = elo_engine.get_elo(t_name, season)

                results.append(TeamSeasonResponse(
                    team_id=t_name,
                    team_name=t_name,
                    season=season,
                    elo=elo,
                    league_position=rank,
                    points=team_data["points"],
                    has_xg=has_xg
                ))

        return results

    def _get_team_season_context(self, db: Session, team_name: str, season: str) -> Dict[str, Any]:
        """Fetch stats for team-season from staging_team_season_summary and team_match_xg"""
        query = text("""
            SELECT played, wins, draws, losses, goals_for, goals_against, goal_diff, points
            FROM staging_team_season_summary
            WHERE LOWER(team) = LOWER(:team) AND season = :season
            LIMIT 1
        """)
        row = db.execute(query, {"team": team_name, "season": season}).mappings().first()

        ctx: Dict[str, Any] = {
            "team": team_name,
            "season": season,
            "played": None,
            "points": None,
            "goal_diff": None,
            "ppg": None,
            "gf_per_game": None,
            "ga_per_game": None,
            "gd_per_game": None,
            "league_position": None,
            "xg_per_game": None,
            "market_value_total": None,
        }

        if row:
            played = row["played"] or 38
            points = row["points"]
            gf = row["goals_for"]
            ga = row["goals_against"]
            gd = row["goal_diff"]

            ctx["played"] = played
            ctx["points"] = points
            ctx["goal_diff"] = gd
            ctx["ppg"] = round(points / played, 2) if played > 0 and points is not None else None
            ctx["gf_per_game"] = round(gf / played, 2) if played > 0 and gf is not None else None
            ctx["ga_per_game"] = round(ga / played, 2) if played > 0 and ga is not None else None
            ctx["gd_per_game"] = round(gd / played, 2) if played > 0 and gd is not None else None

        # Try xG stats for 2014+
        try:
            start_year = int(season.split("-")[0])
        except Exception:
            start_year = 2000

        if start_year >= 2014:
            xg_query = text("""
                SELECT AVG(xg) as avg_xg
                SELECT AVG(xg) as avg_xg FROM staging_team_match_xg
                WHERE LOWER(club_name) LIKE LOWER(:club) AND season = :start_year
            """)
            try:
                xg_val = db.execute(text("""
                    SELECT AVG(xg) FROM staging_team_match_xg
                    WHERE LOWER(club_name) LIKE LOWER(:club) AND season = :start_year
                """), {"club": f"%{team_name.split()[0]}%", "start_year": start_year}).scalar()
                if xg_val is not None:
                    ctx["xg_per_game"] = round(float(xg_val), 2)
            except Exception:
                pass

        return ctx

    def predict_matchup(self, db: Session, request: PredictRequest) -> PredictResponse:
        self.ensure_elo_computed(db)

        team_a = self._resolve_team_name(db, request.team_a_id)
        team_b = self._resolve_team_name(db, request.team_b_id)
        season_a = request.team_a_season
        season_b = request.team_b_season

        # Retrieve Elo ratings
        elo_a = elo_engine.get_elo(team_a, season_a)
        elo_b = elo_engine.get_elo(team_b, season_b)

        # Retrieve team contexts
        ctx_a = self._get_team_season_context(db, team_a, season_a)
        ctx_b = self._get_team_season_context(db, team_b, season_b)

        # Predict match probabilities using Dixon-Coles model
        outcome = dixon_coles_model.predict_matchup(
            team_a_elo=elo_a,
            team_b_elo=elo_b,
            team_a_gf_per_game=ctx_a.get("gf_per_game"),
            team_a_ga_per_game=ctx_a.get("ga_per_game"),
            team_b_gf_per_game=ctx_b.get("gf_per_game"),
            team_b_ga_per_game=ctx_b.get("ga_per_game"),
        )

        # Determine reduced confidence (pre-2014)
        try:
            start_a = int(season_a.split("-")[0])
            start_b = int(season_b.split("-")[0])
        except Exception:
            start_a, start_b = 2000, 2000

        reduced_confidence = (start_a < 2014) or (start_b < 2014)

        # Extract top feature attributions
        raw_features = extract_top_features(ctx_a, ctx_b, elo_a, elo_b)
        top_features_schema = [FeatureAttribution(**f) for f in raw_features]

        # Generate IDs
        hypothetical_id = f"hyp_{uuid.uuid4().hex[:12]}"
        prediction_id = f"pred_{uuid.uuid4().hex[:12]}"
        created_at = datetime.utcnow()

        # Database persistence
        hyp_db = HypotheticalMatchup(
            hypothetical_id=hypothetical_id,
            team_a_id=team_a,
            team_a_season=season_a,
            team_b_id=team_b,
            team_b_season=season_b,
            team_a_elo=elo_a,
            team_b_elo=elo_b,
            created_at=created_at,
        )
        db.add(hyp_db)

        pred_db = Prediction(
            prediction_id=prediction_id,
            hypothetical_id=hypothetical_id,
            model_version=MODEL_VERSION,
            home_win_prob=outcome["home_win_prob"],
            draw_prob=outcome["draw_prob"],
            away_win_prob=outcome["away_win_prob"],
            predicted_home_goals=outcome["predicted_home_goals"],
            predicted_away_goals=outcome["predicted_away_goals"],
            created_at=created_at,
        )
        db.add(pred_db)

        for feat in raw_features:
            exp_db = PredictionExplanation(
                prediction_id=prediction_id,
                feature_name=feat["feature_name"],
                feature_value=float(feat["feature_value"]) if feat["feature_value"] is not None else None,
                shap_value=float(feat["shap_value"]) if feat["shap_value"] is not None else None,
                favors=feat["favors"],
            )
            db.add(exp_db)

        db.commit()

        team_a_context = TeamContext(
            name=team_a,
            season=season_a,
            league_position=ctx_a.get("league_position"),
            points=ctx_a.get("points"),
            goal_diff=ctx_a.get("goal_diff"),
            elo_rating=elo_a
        )

        team_b_context = TeamContext(
            name=team_b,
            season=season_b,
            league_position=ctx_b.get("league_position"),
            points=ctx_b.get("points"),
            goal_diff=ctx_b.get("goal_diff"),
            elo_rating=elo_b
        )

        return PredictResponse(
            prediction_id=prediction_id,
            hypothetical_id=hypothetical_id,
            model_version=MODEL_VERSION,
            home_win_prob=outcome["home_win_prob"],
            draw_prob=outcome["draw_prob"],
            away_win_prob=outcome["away_win_prob"],
            predicted_home_goals=outcome["predicted_home_goals"],
            predicted_away_goals=outcome["predicted_away_goals"],
            reduced_confidence=reduced_confidence,
            team_a=team_a_context,
            team_b=team_b_context,
            top_features=top_features_schema
        )


predictor_service = PredictorService()
