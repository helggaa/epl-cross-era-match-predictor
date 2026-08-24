import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <div className="header-meta-row">
        <span className="header-meta-item">
          <span className="status-dot"></span> Historical Archive 1992–2026
        </span>
        <span className="meta-divider">•</span>
        <span className="header-meta-item">34 Seasons</span>
        <span className="meta-divider">•</span>
        <span className="header-meta-item">Dixon-Coles & Dynamic Elo</span>
      </div>

      <div className="header-brand">
        <div className="brand-category">PREMIER LEAGUE ANALYTICS</div>
        <h1 className="brand-title">Cross-Era Match Predictor</h1>
        <p className="brand-subtitle">
          Simulate historical Premier League matchups using bivariate Poisson goal modeling and era-adjusted Elo ratings.
        </p>
      </div>
    </header>
  );
}
