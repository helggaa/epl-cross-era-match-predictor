import pytest
from sqlalchemy.orm import Session
from app.ml.elo import EloEngine, DEFAULT_ELO


def test_elo_computation(db_session: Session):
    engine = EloEngine()
    engine.compute_all_elos(db_session)

    assert engine.is_computed
    assert len(engine.season_snapshots) > 0

    # Test sample team-season snapshots exist
    liverpool_1920 = engine.get_elo("Liverpool", "2019-2020")
    arsenal_2526 = engine.get_elo("Arsenal", "2025-2026")

    assert liverpool_1920 > DEFAULT_ELO, "Liverpool 2019-20 title squad should rate well above 1500"
    assert arsenal_2526 > DEFAULT_ELO, "Arsenal 2025-26 squad should rate well above 1500"


def test_elo_determinism(db_session: Session):
    engine1 = EloEngine()
    engine1.compute_all_elos(db_session)
    val1 = engine1.get_elo("Manchester City", "2017-2018")

    engine2 = EloEngine()
    engine2.compute_all_elos(db_session)
    val2 = engine2.get_elo("Manchester City", "2017-2018")

    assert val1 == val2, "Elo computation must be 100% deterministic"
