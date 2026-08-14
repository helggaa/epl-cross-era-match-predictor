import React from 'react';
import { getTeamMeta } from '../utils/teamMetadata';

export default function ProbabilityDisplay({ prediction }) {
  if (!prediction) return null;

  const {
    home_win_prob,
    draw_prob,
    away_win_prob,
    predicted_home_goals,
    predicted_away_goals,
    team_a,
    team_b,
  } = prediction;

  const homePct = Math.round(home_win_prob * 100);
  const drawPct = Math.round(draw_prob * 100);
  const awayPct = Math.round(away_win_prob * 100);

  const metaA = getTeamMeta(team_a.name);
  const metaB = getTeamMeta(team_b.name);

  const eloDiff = Math.round((team_a.elo_rating || 1500) - (team_b.elo_rating || 1500));
  const eloFavorsA = eloDiff > 0;

  const hasExpectedGoals =
    predicted_home_goals !== undefined &&
    predicted_home_goals !== null &&
    predicted_away_goals !== undefined &&
    predicted_away_goals !== null;

  return (
    <div className="card probability-card glass-panel">
      <div className="card-header-bar">
        <div>
          <span className="card-tag">BROADCAST PROJECTION</span>
          <h2 className="card-title">Match Outcome Probabilities</h2>
        </div>
        <div className="elo-diff-pill">
          <span className="elo-diff-label">Elo Delta:</span>
          <span className="elo-diff-val" style={{ color: eloFavorsA ? 'var(--epl-green)' : 'var(--epl-magenta)' }}>
            {eloFavorsA ? `+${eloDiff} ${team_a.name}` : `+${Math.abs(eloDiff)} ${team_b.name}`}
          </span>
        </div>
      </div>

      {/* 3-Way Probability Battle Cards */}
      <div className="prob-battle-grid">
        {/* Team A Win Card */}
        <div
          className={`prob-outcome-card home-win ${homePct >= awayPct && homePct >= drawPct ? 'favorite' : ''}`}
          style={{ '--accent-color': metaA.primaryColor }}
        >
          <div className="outcome-top">
            <span className="outcome-role">HOME WIN</span>
            {homePct >= awayPct && homePct >= drawPct && (
              <span className="fav-badge">FAVORITE</span>
            )}
          </div>
          <div className="outcome-team-name">{team_a.name}</div>
          <div className="outcome-season-sub">{team_a.season}</div>
          <div className="outcome-percent-huge" style={{ color: 'var(--epl-green)' }}>
            {homePct}%
          </div>
          <div className="outcome-elo-badge">Elo: {Math.round(team_a.elo_rating)}</div>
        </div>

        {/* Draw Card */}
        <div className={`prob-outcome-card draw-card ${drawPct >= homePct && drawPct >= awayPct ? 'favorite' : ''}`}>
          <div className="outcome-top">
            <span className="outcome-role">STALEMATE</span>
          </div>
          <div className="outcome-team-name">Draw</div>
          <div className="outcome-season-sub">90 Min Parity</div>
          <div className="outcome-percent-huge draw-percent">
            {drawPct}%
          </div>
          <div className="outcome-elo-badge">Poisson Overlap</div>
        </div>

        {/* Team B Win Card */}
        <div
          className={`prob-outcome-card away-win ${awayPct >= homePct && awayPct >= drawPct ? 'favorite' : ''}`}
          style={{ '--accent-color': metaB.primaryColor }}
        >
          <div className="outcome-top">
            <span className="outcome-role">AWAY WIN</span>
            {awayPct >= homePct && awayPct >= drawPct && (
              <span className="fav-badge">FAVORITE</span>
            )}
          </div>
          <div className="outcome-team-name">{team_b.name}</div>
          <div className="outcome-season-sub">{team_b.season}</div>
          <div className="outcome-percent-huge" style={{ color: 'var(--epl-magenta)' }}>
            {awayPct}%
          </div>
          <div className="outcome-elo-badge">Elo: {Math.round(team_b.elo_rating)}</div>
        </div>
      </div>

      {/* Segmented Momentum Bar */}
      <div className="prob-meter-wrapper">
        <div className="prob-meter-labels">
          <span style={{ color: 'var(--epl-green)' }}>{team_a.name} ({homePct}%)</span>
          <span style={{ color: '#94a3b8' }}>Draw ({drawPct}%)</span>
          <span style={{ color: 'var(--epl-magenta)' }}>{team_b.name} ({awayPct}%)</span>
        </div>
        <div className="prob-bar-container">
          <div className="prob-bar home-bar" style={{ width: `${homePct}%` }} />
          <div className="prob-bar draw-bar" style={{ width: `${drawPct}%` }} />
          <div className="prob-bar away-bar" style={{ width: `${awayPct}%` }} />
        </div>
      </div>

      {/* Stadium LED Scoreboard */}
      {hasExpectedGoals && (
        <div className="scoreboard-panel">
          <div className="scoreboard-header">
            <span className="scoreboard-title">🏟️ DIXON-COLES MODELED SCORELINE</span>
            <span className="live-tag">EXPECTED GOALS (xG PROJECTION)</span>
          </div>
          <div className="scoreboard-display">
            <div className="scoreboard-team-box home-side">
              <span className="score-team-name">{team_a.name}</span>
              <span className="score-season-label">{team_a.season}</span>
            </div>
            <div className="scoreboard-digits">
              <span className="score-num">{predicted_home_goals.toFixed(2)}</span>
              <span className="score-divider">:</span>
              <span className="score-num">{predicted_away_goals.toFixed(2)}</span>
            </div>
            <div className="scoreboard-team-box away-side">
              <span className="score-team-name">{team_b.name}</span>
              <span className="score-season-label">{team_b.season}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
