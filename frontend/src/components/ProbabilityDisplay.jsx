import React from 'react';

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

  const hasExpectedGoals =
    predicted_home_goals !== undefined &&
    predicted_home_goals !== null &&
    predicted_away_goals !== undefined &&
    predicted_away_goals !== null;

  return (
    <div className="card probability-card">
      <h2 className="card-title">Match Outcome Probabilities</h2>

      <div className="prob-overview">
        <div className="prob-team home">
          <span className="team-name">{team_a.name} ({team_a.season})</span>
          <span className="prob-value">{homePct}%</span>
          <span className="elo-tag">Elo: {Math.round(team_a.elo_rating)}</span>
        </div>

        <div className="prob-team draw">
          <span className="team-name">Draw</span>
          <span className="prob-value">{drawPct}%</span>
        </div>

        <div className="prob-team away">
          <span className="team-name">{team_b.name} ({team_b.season})</span>
          <span className="prob-value">{awayPct}%</span>
          <span className="elo-tag">Elo: {Math.round(team_b.elo_rating)}</span>
        </div>
      </div>

      <div className="prob-bar-container">
        <div className="prob-bar home-bar" style={{ width: `${homePct}%` }} title={`Home Win: ${homePct}%`} />
        <div className="prob-bar draw-bar" style={{ width: `${drawPct}%` }} title={`Draw: ${drawPct}%`} />
        <div className="prob-bar away-bar" style={{ width: `${awayPct}%` }} title={`Away Win: ${awayPct}%`} />
      </div>

      {hasExpectedGoals && (
        <div className="expected-scoreline">
          <span className="scoreline-label">Modeled Expected Scoreline:</span>
          <span className="scoreline-value">
            {team_a.name} {predicted_home_goals.toFixed(2)} – {predicted_away_goals.toFixed(2)} {team_b.name}
          </span>
        </div>
      )}
    </div>
  );
}
