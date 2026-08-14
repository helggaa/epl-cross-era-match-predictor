import React from 'react';
import { getTeamMeta, getSeasonNickname, PRESET_MATCHUPS } from '../utils/teamMetadata';

export default function MatchupSelector({
  teams,
  teamSeasons,
  teamA,
  setTeamA,
  seasonA,
  setSeasonA,
  teamB,
  setTeamB,
  seasonB,
  setSeasonB,
  onPredict,
  loading,
}) {
  const seasonsForA = teamSeasons
    .filter((ts) => ts.team_name === teamA)
    .map((ts) => ts.season);

  const seasonsForB = teamSeasons
    .filter((ts) => ts.team_name === teamB)
    .map((ts) => ts.season);

  const isSameTeamSeason = teamA === teamB && seasonA === seasonB;

  const metaA = getTeamMeta(teamA);
  const metaB = getTeamMeta(teamB);
  const nicknameA = getSeasonNickname(teamA, seasonA);
  const nicknameB = getSeasonNickname(teamB, seasonB);

  const handleSwap = () => {
    const tempT = teamA;
    const tempS = seasonA;
    setTeamA(teamB);
    setSeasonA(seasonB);
    setTeamB(tempT);
    setSeasonB(tempS);
  };

  const handleApplyPreset = (preset) => {
    setTeamA(preset.teamA);
    setSeasonA(preset.seasonA);
    setTeamB(preset.teamB);
    setSeasonB(preset.seasonB);
  };

  return (
    <div className="card selector-card glass-panel">
      {/* Preset Quick Selectors */}
      <div className="presets-bar">
        <span className="presets-title">⚡ Iconic Clashes:</span>
        <div className="presets-scroll">
          {PRESET_MATCHUPS.map((p) => {
            const isActive =
              teamA === p.teamA &&
              seasonA === p.seasonA &&
              teamB === p.teamB &&
              seasonB === p.seasonB;

            return (
              <button
                key={p.id}
                type="button"
                className={`preset-chip ${isActive ? 'active' : ''}`}
                onClick={() => handleApplyPreset(p)}
                title={`${p.title} (${p.subtitle})`}
              >
                <span className="preset-badge">{p.badge}</span>
                <span className="preset-name">{p.title}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="selector-grid">
        {/* Team A Card */}
        <div
          className="team-card home-team-card"
          style={{ '--team-color': metaA.primaryColor }}
        >
          <div className="team-card-header">
            <div className="team-badge-circle" style={{ backgroundColor: metaA.primaryColor }}>
              <span className="team-short-code">{metaA.short}</span>
            </div>
            <div className="team-header-info">
              <span className="venue-tag">🏠 Home Advantage</span>
              <h3 className="team-display-name">{teamA}</h3>
            </div>
          </div>

          <div className="picker-group">
            <label className="picker-label">Select Club</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={teamA}
                onChange={(e) => {
                  const newT = e.target.value;
                  setTeamA(newT);
                  const available = teamSeasons.filter((ts) => ts.team_name === newT);
                  if (available.length > 0) setSeasonA(available[0].season);
                }}
              >
                {teams.map((t) => (
                  <option key={t.team_id} value={t.team_name}>
                    {t.team_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="picker-group">
            <label className="picker-label">Select Historic Season</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={seasonA}
                onChange={(e) => setSeasonA(e.target.value)}
              >
                {seasonsForA.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="season-nickname-pill">{nicknameA}</div>
          </div>
        </div>

        {/* VS / Battle Control */}
        <div className="vs-container">
          <div className="vs-glow-orb">
            <span className="vs-text">VS</span>
          </div>
          <button
            type="button"
            className="btn-swap-teams"
            onClick={handleSwap}
            title="Swap Home & Away Teams"
          >
            <span className="swap-icon">⇄</span>
            <span className="swap-label">Swap</span>
          </button>
        </div>

        {/* Team B Card */}
        <div
          className="team-card away-team-card"
          style={{ '--team-color': metaB.primaryColor }}
        >
          <div className="team-card-header">
            <div className="team-badge-circle" style={{ backgroundColor: metaB.primaryColor }}>
              <span className="team-short-code">{metaB.short}</span>
            </div>
            <div className="team-header-info">
              <span className="venue-tag">✈️ Away Squad</span>
              <h3 className="team-display-name">{teamB}</h3>
            </div>
          </div>

          <div className="picker-group">
            <label className="picker-label">Select Club</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={teamB}
                onChange={(e) => {
                  const newT = e.target.value;
                  setTeamB(newT);
                  const available = teamSeasons.filter((ts) => ts.team_name === newT);
                  if (available.length > 0) setSeasonB(available[0].season);
                }}
              >
                {teams.map((t) => (
                  <option key={t.team_id} value={t.team_name}>
                    {t.team_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="picker-group">
            <label className="picker-label">Select Historic Season</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={seasonB}
                onChange={(e) => setSeasonB(e.target.value)}
              >
                {seasonsForB.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="season-nickname-pill">{nicknameB}</div>
          </div>
        </div>
      </div>

      {isSameTeamSeason && (
        <div className="validation-warning animate-shake">
          <span className="warning-icon">⚠️</span>
          <span>
            Cannot simulate a matchup for the exact same team in the exact same season. Please select different teams or seasons.
          </span>
        </div>
      )}

      <button
        type="button"
        className="btn-predict-cta"
        onClick={onPredict}
        disabled={loading || isSameTeamSeason || !teamA || !seasonA || !teamB || !seasonB}
      >
        {loading ? (
          <>
            <span className="cta-spinner"></span>
            <span>Simulating 10,000 Cross-Era Iterations...</span>
          </>
        ) : (
          <>
            <span className="cta-icon">⚡</span>
            <span>Simulate Cross-Era Matchup</span>
            <span className="cta-sub">Elo & Dixon-Coles Probability Engine</span>
          </>
        )}
      </button>
    </div>
  );
}
