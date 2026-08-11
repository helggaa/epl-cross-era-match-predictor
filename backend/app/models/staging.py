from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Index
from app.db.base import Base


class StagingMatches(Base):
    __tablename__ = "staging_matches"

    match_id = Column(Integer, primary_key=True, index=True)
    division = Column(String, nullable=True)
    date = Column(String, index=True)
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    result = Column(String, nullable=True)
    ht_home_goals = Column(Float, nullable=True)
    ht_away_goals = Column(Float, nullable=True)
    ht_result = Column(String, nullable=True)
    referee = Column(String, nullable=True)
    home_shots = Column(Float, nullable=True)
    away_shots = Column(Float, nullable=True)
    home_shots_target = Column(Float, nullable=True)
    away_shots_target = Column(Float, nullable=True)
    home_fouls = Column(Float, nullable=True)
    away_fouls = Column(Float, nullable=True)
    home_corners = Column(Float, nullable=True)
    away_corners = Column(Float, nullable=True)
    home_yellow = Column(Float, nullable=True)
    away_yellow = Column(Float, nullable=True)
    home_red = Column(Float, nullable=True)
    away_red = Column(Float, nullable=True)
    odds_b365_home = Column(Float, nullable=True)
    odds_b365_draw = Column(Float, nullable=True)
    odds_b365_away = Column(Float, nullable=True)
    odds_avg_home = Column(Float, nullable=True)
    odds_avg_draw = Column(Float, nullable=True)
    odds_avg_away = Column(Float, nullable=True)
    season = Column(String, index=True)

    __table_args__ = (
        Index("idx_staging_matches_season_home", "season", "home_team"),
        Index("idx_staging_matches_season_away", "season", "away_team"),
    )


class StagingTeamSeasonSummary(Base):
    __tablename__ = "staging_team_season_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(String, index=True)
    team = Column(String, index=True)
    played = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)
    draws = Column(Integer, nullable=True)
    losses = Column(Integer, nullable=True)
    goals_for = Column(Float, nullable=True)
    goals_against = Column(Float, nullable=True)
    goal_diff = Column(Float, nullable=True)
    points = Column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_staging_tss_team_season", "team", "season"),
    )


class StagingPlayerTeamSeasons(Base):
    __tablename__ = "staging_player_team_seasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(String, nullable=True)
    foot = Column(String, nullable=True)
    player_name = Column(String, index=True)
    height = Column(Float, nullable=True)
    player_id = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    market_value = Column(String, nullable=True)
    signed_from = Column(String, nullable=True)
    age = Column(Float, nullable=True)
    date_of_birth = Column(String, nullable=True)
    current_club = Column(String, nullable=True)
    jersey_number = Column(String, nullable=True)
    is_loan = Column(Boolean, nullable=True)
    loaned_from = Column(String, nullable=True)
    team_id = Column(String, nullable=True)
    team_name = Column(String, index=True)
    season_start_year = Column(Integer, index=True)

    __table_args__ = (
        Index("idx_staging_pts_team_season", "team_name", "season_start_year"),
    )


class StagingTeamMatchXG(Base):
    __tablename__ = "staging_team_match_xg"

    id = Column(Integer, primary_key=True, autoincrement=True)
    understat_id = Column(Integer, nullable=True)
    league = Column(String, nullable=True)
    season = Column(Integer, index=True)
    club_name = Column(String, index=True)
    home_away = Column(String, nullable=True)
    xg = Column(Float, nullable=True)
    xga = Column(Float, nullable=True)
    npxg = Column(Float, nullable=True)
    npxga = Column(Float, nullable=True)
    ppda = Column(Float, nullable=True)
    ppda_allowed = Column(Float, nullable=True)
    deep = Column(Float, nullable=True)
    deep_allowed = Column(Float, nullable=True)
    scored = Column(Integer, nullable=True)
    missed = Column(Integer, nullable=True)
    xpts = Column(Float, nullable=True)
    result = Column(String, nullable=True)
    date = Column(String, nullable=True)
    wins = Column(Integer, nullable=True)
    draws = Column(Integer, nullable=True)
    loses = Column(Integer, nullable=True)
    pts = Column(Integer, nullable=True)
    npxgd = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_staging_tmx_club_season", "club_name", "season"),
    )


