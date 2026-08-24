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
    if (loading) return;
    const tempT = teamA;
    const tempS = seasonA;
    setTeamA(teamB);
    setSeasonA(seasonB);
    setTeamB(tempT);
    setSeasonB(tempS);
  };

  const handleApplyPreset = (preset) => {
    if (loading) return;
    setTeamA(preset.teamA);
    setSeasonA(preset.seasonA);
    setTeamB(preset.teamB);
    setSeasonB(preset.seasonB);
  };

  return (
    <div className={`card selector-card ${loading ? 'selector-busy' : ''}`}>
      {/* Preset Matchups Section */}
      <div className="presets-bar">
        <span className="presets-title">Curated Matchups</span>
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
                disabled={loading}
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
        {/* Team A Card (Home) */}
        <div
          className="team-card home-team-card"
          style={{ '--team-accent': metaA.primaryColor }}
        >
          <div className="team-card-header">
            <div
              className="team-badge-circle"
              style={{ backgroundColor: metaA.primaryColor }}
            >
              {metaA.short}
            </div>
            <div className="team-header-info">
              <span className="venue-tag">Home Side</span>
              <h3 className="team-display-name">{teamA}</h3>
            </div>
          </div>

          <div className="picker-group">
            <label className="picker-label">Club</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={teamA}
                disabled={loading}
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
            <label className="picker-label">Season</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={seasonA}
                disabled={loading}
                onChange={(e) => setSeasonA(e.target.value)}
              >
                {seasonsForA.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            {nicknameA && <div className="season-nickname-pill">{nicknameA}</div>}
          </div>
        </div>

        {/* VS / Swap Action */}
        <div className="vs-container">
          <div className="vs-orb">
            <span className="vs-text">VS</span>
          </div>
          <button
            type="button"
            className="btn-swap-teams"
            onClick={handleSwap}
            disabled={loading}
            title="Swap Home and Away sides"
          >
            <svg
              className="swap-icon-svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M7 16V4M7 4L3 8M7 4L11 8M17 8v12M17 20l4-4M17 20l-4-4" />
            </svg>
            <span>Swap</span>
          </button>
        </div>

        {/* Team B Card (Away) */}
        <div
          className="team-card away-team-card"
          style={{ '--team-accent': metaB.primaryColor }}
        >
          <div className="team-card-header">
            <div
              className="team-badge-circle"
              style={{ backgroundColor: metaB.primaryColor }}
            >
              {metaB.short}
            </div>
            <div className="team-header-info">
              <span className="venue-tag">Away Side</span>
              <h3 className="team-display-name">{teamB}</h3>
            </div>
          </div>

          <div className="picker-group">
            <label className="picker-label">Club</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={teamB}
                disabled={loading}
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
            <label className="picker-label">Season</label>
            <div className="select-wrapper">
              <select
                className="select-input"
                value={seasonB}
                disabled={loading}
                onChange={(e) => setSeasonB(e.target.value)}
              >
                {seasonsForB.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            {nicknameB && <div className="season-nickname-pill">{nicknameB}</div>}
          </div>
        </div>
      </div>

      {isSameTeamSeason && (
        <div className="validation-alert">
          <span className="alert-bullet"></span>
          <span>
            Please select different teams or seasons to simulate a cross-era matchup.
          </span>
        </div>
      )}

      <button
        type="button"
        className={`btn-predict-cta ${loading ? 'btn-simulating' : ''}`}
        onClick={onPredict}
        disabled={loading || isSameTeamSeason || !teamA || !seasonA || !teamB || !seasonB}
      >
        {loading ? (
          <div className="cta-loading-content">
            <span className="cta-spinner"></span>
            <div className="cta-loading-text-group">
              <span className="cta-main-text">Simulating Matchup & Tactical Breakdown...</span>
              <span className="cta-sub-text">Bivariate Poisson • Elo • Tactical Synthesis</span>
            </div>
          </div>
        ) : (
          <div className="cta-idle-content">
            <span className="cta-main-text">Simulate Matchup</span>
            <span className="cta-sub-text">Bivariate Poisson & Elo Calculation</span>
          </div>
        )}
      </button>
    </div>
  );
}
