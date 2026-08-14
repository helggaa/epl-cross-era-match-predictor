import React, { useState } from 'react';
import { getTeamMeta } from '../utils/teamMetadata';

function parseReasonTag(text) {
  const lower = text.toLowerCase();
  if (lower.includes('press') || lower.includes('tactic') || lower.includes('system') || lower.includes('block')) {
    return { tag: '🧠 TACTICAL EDGE', className: 'tag-tactical' };
  }
  if (lower.includes('defense') || lower.includes('clean sheet') || lower.includes('conceded') || lower.includes('backline')) {
    return { tag: '🛡️ DEFENSE', className: 'tag-defense' };
  }
  if (lower.includes('attack') || lower.includes('goal') || lower.includes('salah') || lower.includes('haaland') || lower.includes('henry') || lower.includes('ronaldo') || lower.includes('xg')) {
    return { tag: '⚡ ATTACK POWER', className: 'tag-attack' };
  }
  if (lower.includes('anfield') || lower.includes('home') || lower.includes('crowd') || lower.includes('stadium')) {
    return { tag: '🏟️ HOME FORTRESS', className: 'tag-venue' };
  }
  if (lower.includes('meme') || lower.includes('bottle') || lower.includes('fraud') || lower.includes('bus') || lower.includes('banter')) {
    return { tag: '🎭 BANTER / MEME', className: 'tag-banter' };
  }
  return { tag: '📌 KEY FACTOR', className: 'tag-general' };
}

function ReasonList({ reasons, type = 'win' }) {
  if (!reasons || reasons.length === 0) {
    return <p className="no-reasons">No tactical breakdowns provided for this section.</p>;
  }

  return (
    <div className="reason-cards-stack">
      {reasons.map((reason, idx) => {
        const { tag, className } = parseReasonTag(reason);
        return (
          <div key={idx} className={`reason-tactical-card ${type === 'win' ? 'win-theme' : 'lose-theme'}`}>
            <div className="reason-card-top">
              <span className={`reason-category-tag ${className}`}>{tag}</span>
              <span className="reason-idx">#{idx + 1}</span>
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
      <div className="card explanation-card loading-state glass-panel">
        <div className="pundit-loading-wrapper">
          <div className="pulsing-mic">🎙️</div>
          <h3 className="loading-title">Studio Pundit AI Analysis In Progress</h3>
          <p className="loading-sub">
            Analyzing {teamA.name} ({teamA.season}) vs {teamB.name} ({teamB.season}) tactical matchups, historical data, and memes...
          </p>
          <div className="loading-progress-bar">
            <div className="progress-fill" />
          </div>
        </div>
      </div>
    );
  }

  if (!explanation) return null;

  if (!explanation.narrative_available || !explanation.narratives) {
    return (
      <div className="card explanation-card fallback-state glass-panel">
        <div className="card-header-bar">
          <div>
            <span className="card-tag">AI ANALYSIS</span>
            <h3 className="card-title">🎙️ Pundit Studio Breakdown</h3>
          </div>
        </div>
        <div className="fallback-banner">
          <span className="fallback-icon">ℹ️</span>
          <div className="fallback-content">
            <strong>Statistical Prediction Active</strong>
            <p className="fallback-message">
              {explanation.status_message ||
                'LLM explanation service is unconfigured or unavailable. The statistical prediction above remains 100% valid.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { narratives } = explanation;

  const handleCopyAnalysis = () => {
    const textToCopy = `🏆 EPL Cross-Era Clash: ${teamA.name} (${teamA.season}) vs ${teamB.name} (${teamB.season})
    
✅ Why ${teamA.name} Wins:
${narratives.why_team_a_wins.map((r, i) => `• ${r}`).join('\n')}

❌ Why ${teamA.name} Struggles:
${narratives.why_team_a_loses.map((r, i) => `• ${r}`).join('\n')}

✅ Why ${teamB.name} Wins:
${narratives.why_team_b_wins.map((r, i) => `• ${r}`).join('\n')}

❌ Why ${teamB.name} Struggles:
${narratives.why_team_b_loses.map((r, i) => `• ${r}`).join('\n')}`;

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="card explanation-card glass-panel">
      {/* Studio Header */}
      <div className="card-header-bar">
        <div>
          <span className="card-tag">AI PUNDIT STUDIO ANALYSIS</span>
          <h3 className="card-title">🎙️ Tactical & Cultural Breakdown</h3>
        </div>

        <div className="header-actions">
          {/* View Tab Buttons */}
          <div className="studio-tabs">
            <button
              type="button"
              className={`tab-btn ${activeTab === 'both' ? 'active' : ''}`}
              onClick={() => setActiveTab('both')}
            >
              ⚔️ Side-by-Side
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
            title="Copy tactical breakdown to clipboard"
          >
            {copied ? '✓ Copied!' : '📋 Share'}
          </button>
        </div>
      </div>

      {/* Two-Column or Filtered Tactical Board */}
      <div className={`narratives-layout-container layout-${activeTab}`}>
        {/* Team A Column */}
        {(activeTab === 'both' || activeTab === 'teamA') && (
          <div
            className="tactical-team-column team-a-column"
            style={{ '--club-theme': metaA.primaryColor }}
          >
            <div className="column-club-banner">
              <div className="club-badge-sm" style={{ backgroundColor: metaA.primaryColor }}>
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
                <span className="block-icon">🏆</span>
                <h5>Paths to Victory ({narratives.why_team_a_wins.length} Points)</h5>
              </div>
              <ReasonList reasons={narratives.why_team_a_wins} type="win" />
            </div>

            {/* Loses */}
            <div className="tactical-block lose-block">
              <div className="tactical-block-heading lose-head">
                <span className="block-icon">⚠️</span>
                <h5>Vulnerabilities & Risk ({narratives.why_team_a_loses.length} Points)</h5>
              </div>
              <ReasonList reasons={narratives.why_team_a_loses} type="lose" />
            </div>
          </div>
        )}

        {/* Team B Column */}
        {(activeTab === 'both' || activeTab === 'teamB') && (
          <div
            className="tactical-team-column team-b-column"
            style={{ '--club-theme': metaB.primaryColor }}
          >
            <div className="column-club-banner">
              <div className="club-badge-sm" style={{ backgroundColor: metaB.primaryColor }}>
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
                <span className="block-icon">🏆</span>
                <h5>Paths to Victory ({narratives.why_team_b_wins.length} Points)</h5>
              </div>
              <ReasonList reasons={narratives.why_team_b_wins} type="win" />
            </div>

            {/* Loses */}
            <div className="tactical-block lose-block">
              <div className="tactical-block-heading lose-head">
                <span className="block-icon">⚠️</span>
                <h5>Vulnerabilities & Risk ({narratives.why_team_b_loses.length} Points)</h5>
              </div>
              <ReasonList reasons={narratives.why_team_b_loses} type="lose" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