class StagingPlayerSeasonXG(Base):
    __tablename__ = "staging_player_season_xg"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, index=True, nullable=True)
    name = Column(String, index=True)
    season = Column(Integer, index=True)
    position = Column(String, nullable=True)
    games = Column(Integer, nullable=True)
    goals = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    time = Column(Integer, nullable=True)
    xg = Column(Float, nullable=True)
    assists = Column(Integer, nullable=True)
    xa = Column(Float, nullable=True)
    key_passes = Column(Integer, nullable=True)
    team = Column(String, index=True)
    yellow = Column(Integer, nullable=True)
    red = Column(Integer, nullable=True)
    npg = Column(Integer, nullable=True)
    npxg = Column(Float, nullable=True)
    xgchain = Column(Float, nullable=True)
    xgbuildup = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_staging_psx_team_season", "team", "season"),
    )


class StagingMatchForecastFeatures(Base):
    __tablename__ = "staging_match_forecast_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, index=True, nullable=True)
    date = Column(String, nullable=True)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    u_forecast_w = Column(Float, nullable=True)
    u_forecast_d = Column(Float, nullable=True)
    u_forecast_l = Column(Float, nullable=True)
    u_home_roster_total_goals = Column(Float, nullable=True)
    u_home_roster_total_assists = Column(Float, nullable=True)
    u_home_roster_total_shots = Column(Float, nullable=True)
    u_home_roster_total_key_passes = Column(Float, nullable=True)
    u_home_roster_total_xg = Column(Float, nullable=True)
    u_home_roster_total_xa = Column(Float, nullable=True)
    u_home_roster_total_yellow_card = Column(Float, nullable=True)
    u_home_roster_total_red_card = Column(Float, nullable=True)
    u_home_shots_directfreekick = Column(Float, nullable=True)
    u_home_shots_fromcorner = Column(Float, nullable=True)
    u_home_shots_openplay = Column(Float, nullable=True)
    u_home_shots_penalty = Column(Float, nullable=True)
    u_home_shots_setpiece = Column(Float, nullable=True)
    u_away_roster_total_goals = Column(Float, nullable=True)
    u_away_roster_total_assists = Column(Float, nullable=True)
    u_away_roster_total_shots = Column(Float, nullable=True)
    u_away_roster_total_key_passes = Column(Float, nullable=True)
    u_away_roster_total_xg = Column(Float, nullable=True)
    u_away_roster_total_xa = Column(Float, nullable=True)
    u_away_roster_total_yellow_card = Column(Float, nullable=True)
    u_away_roster_total_red_card = Column(Float, nullable=True)
    u_away_shots_directfreekick = Column(Float, nullable=True)
    u_away_shots_fromcorner = Column(Float, nullable=True)
    u_away_shots_openplay = Column(Float, nullable=True)
    u_away_shots_penalty = Column(Float, nullable=True)
    u_away_shots_setpiece = Column(Float, nullable=True)


class StagingPlayerMatchStats(Base):
    __tablename__ = "staging_player_match_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    understat_id = Column(Integer, nullable=True)
    goals = Column(Integer, nullable=True)
    own_goals = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    xg = Column(Float, nullable=True)
    time = Column(Integer, nullable=True)
    player_id = Column(String, index=True, nullable=True)
    team_id = Column(String, nullable=True)
    position = Column(String, nullable=True)
    player = Column(String, index=True, nullable=True)
    h_a = Column(String, nullable=True)
    yellow_card = Column(Integer, nullable=True)
    red_card = Column(Integer, nullable=True)
    roster_in = Column(String, nullable=True)
    roster_out = Column(String, nullable=True)
    key_passes = Column(Integer, nullable=True)
    assists = Column(Integer, nullable=True)
    xa = Column(Float, nullable=True)
    xgchain = Column(Float, nullable=True)
    xgbuildup = Column(Float, nullable=True)
    position_order = Column(Integer, nullable=True)
    match_id = Column(Integer, index=True, nullable=True)
    season = Column(Integer, index=True, nullable=True)
    side = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_staging_pms_match_player", "match_id", "player_id"),
    )


class StagingTeams(Base):
    __tablename__ = "staging_teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String, index=True)
    team_id = Column(String, nullable=True)
