import React, { useState } from 'react';
import { getTeamMeta } from '../utils/teamMetadata';

function parseReasonTag(text) {
  const lower = text.toLowerCase();
  if (lower.includes('press') || lower.includes('tactic') || lower.includes('system') || lower.includes('block') || lower.includes('formation')) {
    return { tag: 'Tactical System', className: 'tag-tactical' };
  }
  if (lower.includes('defense') || lower.includes('clean sheet') || lower.includes('conceded') || lower.includes('backline') || lower.includes('keeper')) {
    return { tag: 'Defensive Record', className: 'tag-defense' };
  }
  if (lower.includes('attack') || lower.includes('goal') || lower.includes('salah') || lower.includes('haaland') || lower.includes('henry') || lower.includes('ronaldo') || lower.includes('xg') || lower.includes('finishing')) {
    return { tag: 'Attacking Threat', className: 'tag-attack' };
  }
  if (lower.includes('anfield') || lower.includes('home') || lower.includes('crowd') || lower.includes('stadium') || lower.includes('fortress')) {
    return { tag: 'Venue & Pitch', className: 'tag-venue' };
  }
  if (lower.includes('experience') || lower.includes('clutch') || lower.includes('mentality') || lower.includes('streak') || lower.includes('title')) {
    return { tag: 'Era Dynamics', className: 'tag-era' };
  }
  return { tag: 'Key Factor', className: 'tag-general' };
}

function ReasonList({ reasons, type = 'win' }) {
  if (!reasons || reasons.length === 0) {
    return <p className="no-reasons">No tactical points available for this section.</p>;
  }

  return (
    <div className="reason-cards-stack">
      {reasons.map((reason, idx) => {
        const { tag, className } = parseReasonTag(reason);
        return (
          <div
            key={idx}
            className={`reason-tactical-card ${type === 'win' ? 'win-theme' : 'lose-theme'}`}
          >
            <div className="reason-card-top">
              <span className={`reason-category-tag ${className}`}>{tag}</span>
              <span className="reason-idx">{idx + 1}</span>
            </div>
            <p className="reason-text">{reason}</p>
          </div>
        );
      })}
    </div>
  );
}

