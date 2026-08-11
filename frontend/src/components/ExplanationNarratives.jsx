import React from 'react';

export default function ExplanationNarratives({ explanation, loading, teamA, teamB }) {
  if (loading) {
    return (
      <div className="card explanation-card loading-state">
        <p>Loading natural-language explanation analysis...</p>
      </div>
    );
  }

  if (!explanation) return null;

  if (!explanation.narrative_available || !explanation.narratives) {
    return (
      <div className="card explanation-card fallback-state">
        <h3 className="card-subtitle">AI Explanation Layer</h3>
        <div className="fallback-banner">
          <span className="fallback-icon">ℹ️</span>
          <p className="fallback-message">
            {explanation.status_message || "LLM explanation service is unconfigured or unavailable. Statistical prediction remains fully valid."}
          </p>
        </div>
      </div>
    );
  }

  const { narratives } = explanation;

  return (
    <div className="card explanation-card">
      <h3 className="card-subtitle">Match Analysis Narratives</h3>
      <div className="narratives-grid">
        <div className="narrative-box win-a">
          <h4>Why {teamA.name} Wins</h4>
          <p>{narratives.why_team_a_wins}</p>
        </div>
        <div className="narrative-box lose-a">
          <h4>Why {teamA.name} Loses</h4>
          <p>{narratives.why_team_a_loses}</p>
        </div>
        <div className="narrative-box win-b">
          <h4>Why {teamB.name} Wins</h4>
          <p>{narratives.why_team_b_wins}</p>
        </div>
        <div className="narrative-box lose-b">
          <h4>Why {teamB.name} Loses</h4>
          <p>{narratives.why_team_b_loses}</p>
        </div>
      </div>
    </div>
  );
}
