import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Add parent directory to path so app modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_data")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

CSV_FILES = [
    "matches.csv",
    "team_season_summary.csv",
    "player_team_seasons.csv",
    "team_match_xg.csv",
    "player_season_xg.csv",
    "match_forecast_features.csv",
    "player_match_stats.csv",
    "teams.csv",
]


def clear_table(engine, table_name: str):
    with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            conn.execute(text(f"DELETE FROM {table_name};"))
        else:
            conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))


def load_matches(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    table_name = "staging_matches"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_team_season_summary(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    table_name = "staging_team_season_summary"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_player_team_seasons(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    rename_map = {
        "currentClub": "current_club",
        "jerseyNumber": "jersey_number",
        "isLoan": "is_loan",
        "loanedFrom": "loaned_from",
    }
    df = df.rename(columns=rename_map)

    if "is_loan" in df.columns:
        df["is_loan"] = df["is_loan"].map({True: True, False: False, "True": True, "False": False, np.nan: None})

    table_name = "staging_player_team_seasons"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_team_match_xg(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    rename_map = {
        "id": "understat_id",
        "xG": "xg",
        "xGA": "xga",
        "npxG": "npxg",
        "npxGA": "npxga",
        "npxGD": "npxgd",
    }
    df = df.rename(columns=rename_map)

    table_name = "staging_team_match_xg"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_player_season_xg(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    rename_map = {
        "xG": "xg",
        "xA": "xa",
        "npxG": "npxg",
        "xGChain": "xgchain",
        "xGBuildup": "xgbuildup",
    }
    df = df.rename(columns=rename_map)

    table_name = "staging_player_season_xg"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_match_forecast_features(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    df.columns = [col.lower() for col in df.columns]

    table_name = "staging_match_forecast_features"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_player_match_stats(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    rename_map = {
        "id": "understat_id",
        "xG": "xg",
        "xA": "xa",
        "xGChain": "xgchain",
        "xGBuildup": "xgbuildup",
        "positionOrder": "position_order",
    }
    df = df.rename(columns=rename_map)

    table_name = "staging_player_match_stats"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def load_teams(engine, csv_path: Path):
    logger.info(f"Processing {csv_path.name}...")
    df = pd.read_csv(csv_path, keep_default_na=True)
    csv_rows = len(df)

    table_name = "staging_teams"
    clear_table(engine, table_name)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method=None
    )

    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

    logger.info(f"✓ {csv_path.name} -> {table_name}: CSV rows={csv_rows}, DB rows={db_rows}")
    assert csv_rows == db_rows, f"Mismatch in {table_name}: {csv_rows} vs {db_rows}"


def main():
    logger.info("=== Starting Phase 0 Data Loader ===")
    logger.info(f"Data directory: {DATA_DIR}")

    missing_files = [f for f in CSV_FILES if not (DATA_DIR / f).exists()]
    if missing_files:
        logger.error(f"Missing CSV files in {DATA_DIR}: {missing_files}")
        sys.exit(1)

    engine = create_engine(settings.DATABASE_URL)

    try:
        load_matches(engine, DATA_DIR / "matches.csv")
        load_team_season_summary(engine, DATA_DIR / "team_season_summary.csv")
        load_player_team_seasons(engine, DATA_DIR / "player_team_seasons.csv")
        load_team_match_xg(engine, DATA_DIR / "team_match_xg.csv")
        load_player_season_xg(engine, DATA_DIR / "player_season_xg.csv")
        load_match_forecast_features(engine, DATA_DIR / "match_forecast_features.csv")
        load_player_match_stats(engine, DATA_DIR / "player_match_stats.csv")
        load_teams(engine, DATA_DIR / "teams.csv")

        logger.info("=== Data Loader Completed Successfully! ===")
    except Exception as e:
        logger.error(f"Data loading failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
