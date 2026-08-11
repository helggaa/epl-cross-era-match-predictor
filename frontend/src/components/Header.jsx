import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <div className="header-container">
        <div className="brand">
          <span className="brand-badge">EPL</span>
          <h1 className="brand-title">Cross-Era Match Predictor</h1>
        </div>
        <p className="header-subtitle">
          Statistical Elo & Dixon-Coles Cross-Era Matchup Simulator
        </p>
      </div>
    </header>
  );
}
