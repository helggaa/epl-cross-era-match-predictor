import React from 'react';

export default function DataHonestyBadge({ reducedConfidence }) {
  if (reducedConfidence === undefined || reducedConfidence === null) return null;

  return (
    <div className={`data-honesty-banner ${reducedConfidence ? 'banner-limited' : 'banner-full'}`}>
      <div className="honesty-indicator">
        <span className="honesty-dot"></span>
        <span className="honesty-tag">
          {reducedConfidence ? 'HISTORICAL ERA DATA BASELINE' : 'FULL OPTA xG INTEGRATION'}
        </span>
      </div>
      <p className="honesty-desc">
        {reducedConfidence
          ? 'Limited data coverage — Advanced xG tracking is unavailable for at least one selected season. Dixon-Coles model utilizes all available historical shot & goal-scoring features for that era.'
          : 'xG-supported match data — Advanced expected goals (xG), shot efficiency, and deep tactical features are fully active for this matchup.'}
      </p>
    </div>
  );
}
