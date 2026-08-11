import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import math

logger = logging.getLogger("elo_engine")

DEFAULT_ELO = 1500.0
HOME_ADVANTAGE = 65.0
K_FACTOR = 24.0
REGRESSION_FACTOR = 0.25  # Inter-season decay: 25% regression toward 1500


class EloEngine:
    def __init__(self):
        self.team_ratings: Dict[str, float] = {}
        self.season_snapshots: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.team_season_history: Dict[Tuple[str, str], List[float]] = {}
        self.is_computed: bool = False

    def _expected_outcome(self, rating_a: float, rating_b: float) -> float:
        """Expected score for Team A against Team B"""
        return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))

    def compute_all_elos(self, db: Session):
        """
        Process matches in strict chronological order and compute Elo ratings and season snapshots.
        """
        logger.info("Computing chronological Elo ratings across all matches...")
        self.team_ratings.clear()
        self.season_snapshots.clear()
        self.team_season_history.clear()

        # Query matches ordered by date and match_id
        query = text("""
            SELECT match_id, season, date, home_team, away_team, home_goals, away_goals, result
            FROM staging_matches
            WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
            ORDER BY date ASC, match_id ASC
        """)
        matches = db.execute(query).mappings().all()

        current_season = None

        for match in matches:
            season = match["season"]
            home_team = match["home_team"]
            away_team = match["away_team"]
            home_goals = match["home_goals"]
            away_goals = match["away_goals"]
            result = match["result"]  # 'H', 'D', 'A'

            # Season transition -> mean reversion regression
            if current_season is not None and season != current_season:
                self._apply_inter_season_decay()

            current_season = season

            # Initialize teams if new
            if home_team not in self.team_ratings:
                self.team_ratings[home_team] = DEFAULT_ELO
            if away_team not in self.team_ratings:
                self.team_ratings[away_team] = DEFAULT_ELO

            # Record rating before match
            r_home = self.team_ratings[home_team]
            r_away = self.team_ratings[away_team]

            # Actual score outcome
            if result == 'H':
                s_home, s_away = 1.0, 0.0
            elif result == 'A':
                s_home, s_away = 0.0, 1.0
            else:  # Draw
                s_home, s_away = 0.5, 0.5

            # Expected score with home advantage
            exp_home = self._expected_outcome(r_home + HOME_ADVANTAGE, r_away)
            exp_away = 1.0 - exp_home

            # Margin of victory multiplier
            goal_diff = abs(home_goals - away_goals)
            mov_multiplier = math.log(1.0 + goal_diff) if goal_diff > 1 else 1.0

            # Update ratings
            new_r_home = r_home + K_FACTOR * mov_multiplier * (s_home - exp_home)
            new_r_away = r_away + K_FACTOR * mov_multiplier * (s_away - exp_away)

            self.team_ratings[home_team] = new_r_home
            self.team_ratings[away_team] = new_r_away

            # Record history for snapshot stats
            self._record_rating(home_team, season, new_r_home)
            self._record_rating(away_team, season, new_r_away)

        # Finalize snapshot dictionary
        self._build_season_snapshots()
        self.is_computed = True
        logger.info(f"✓ Computed Elo snapshots for {len(self.season_snapshots)} team-seasons.")

    def _apply_inter_season_decay(self):
        """Regress ratings 25% toward league average (1500) between seasons"""
        for team in self.team_ratings:
            self.team_ratings[team] = (1.0 - REGRESSION_FACTOR) * self.team_ratings[team] + REGRESSION_FACTOR * DEFAULT_ELO

    def _record_rating(self, team: str, season: str, rating: float):
        key = (team, season)
        if key not in self.team_season_history:
            self.team_season_history[key] = []
        self.team_season_history[key].append(rating)

    def _build_season_snapshots(self):
        for (team, season), ratings in self.team_season_history.items():
            if not ratings:
                continue
            final_elo = round(ratings[-1], 2)
            avg_elo = round(sum(ratings) / len(ratings), 2)
            peak_elo = round(max(ratings), 2)

            self.season_snapshots[(team, season)] = {
                "team": team,
                "season": season,
                "final_elo": final_elo,
                "avg_elo": avg_elo,
                "peak_elo": peak_elo,
            }

    def get_elo(self, team: str, season: str) -> float:
        """Retrieve final Elo for a team-season snapshot, fallback to DEFAULT_ELO if not found"""
        key = (team, season)
        if key in self.season_snapshots:
            return self.season_snapshots[key]["final_elo"]
        return DEFAULT_ELO


# Singleton engine instance
elo_engine = EloEngine()