export default function ExplanationNarratives({ explanation, loading, teamA, teamB }) {
  const [activeTab, setActiveTab] = useState('both');
  const [copied, setCopied] = useState(false);

  const metaA = getTeamMeta(teamA.name);
  const metaB = getTeamMeta(teamB.name);

  if (loading) {
    return (
      <div className="card explanation-card loading-state">
        <div className="pundit-loading-wrapper">
          <div className="loading-spinner"></div>
          <h3 className="loading-title">Generating Tactical Matchup Analysis</h3>
          <p className="loading-sub">
            Evaluating historical data, tactical frameworks, and matchup drivers for {teamA.name} ({teamA.season}) vs {teamB.name} ({teamB.season})...
          </p>
        </div>
      </div>
    );
  }

  if (!explanation) return null;

  if (!explanation.narrative_available || !explanation.narratives) {
    return (
      <div className="card explanation-card fallback-state">
        <div className="card-header-bar">
          <div>
            <span className="card-tag">TACTICAL REPORT</span>
            <h3 className="card-title">Tactical Breakdown</h3>
          </div>
        </div>
        <div className="fallback-banner">
          <div className="fallback-content">
            <strong>Statistical Prediction Active</strong>
            <p className="fallback-message">
              {explanation.status_message ||
                'Tactical narrative generation is unavailable. The statistical and Elo predictions remain active and calibrated.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { narratives } = explanation;

  const handleCopyAnalysis = () => {
    const textToCopy = `Premier League Cross-Era Analysis: ${teamA.name} (${teamA.season}) vs ${teamB.name} (${teamB.season})

Why ${teamA.name} Can Win:
${narratives.why_team_a_wins.map((r, i) => `${i + 1}. ${r}`).join('\n')}

Vulnerabilities for ${teamA.name}:
${narratives.why_team_a_loses.map((r, i) => `${i + 1}. ${r}`).join('\n')}

Why ${teamB.name} Can Win:
${narratives.why_team_b_wins.map((r, i) => `${i + 1}. ${r}`).join('\n')}

Vulnerabilities for ${teamB.name}:
${narratives.why_team_b_loses.map((r, i) => `${i + 1}. ${r}`).join('\n')}`;

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card explanation-card">
      {/* Header */}
      <div className="card-header-bar">
        <div>
          <span className="card-tag">TACTICAL REPORT</span>
          <h3 className="card-title">Matchup Breakdown & Tactical Context</h3>
        </div>

        <div className="header-actions">
          <div className="studio-tabs">
            <button
              type="button"
              className={`tab-btn ${activeTab === 'both' ? 'active' : ''}`}
              onClick={() => setActiveTab('both')}
            >
              Side-by-Side
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === 'teamA' ? 'active' : ''}`}
              onClick={() => setActiveTab('teamA')}
            >
              {teamA.name}
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === 'teamB' ? 'active' : ''}`}
              onClick={() => setActiveTab('teamB')}
            >
              {teamB.name}
            </button>
          </div>

          <button
            type="button"
            className="btn-copy-analysis"
            onClick={handleCopyAnalysis}
            title="Copy breakdown text"
          >
            {copied ? 'Copied' : 'Copy Summary'}
          </button>
        </div>
      </div>

      {/* Breakdown Columns */}
      <div className={`narratives-layout-container layout-${activeTab}`}>
        {/* Team A Column */}
        {(activeTab === 'both' || activeTab === 'teamA') && (
          <div
            className="tactical-team-column team-a-column"
            style={{ '--club-accent': metaA.primaryColor }}
          >
            <div className="column-club-banner">
              <div
                className="club-badge-sm"
                style={{ backgroundColor: metaA.primaryColor }}
              >
                {metaA.short}
              </div>
              <div>
                <h4 className="column-club-name">{teamA.name}</h4>
                <span className="column-club-season">{teamA.season} • Home</span>
              </div>
            </div>

            {/* Wins */}
            <div className="tactical-block win-block">
              <div className="tactical-block-heading win-head">
                <span className="block-indicator win-ind"></span>
                <h5>Key Tactical Advantages ({narratives.why_team_a_wins.length})</h5>
              </div>
              <ReasonList reasons={narratives.why_team_a_wins} type="win" />
            </div>

            {/* Risks */}
            <div className="tactical-block lose-block">
              <div className="tactical-block-heading lose-head">
                <span className="block-indicator lose-ind"></span>
                <h5>Matchup Vulnerabilities ({narratives.why_team_a_loses.length})</h5>
              </div>
              <ReasonList reasons={narratives.why_team_a_loses} type="lose" />
            </div>
          </div>
        )}

        {/* Team B Column */}
        {(activeTab === 'both' || activeTab === 'teamB') && (
          <div
            className="tactical-team-column team-b-column"
            style={{ '--club-accent': metaB.primaryColor }}
          >
            <div className="column-club-banner">
              <div
                className="club-badge-sm"
                style={{ backgroundColor: metaB.primaryColor }}
              >
                {metaB.short}
              </div>
              <div>
                <h4 className="column-club-name">{teamB.name}</h4>
                <span className="column-club-season">{teamB.season} • Away</span>
              </div>
            </div>

            {/* Wins */}
            <div className="tactical-block win-block">
              <div className="tactical-block-heading win-head">
                <span className="block-indicator win-ind"></span>
                <h5>Key Tactical Advantages ({narratives.why_team_b_wins.length})</h5>
              </div>
              <ReasonList reasons={narratives.why_team_b_wins} type="win" />
            </div>

            {/* Risks */}
            <div className="tactical-block lose-block">
              <div className="tactical-block-heading lose-head">
                <span className="block-indicator lose-ind"></span>
                <h5>Matchup Vulnerabilities ({narratives.why_team_b_loses.length})</h5>
              </div>
              <ReasonList reasons={narratives.why_team_b_loses} type="lose" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
