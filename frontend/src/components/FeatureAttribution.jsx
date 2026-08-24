import React from 'react';
import { getTeamMeta } from '../utils/teamMetadata';

export default function FeatureAttribution({ features, teamA, teamB }) {
  if (!features || features.length === 0) return null;

  return (
    <div className="card features-card">
      <div className="card-header-bar">
        <div>
          <span className="card-tag">STATISTICAL FACTORS</span>
          <h3 className="card-title">Key Match Drivers</h3>
        </div>
        <span className="drivers-count">{features.length} Indicators Evaluated</span>
      </div>

      <div className="features-battle-list">
        {features.map((feat, idx) => {
          const isFavorsA = feat.favors === 'team_a';
          const isFavorsB = feat.favors === 'team_b';
          const isNeutral = !isFavorsA && !isFavorsB;

          let formattedVal = feat.feature_value !== null ? feat.feature_value : 'N/A';
          if (typeof feat.feature_value === 'number') {
            formattedVal =
              feat.feature_value > 100
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
                  Differential: <span className="val-bold">{formattedVal}</span>
                </span>
              </div>

              {/* Comparative Indicator */}
              <div className="tug-of-war-container">
                <div className="tug-side team-a-side">
                  <span
                    className={`side-team-label ${isFavorsA ? 'label-active' : ''}`}
                  >
                    {teamA.name}
                  </span>
                  <div className="tug-bar-track left-track">
                    <div
                      className={`tug-bar-fill left-fill ${isFavorsA ? 'active' : ''}`}
                      style={{ width: isFavorsA ? '100%' : '15%' }}
                    />
                  </div>
                </div>

                <div className="tug-center-badge">
                  {isFavorsA && (
                    <span className="tilt-badge tilt-a">Favors {teamA.name}</span>
                  )}
                  {isFavorsB && (
                    <span className="tilt-badge tilt-b">Favors {teamB.name}</span>
                  )}
                  {isNeutral && (
                    <span className="tilt-badge tilt-neutral">Neutral</span>
                  )}
                </div>

                <div className="tug-side team-b-side">
                  <div className="tug-bar-track right-track">
                    <div
                      className={`tug-bar-fill right-fill ${isFavorsB ? 'active' : ''}`}
                      style={{ width: isFavorsB ? '100%' : '15%' }}
                    />
                  </div>
                  <span
                    className={`side-team-label ${isFavorsB ? 'label-active' : ''}`}
                  >
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
