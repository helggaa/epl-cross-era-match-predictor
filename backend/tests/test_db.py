import pytest
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session


def test_database_connection(db_session: Session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_tables_exist(db_session: Session):
    expected_tables = [
        "staging_matches",
        "staging_team_season_summary",
        "staging_player_team_seasons",
        "staging_team_match_xg",
        "staging_player_season_xg",
        "staging_match_forecast_features",
        "staging_player_match_stats",
        "staging_teams",
        "hypothetical_matchups",
        "predictions",
        "prediction_explanations",
        "prediction_narratives",
        "player_event_rates",
        "simulation_runs",
    ]

    inspector = inspect(db_session.bind)
    existing_tables = inspector.get_table_names()

    for table in expected_tables:
        assert table in existing_tables, f"Table '{table}' does not exist in database"


def test_staging_row_counts(db_session: Session):
    expected_counts = {
        "staging_matches": 13401,
        "staging_team_season_summary": 664,
        "staging_player_team_seasons": 24541,
        "staging_team_match_xg": 7718,
        "staging_player_season_xg": 5864,
        "staging_match_forecast_features": 4180,
        "staging_player_match_stats": 119148,
        "staging_teams": 51,
    }

    for table, expected_count in expected_counts.items():
        query = text(f"SELECT COUNT(*) FROM {table}")
        count = db_session.execute(query).scalar()
        assert count == expected_count, f"Table {table} row count mismatch: expected {expected_count}, got {count}"
