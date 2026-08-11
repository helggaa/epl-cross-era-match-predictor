"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Staging Matches
    op.create_table(
        'staging_matches',
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('division', sa.String(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('home_team', sa.String(), nullable=True),
        sa.Column('away_team', sa.String(), nullable=True),
        sa.Column('home_goals', sa.Integer(), nullable=True),
        sa.Column('away_goals', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(), nullable=True),
        sa.Column('ht_home_goals', sa.Float(), nullable=True),
        sa.Column('ht_away_goals', sa.Float(), nullable=True),
        sa.Column('ht_result', sa.String(), nullable=True),
        sa.Column('referee', sa.String(), nullable=True),
        sa.Column('home_shots', sa.Float(), nullable=True),
        sa.Column('away_shots', sa.Float(), nullable=True),
        sa.Column('home_shots_target', sa.Float(), nullable=True),
        sa.Column('away_shots_target', sa.Float(), nullable=True),
        sa.Column('home_fouls', sa.Float(), nullable=True),
        sa.Column('away_fouls', sa.Float(), nullable=True),
        sa.Column('home_corners', sa.Float(), nullable=True),
        sa.Column('away_corners', sa.Float(), nullable=True),
        sa.Column('home_yellow', sa.Float(), nullable=True),
        sa.Column('away_yellow', sa.Float(), nullable=True),
        sa.Column('home_red', sa.Float(), nullable=True),
        sa.Column('away_red', sa.Float(), nullable=True),
        sa.Column('odds_b365_home', sa.Float(), nullable=True),
        sa.Column('odds_b365_draw', sa.Float(), nullable=True),
        sa.Column('odds_b365_away', sa.Float(), nullable=True),
        sa.Column('odds_avg_home', sa.Float(), nullable=True),
        sa.Column('odds_avg_draw', sa.Float(), nullable=True),
        sa.Column('odds_avg_away', sa.Float(), nullable=True),
        sa.Column('season', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('match_id')
    )
    op.create_index('idx_staging_matches_match_id', 'staging_matches', ['match_id'])
    op.create_index('idx_staging_matches_date', 'staging_matches', ['date'])
    op.create_index('idx_staging_matches_home', 'staging_matches', ['home_team'])
    op.create_index('idx_staging_matches_away', 'staging_matches', ['away_team'])
    op.create_index('idx_staging_matches_season', 'staging_matches', ['season'])
    op.create_index('idx_staging_matches_season_home', 'staging_matches', ['season', 'home_team'])
    op.create_index('idx_staging_matches_season_away', 'staging_matches', ['season', 'away_team'])

    # 2. Staging Team Season Summary
    op.create_table(
        'staging_team_season_summary',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('season', sa.String(), nullable=True),
        sa.Column('team', sa.String(), nullable=True),
        sa.Column('played', sa.Integer(), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('draws', sa.Integer(), nullable=True),
        sa.Column('losses', sa.Integer(), nullable=True),
        sa.Column('goals_for', sa.Float(), nullable=True),
        sa.Column('goals_against', sa.Float(), nullable=True),
        sa.Column('goal_diff', sa.Float(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_tss_team', 'staging_team_season_summary', ['team'])
    op.create_index('idx_staging_tss_season', 'staging_team_season_summary', ['season'])
    op.create_index('idx_staging_tss_team_season', 'staging_team_season_summary', ['team', 'season'])

    # 3. Staging Player Team Seasons
    op.create_table(
        'staging_player_team_seasons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('position', sa.String(), nullable=True),
        sa.Column('foot', sa.String(), nullable=True),
        sa.Column('player_name', sa.String(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('nationality', sa.String(), nullable=True),
        sa.Column('market_value', sa.String(), nullable=True),
        sa.Column('signed_from', sa.String(), nullable=True),
        sa.Column('age', sa.Float(), nullable=True),
        sa.Column('date_of_birth', sa.String(), nullable=True),
        sa.Column('current_club', sa.String(), nullable=True),
        sa.Column('jersey_number', sa.String(), nullable=True),
        sa.Column('is_loan', sa.Boolean(), nullable=True),
        sa.Column('loaned_from', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('season_start_year', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_pts_player_name', 'staging_player_team_seasons', ['player_name'])
    op.create_index('idx_staging_pts_team_name', 'staging_player_team_seasons', ['team_name'])
    op.create_index('idx_staging_pts_season_start_year', 'staging_player_team_seasons', ['season_start_year'])
    op.create_index('idx_staging_pts_team_season', 'staging_player_team_seasons', ['team_name', 'season_start_year'])

    # 4. Staging Team Match XG
    op.create_table(
        'staging_team_match_xg',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('understat_id', sa.Integer(), nullable=True),
        sa.Column('league', sa.String(), nullable=True),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('club_name', sa.String(), nullable=True),
        sa.Column('home_away', sa.String(), nullable=True),
        sa.Column('xg', sa.Float(), nullable=True),
        sa.Column('xga', sa.Float(), nullable=True),
        sa.Column('npxg', sa.Float(), nullable=True),
        sa.Column('npxga', sa.Float(), nullable=True),
        sa.Column('ppda', sa.Float(), nullable=True),
        sa.Column('ppda_allowed', sa.Float(), nullable=True),
        sa.Column('deep', sa.Float(), nullable=True),
        sa.Column('deep_allowed', sa.Float(), nullable=True),
        sa.Column('scored', sa.Integer(), nullable=True),
        sa.Column('missed', sa.Integer(), nullable=True),
        sa.Column('xpts', sa.Float(), nullable=True),
        sa.Column('result', sa.String(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('draws', sa.Integer(), nullable=True),
        sa.Column('loses', sa.Integer(), nullable=True),
        sa.Column('pts', sa.Integer(), nullable=True),
        sa.Column('npxgd', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_tmx_club', 'staging_team_match_xg', ['club_name'])
    op.create_index('idx_staging_tmx_season', 'staging_team_match_xg', ['season'])
    op.create_index('idx_staging_tmx_club_season', 'staging_team_match_xg', ['club_name', 'season'])

    # 5. Staging Player Season XG
    op.create_table(
        'staging_player_season_xg',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('position', sa.String(), nullable=True),
        sa.Column('games', sa.Integer(), nullable=True),
        sa.Column('goals', sa.Integer(), nullable=True),
        sa.Column('shots', sa.Integer(), nullable=True),
        sa.Column('time', sa.Integer(), nullable=True),
        sa.Column('xg', sa.Float(), nullable=True),
        sa.Column('assists', sa.Integer(), nullable=True),
        sa.Column('xa', sa.Float(), nullable=True),
        sa.Column('key_passes', sa.Integer(), nullable=True),
        sa.Column('team', sa.String(), nullable=True),
        sa.Column('yellow', sa.Integer(), nullable=True),
        sa.Column('red', sa.Integer(), nullable=True),
        sa.Column('npg', sa.Integer(), nullable=True),
        sa.Column('npxg', sa.Float(), nullable=True),
        sa.Column('xgchain', sa.Float(), nullable=True),
        sa.Column('xgbuildup', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_psx_player_id', 'staging_player_season_xg', ['player_id'])
    op.create_index('idx_staging_psx_name', 'staging_player_season_xg', ['name'])
    op.create_index('idx_staging_psx_team', 'staging_player_season_xg', ['team'])
    op.create_index('idx_staging_psx_season', 'staging_player_season_xg', ['season'])
    op.create_index('idx_staging_psx_team_season', 'staging_player_season_xg', ['team', 'season'])

    # 6. Staging Match Forecast Features
    op.create_table(
        'staging_match_forecast_features',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('home_team', sa.String(), nullable=True),
        sa.Column('away_team', sa.String(), nullable=True),
        sa.Column('u_forecast_w', sa.Float(), nullable=True),
        sa.Column('u_forecast_d', sa.Float(), nullable=True),
        sa.Column('u_forecast_l', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_goals', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_assists', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_shots', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_key_passes', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_xg', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_xa', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_yellow_card', sa.Float(), nullable=True),
        sa.Column('u_home_roster_total_red_card', sa.Float(), nullable=True),
        sa.Column('u_home_shots_directfreekick', sa.Float(), nullable=True),
        sa.Column('u_home_shots_fromcorner', sa.Float(), nullable=True),
        sa.Column('u_home_shots_openplay', sa.Float(), nullable=True),
        sa.Column('u_home_shots_penalty', sa.Float(), nullable=True),
        sa.Column('u_home_shots_setpiece', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_goals', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_assists', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_shots', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_key_passes', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_xg', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_xa', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_yellow_card', sa.Float(), nullable=True),
        sa.Column('u_away_roster_total_red_card', sa.Float(), nullable=True),
        sa.Column('u_away_shots_directfreekick', sa.Float(), nullable=True),
        sa.Column('u_away_shots_fromcorner', sa.Float(), nullable=True),
        sa.Column('u_away_shots_openplay', sa.Float(), nullable=True),
        sa.Column('u_away_shots_penalty', sa.Float(), nullable=True),
        sa.Column('u_away_shots_setpiece', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_mff_match_id', 'staging_match_forecast_features', ['match_id'])

    # 7. Staging Player Match Stats
    op.create_table(
        'staging_player_match_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('understat_id', sa.Integer(), nullable=True),
        sa.Column('goals', sa.Integer(), nullable=True),
        sa.Column('own_goals', sa.Integer(), nullable=True),
        sa.Column('shots', sa.Integer(), nullable=True),
        sa.Column('xg', sa.Float(), nullable=True),
        sa.Column('time', sa.Integer(), nullable=True),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('position', sa.String(), nullable=True),
        sa.Column('player', sa.String(), nullable=True),
        sa.Column('h_a', sa.String(), nullable=True),
        sa.Column('yellow_card', sa.Integer(), nullable=True),
        sa.Column('red_card', sa.Integer(), nullable=True),
        sa.Column('roster_in', sa.String(), nullable=True),
        sa.Column('roster_out', sa.String(), nullable=True),
        sa.Column('key_passes', sa.Integer(), nullable=True),
        sa.Column('assists', sa.Integer(), nullable=True),
        sa.Column('xa', sa.Float(), nullable=True),
        sa.Column('xgchain', sa.Float(), nullable=True),
        sa.Column('xgbuildup', sa.Float(), nullable=True),
        sa.Column('position_order', sa.Integer(), nullable=True),
        sa.Column('match_id', sa.Integer(), nullable=True),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('side', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_pms_player_id', 'staging_player_match_stats', ['player_id'])
    op.create_index('idx_staging_pms_match_id', 'staging_player_match_stats', ['match_id'])
    op.create_index('idx_staging_pms_season', 'staging_player_match_stats', ['season'])
    op.create_index('idx_staging_pms_match_player', 'staging_player_match_stats', ['match_id', 'player_id'])

    # 8. Staging Teams
    op.create_table(
        'staging_teams',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_staging_teams_name', 'staging_teams', ['team_name'])

    # --- Application Tables ---

    # 9. Hypothetical Matchups
    op.create_table(
        'hypothetical_matchups',
        sa.Column('hypothetical_id', sa.String(), nullable=False),
        sa.Column('team_a_id', sa.String(), nullable=True),
        sa.Column('team_a_season', sa.String(), nullable=True),
        sa.Column('team_b_id', sa.String(), nullable=True),
        sa.Column('team_b_season', sa.String(), nullable=True),
        sa.Column('team_a_elo', sa.Float(), nullable=True),
        sa.Column('team_b_elo', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('hypothetical_id')
    )

    # 10. Predictions
    op.create_table(
        'predictions',
        sa.Column('prediction_id', sa.String(), nullable=False),
        sa.Column('hypothetical_id', sa.String(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('home_win_prob', sa.Float(), nullable=True),
        sa.Column('draw_prob', sa.Float(), nullable=True),
        sa.Column('away_win_prob', sa.Float(), nullable=True),
        sa.Column('predicted_home_goals', sa.Float(), nullable=True),
        sa.Column('predicted_away_goals', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hypothetical_id'], ['hypothetical_matchups.hypothetical_id'], ),
        sa.PrimaryKeyConstraint('prediction_id')
    )

    # 11. Prediction Explanations
    op.create_table(
        'prediction_explanations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('prediction_id', sa.String(), nullable=True),
        sa.Column('feature_name', sa.String(), nullable=True),
        sa.Column('feature_value', sa.Float(), nullable=True),
        sa.Column('shap_value', sa.Float(), nullable=True),
        sa.Column('favors', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.prediction_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_prediction_explanations_pred_id', 'prediction_explanations', ['prediction_id'])

    # 12. Prediction Narratives
    op.create_table(
        'prediction_narratives',
        sa.Column('prediction_id', sa.String(), nullable=False),
        sa.Column('llm_model', sa.String(), nullable=True),
        sa.Column('narrative_team_a_win', sa.String(), nullable=True),
        sa.Column('narrative_team_a_lose', sa.String(), nullable=True),
        sa.Column('narrative_team_b_win', sa.String(), nullable=True),
        sa.Column('narrative_team_b_lose', sa.String(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.prediction_id'], ),
        sa.PrimaryKeyConstraint('prediction_id')
    )

    # 13. Player Event Rates
    op.create_table(
        'player_event_rates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('season', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('goals_per_90', sa.Float(), nullable=True),
        sa.Column('assists_per_90', sa.Float(), nullable=True),
        sa.Column('share_of_team_goals', sa.Float(), nullable=True),
        sa.Column('share_of_team_cards', sa.Float(), nullable=True),
        sa.Column('minutes_played_total', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_per_player_season_team', 'player_event_rates', ['player_id', 'season', 'team_id'])

    # 14. Simulation Runs
    op.create_table(
        'simulation_runs',
        sa.Column('sim_id', sa.String(), nullable=False),
        sa.Column('hypothetical_id', sa.String(), nullable=True),
        sa.Column('run_number', sa.Integer(), nullable=True),
        sa.Column('final_score_team_a', sa.Integer(), nullable=True),
        sa.Column('final_score_team_b', sa.Integer(), nullable=True),
        sa.Column('event_log', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hypothetical_id'], ['hypothetical_matchups.hypothetical_id'], ),
        sa.PrimaryKeyConstraint('sim_id')
    )


def downgrade() -> None:
    op.drop_table('simulation_runs')
    op.drop_table('player_event_rates')
    op.drop_table('prediction_narratives')
    op.drop_table('prediction_explanations')
    op.drop_table('predictions')
    op.drop_table('hypothetical_matchups')
    op.drop_table('staging_teams')
    op.drop_table('staging_player_match_stats')
    op.drop_table('staging_match_forecast_features')
    op.drop_table('staging_player_season_xg')
    op.drop_table('staging_team_match_xg')
    op.drop_table('staging_player_team_seasons')
    op.drop_table('staging_team_season_summary')
    op.drop_table('staging_matches')
