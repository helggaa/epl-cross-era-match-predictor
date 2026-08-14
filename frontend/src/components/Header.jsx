import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <div className="header-top-banner">
        <span className="live-engine-tag">
          <span className="pulse-dot"></span> 34 SEASONS ARCHIVE • 1992–2026
        </span>
        <span className="model-chip">DIXON-COLES + CHRONO ELO</span>
      </div>

      <div className="header-container">
        <div className="brand">
          <div className="brand-badge-wrapper">
            <span className="brand-badge">PREMIER LEAGUE</span>
          </div>
          <h1 className="brand-title">Cross-Era Match Predictor</h1>
        </div>
        <p className="header-subtitle">
          Simulate hypothetical clashes between legendary Premier League sides across 30+ years of football history.
        </p>
      </div>
    </header>
  );
}
