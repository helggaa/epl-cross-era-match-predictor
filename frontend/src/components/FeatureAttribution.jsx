import React from 'react';
import { getTeamMeta } from '../utils/teamMetadata';

export default function FeatureAttribution({ features, teamA, teamB }) {
  if (!features || features.length === 0) return null;

  const metaA = getTeamMeta(teamA.name);
  const metaB = getTeamMeta(teamB.name);

  return (
    <div className="card features-card glass-panel">
      <div className="card-header-bar">
        <div>
          <span className="card-tag">STATISTICAL COMPARISON</span>
          <h3 className="card-title">Key Match Drivers & Metrics</h3>
        </div>
        <span className="drivers-count">{features.length} Factors Analyzed</span>
      </div>

      <div className="features-battle-list">
        {features.map((feat, idx) => {
          const isFavorsA = feat.favors === 'team_a';
          const isFavorsB = feat.favors === 'team_b';
          const isNeutral = !isFavorsA && !isFavorsB;

          let formattedVal = feat.feature_value !== null ? feat.feature_value : 'N/A';
          if (typeof feat.feature_value === 'number') {
            formattedVal = feat.feature_value > 100 
              ? Math.round(feat.feature_value) 
              : feat.feature_value.toFixed(2);
          }

          return (
            <div key={idx} className="feature-battle-row">
              <div className="feature-header-row">
                <span className="feature-title">
                  {feat.description || feat.feature_name.replace(/_/g, ' ')}
                </span>
                <span className="feature-raw-val">
                  Value: <span className="val-bold">{formattedVal}</span>
                </span>
              </div>

              {/* Tug-of-war indicator bar */}
              <div className="tug-of-war-container">
                <div className="tug-side team-a-side">
                  <span className="side-team-label" style={{ color: isFavorsA ? 'var(--epl-green)' : 'var(--text-muted)' }}>
                    {teamA.name}
                  </span>
                  <div className="tug-bar-track left-track">
                    <div
                      className={`tug-bar-fill left-fill ${isFavorsA ? 'active' : ''}`}
                      style={{ width: isFavorsA ? '100%' : '20%' }}
                    />
                  </div>
                </div>

                <div className="tug-center-badge">
                  {isFavorsA && (
                    <span className="tilt-badge tilt-a">← Favors {teamA.name}</span>
                  )}
                  {isFavorsB && (
                    <span className="tilt-badge tilt-b">Favors {teamB.name} →</span>
                  )}
                  {isNeutral && (
                    <span className="tilt-badge tilt-neutral">Balanced</span>
                  )}
                </div>

                <div className="tug-side team-b-side">
                  <div className="tug-bar-track right-track">
                    <div
                      className={`tug-bar-fill right-fill ${isFavorsB ? 'active' : ''}`}
                      style={{ width: isFavorsB ? '100%' : '20%' }}
                    />
                  </div>
                  <span className="side-team-label" style={{ color: isFavorsB ? 'var(--epl-magenta)' : 'var(--text-muted)' }}>
                    {teamB.name}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
