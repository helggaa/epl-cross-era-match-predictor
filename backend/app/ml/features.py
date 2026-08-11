from typing import Dict, Any, List


def extract_top_features(
    team_a_context: Dict[str, Any],
    team_b_context: Dict[str, Any],
    team_a_elo: float,
    team_b_elo: float,
) -> List[Dict[str, Any]]:
    """
    Extract and rank top 5-8 contributing features with directional attribution.
    """
    features: List[Dict[str, Any]] = []

    # 1. Elo difference
    elo_diff = team_a_elo - team_b_elo
    favors_elo = "team_a" if elo_diff > 15 else ("team_b" if elo_diff < -15 else "neutral")
    features.append({
        "feature_name": "elo_diff",
        "feature_value": round(elo_diff, 1),
        "shap_value": round(elo_diff / 100.0, 3),
        "favors": favors_elo,
        "description": "overall squad strength gap"
    })

    # 2. Points per game difference
    ppg_a = team_a_context.get("ppg")
    ppg_b = team_b_context.get("ppg")
    if ppg_a is not None and ppg_b is not None:
        ppg_diff = ppg_a - ppg_b
        favors_ppg = "team_a" if ppg_diff > 0.1 else ("team_b" if ppg_diff < -0.1 else "neutral")
        features.append({
            "feature_name": "points_per_game_diff",
            "feature_value": round(ppg_diff, 2),
            "shap_value": round(ppg_diff * 0.4, 3),
            "favors": favors_ppg,
            "description": "season points-per-game pace gap"
        })

    # 3. Goal diff per game difference
    gd_pg_a = team_a_context.get("gd_per_game")
    gd_pg_b = team_b_context.get("gd_per_game")
    if gd_pg_a is not None and gd_pg_b is not None:
        gd_diff = gd_pg_a - gd_pg_b
        favors_gd = "team_a" if gd_diff > 0.1 else ("team_b" if gd_diff < -0.1 else "neutral")
        features.append({
            "feature_name": "goal_diff_per_game_diff",
            "feature_value": round(gd_diff, 2),
            "shap_value": round(gd_diff * 0.35, 3),
            "favors": favors_gd,
            "description": "net goal differential per match gap"
        })

    # 4. Attacking output (Goals scored per game)
    gf_a = team_a_context.get("gf_per_game")
    gf_b = team_b_context.get("gf_per_game")
    if gf_a is not None and gf_b is not None:
        gf_diff = gf_a - gf_b
        favors_gf = "team_a" if gf_diff > 0.1 else ("team_b" if gf_diff < -0.1 else "neutral")
        features.append({
            "feature_name": "goals_scored_per_game_diff",
            "feature_value": round(gf_diff, 2),
            "shap_value": round(gf_diff * 0.25, 3),
            "favors": favors_gf,
            "description": "attacking threat & goal scoring output"
        })

    # 5. Defensive resilience (Goals against per game - lower is better)
    ga_a = team_a_context.get("ga_per_game")
    ga_b = team_b_context.get("ga_per_game")
    if ga_a is not None and ga_b is not None:
        # Fewer goals conceded favors the team
        ga_diff = ga_b - ga_a  # positive means Team A conceded fewer goals
        favors_ga = "team_a" if ga_diff > 0.1 else ("team_b" if ga_diff < -0.1 else "neutral")
        features.append({
            "feature_name": "defensive_conceded_per_game_diff",
            "feature_value": round(ga_diff, 2),
            "shap_value": round(ga_diff * 0.25, 3),
            "favors": favors_ga,
            "description": "defensive solidity & goal prevention"
        })

    # 6. Advanced xG stats (if available post-2014)
    xg_a = team_a_context.get("xg_per_game")
    xg_b = team_b_context.get("xg_per_game")
    if xg_a is not None and xg_b is not None:
        xg_diff = xg_a - xg_b
        favors_xg = "team_a" if xg_diff > 0.1 else ("team_b" if xg_diff < -0.1 else "neutral")
        features.append({
            "feature_name": "xg_per_game_diff",
            "feature_value": round(xg_diff, 2),
            "shap_value": round(xg_diff * 0.3, 3),
            "favors": favors_xg,
            "description": "understat expected goals (xG) creation gap"
        })

    # 7. Squad Market Value diff (if available post-2004)
    mv_a = team_a_context.get("market_value_total")
    mv_b = team_b_context.get("market_value_total")
    if mv_a is not None and mv_b is not None and (mv_a > 0 or mv_b > 0):
        mv_diff = mv_a - mv_b
        favors_mv = "team_a" if mv_diff > 10_000_000 else ("team_b" if mv_diff < -10_000_000 else "neutral")
        features.append({
            "feature_name": "squad_value_diff",
            "feature_value": round(mv_diff, 0),
            "shap_value": round(mv_diff / 50_000_000.0, 3),
            "favors": favors_mv,
            "description": "squad market value gap"
        })

    # Sort features by absolute shap_value descending
    features.sort(key=lambda f: abs(f["shap_value"]), reverse=True)
    return features
