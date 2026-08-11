import React from 'react';

export default function DataHonestyBadge({ reducedConfidence }) {
  if (reducedConfidence === undefined || reducedConfidence === null) return null;

  return (
    <div className={`data-honesty-badge ${reducedConfidence ? 'limited' : 'full'}`}>
      <span className="badge-icon">{reducedConfidence ? 'ℹ️' : '⚡'}</span>
      <span className="badge-text">
        {reducedConfidence
          ? "Limited data coverage — xG and advanced statistics are unavailable for at least one selected season. The prediction uses the historical features available for that era."
          : "xG-supported data available — advanced match statistics are available for the selected matchup."}
      </span>
    </div>
  );
}
