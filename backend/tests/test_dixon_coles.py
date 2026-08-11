import pytest
from app.ml.dixon_coles import DixonColesModel


def test_dixon_coles_probabilities_sum_to_one():
    model = DixonColesModel()
    res = model.predict_matchup(team_a_elo=1980.0, team_b_elo=1940.0)

    total_prob = res["home_win_prob"] + res["draw_prob"] + res["away_win_prob"]
    assert pytest.approx(total_prob, abs=1e-3) == 1.0, f"Probabilities sum to {total_prob}, expected 1.0"


def test_dixon_coles_home_advantage():
    model = DixonColesModel()
    # Equal Elo ratings
    res = model.predict_matchup(team_a_elo=1500.0, team_b_elo=1500.0)

    # Home team should have higher win prob than away team due to home advantage
    assert res["home_win_prob"] > res["away_win_prob"]
    assert res["predicted_home_goals"] > res["predicted_away_goals"]
