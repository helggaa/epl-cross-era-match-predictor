import React from 'react';

export default function FeatureAttribution({ features, teamA, teamB }) {
  if (!features || features.length === 0) return null;

  return (
    <div className="card features-card">
      <h3 className="card-subtitle">Key Statistical Drivers</h3>
      <div className="features-list">
        {features.map((feat, idx) => {
          let favorsLabel = 'Neutral';
          let badgeClass = 'favors-neutral';

          if (feat.favors === 'team_a') {
            favorsLabel = `Favors ${teamA.name}`;
            badgeClass = 'favors-team-a';
          } else if (feat.favors === 'team_b') {
            favorsLabel = `Favors ${teamB.name}`;
            badgeClass = 'favors-team-b';
          }

          return (
            <div key={idx} className="feature-item">
              <div className="feature-info">
                <span className="feature-name">{feat.description || feat.feature_name}</span>
                <span className="feature-val">Value: {feat.feature_value !== null ? feat.feature_value : 'N/A'}</span>
              </div>
              <span className={`favors-badge ${badgeClass}`}>{favorsLabel}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
