import React from 'react';

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
  // Filter seasons for Team A
  const seasonsForA = teamSeasons
    .filter((ts) => ts.team_name === teamA)
    .map((ts) => ts.season);

  // Filter seasons for Team B
  const seasonsForB = teamSeasons
    .filter((ts) => ts.team_name === teamB)
    .map((ts) => ts.season);

  const handleSwap = () => {
    const tempT = teamA;
    const tempS = seasonA;
    setTeamA(teamB);
    setSeasonA(seasonB);
    setTeamB(tempT);
    setSeasonB(tempS);
  };

  return (
    <div className="card selector-card">
      <div className="selector-grid">
        {/* Team A Picker */}
        <div className="team-picker">
          <label className="picker-label">Home Team (Team A)</label>
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

          <label className="picker-label">Season</label>
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

        {/* VS / Swap Control */}
        <div className="vs-control">
          <span className="vs-badge">VS</span>
          <button
            type="button"
            className="btn-swap"
            onClick={handleSwap}
            title="Swap Teams"
          >
            ⇄
          </button>
        </div>

        {/* Team B Picker */}
        <div className="team-picker">
          <label className="picker-label">Away Team (Team B)</label>
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

          <label className="picker-label">Season</label>
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
      </div>

      <button
        className="btn-predict"
        onClick={onPredict}
        disabled={loading || !teamA || !seasonA || !teamB || !seasonB}
      >
        {loading ? 'Calculating Prediction...' : 'Generate Matchup Prediction'}
      </button>
    </div>
  );
}
