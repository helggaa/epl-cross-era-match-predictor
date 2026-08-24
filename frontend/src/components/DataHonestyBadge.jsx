import React from 'react';

export default function DataHonestyBadge({ reducedConfidence }) {
  if (reducedConfidence === undefined || reducedConfidence === null) return null;

  return (
    <div className={`data-honesty-banner ${reducedConfidence ? 'banner-limited' : 'banner-full'}`}>
      <div className="honesty-indicator">
        <span className="honesty-dot"></span>
        <span className="honesty-tag">
          {reducedConfidence ? 'DATA COVERAGE: HISTORICAL STATISTICAL BASELINE' : 'DATA COVERAGE: FULL xG & TACTICAL METRICS'}
        </span>
      </div>
      <p className="honesty-desc">
        {reducedConfidence
          ? 'Granular tracking metrics (xG, press sequences) are unavailable for older historical eras. The model utilizes comprehensive goal rates, match results, and era-calibrated Elo parameters.'
          : 'Full advanced match tracking active. Predictions incorporate expected goals (xG), shot efficiency distributions, and detailed team metrics.'}
      </p>
    </div>
  );
}
