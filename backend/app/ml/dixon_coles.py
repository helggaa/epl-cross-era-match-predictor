import math
from typing import Tuple, Dict, Any


def tau_adjustment(x: int, y: int, lambda_param: float, mu_param: float, rho: float = -0.05) -> float:
    """
    Dixon-Coles low scoreline interdependence adjustment factor tau(x, y).
    """
    if x == 0 and y == 0:
        return 1.0 - lambda_param * mu_param * rho
    elif x == 1 and y == 0:
        return 1.0 + mu_param * rho
    elif x == 0 and y == 1:
        return 1.0 + lambda_param * rho
    elif x == 1 and y == 1:
        return 1.0 - rho
    else:
        return 1.0


def poisson_pmf(k: int, mu: float) -> float:
    """Poisson probability mass function P(X = k; mu)"""
    if mu <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.pow(mu, k) * math.exp(-mu)) / math.factorial(k)


class DixonColesModel:
    def __init__(self, max_goals: int = 10, rho: float = -0.05):
        self.max_goals = max_goals
        self.rho = rho

    def predict_matchup(
        self,
        team_a_elo: float,
        team_b_elo: float,
        team_a_gf_per_game: float | None = None,
        team_a_ga_per_game: float | None = None,
        team_b_gf_per_game: float | None = None,
        team_b_ga_per_game: float | None = None,
    ) -> Dict[str, Any]:
        """
        Calculate expected goals and match outcome probabilities for Team A (Home) vs Team B (Away).
        """
        # Base expected goals calculation using Elo rating gap and season attacking/defensive stats
        elo_diff = team_a_elo - team_b_elo

        # Baseline expected goals
        # Home advantage worth ~0.25 goal boost to home team
        base_lambda = 1.35 * math.exp(elo_diff / 400.0 * 0.75 + 0.15)
        base_mu = 1.05 * math.exp(-elo_diff / 400.0 * 0.75 - 0.15)

        # Incorporate actual season goal rates if available
        if team_a_gf_per_game is not None and team_b_ga_per_game is not None:
            rate_factor_a = (team_a_gf_per_game / 1.4) * (team_b_ga_per_game / 1.4)
            # Bound scaling factor
            rate_factor_a = max(0.5, min(2.0, rate_factor_a))
            base_lambda *= (0.7 + 0.3 * rate_factor_a)

        if team_b_gf_per_game is not None and team_a_ga_per_game is not None:
            rate_factor_b = (team_b_gf_per_game / 1.4) * (team_a_ga_per_game / 1.4)
            rate_factor_b = max(0.5, min(2.0, rate_factor_b))
            base_mu *= (0.7 + 0.3 * rate_factor_b)

        # Ensure expected goals are within realistic football bounds [0.2, 5.0]
        exp_home_goals = round(max(0.2, min(5.0, base_lambda)), 3)
        exp_away_goals = round(max(0.2, min(5.0, base_mu)), 3)

        # Compute bivariate probability distribution matrix
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0

        for x in range(self.max_goals + 1):
            p_x = poisson_pmf(x, exp_home_goals)
            for y in range(self.max_goals + 1):
                p_y = poisson_pmf(y, exp_away_goals)
                tau = tau_adjustment(x, y, exp_home_goals, exp_away_goals, self.rho)
                p_xy = p_x * p_y * tau

                if x > y:
                    home_win_prob += p_xy
                elif x == y:
                    draw_prob += p_xy
                else:
                    away_win_prob += p_xy

        # Normalize probabilities so sum equals 1.0 exactly
        total_p = home_win_prob + draw_prob + away_win_prob
        if total_p > 0:
            home_win_prob = round(home_win_prob / total_p, 4)
            draw_prob = round(draw_prob / total_p, 4)
            away_win_prob = round(away_win_prob / total_p, 4)

        # Adjust for precision rounding sum delta
        diff = round(1.0 - (home_win_prob + draw_prob + away_win_prob), 4)
        if diff != 0:
            draw_prob = round(draw_prob + diff, 4)

        return {
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "predicted_home_goals": exp_home_goals,
            "predicted_away_goals": exp_away_goals,
        }


dixon_coles_model = DixonColesModel()
