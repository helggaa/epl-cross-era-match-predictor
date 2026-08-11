import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import MatchupSelector from './components/MatchupSelector';
import ProbabilityDisplay from './components/ProbabilityDisplay';
import DataHonestyBadge from './components/DataHonestyBadge';
import FeatureAttribution from './components/FeatureAttribution';
import ExplanationNarratives from './components/ExplanationNarratives';

import {
  fetchTeams,
  fetchTeamSeasons,
  predictMatchup,
  fetchExplanation,
} from './services/api';

export default function App() {
  const [teams, setTeams] = useState([]);
  const [teamSeasons, setTeamSeasons] = useState([]);
  const [loadingInit, setLoadingInit] = useState(true);
  const [initError, setInitError] = useState(null);

  // Selector state
  const [teamA, setTeamA] = useState('Liverpool');
  const [seasonA, setSeasonA] = useState('2019-2020');
  const [teamB, setTeamB] = useState('Arsenal');
  const [seasonB, setSeasonB] = useState('2025-2026');

  // Prediction state
  const [prediction, setPrediction] = useState(null);
  const [loadingPredict, setLoadingPredict] = useState(false);
  const [predictError, setPredictError] = useState(null);

  // Explanation state
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  // Load initial teams and team seasons
  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoadingInit(true);
        const [teamsData, seasonsData] = await Promise.all([
          fetchTeams(),
          fetchTeamSeasons(),
        ]);
        setTeams(teamsData);
        setTeamSeasons(seasonsData);
      } catch (err) {
        setInitError(err.message || 'Failed to load teams data');
      } finally {
        setLoadingInit(false);
      }
    }
    loadInitialData();
  }, []);

  const handlePredict = useCallback(async () => {
    if (!teamA || !seasonA || !teamB || !seasonB) return;

    try {
      setLoadingPredict(true);
      setPredictError(null);
      setPrediction(null);
      setExplanation(null);

      // 1. Calculate statistical prediction immediately
      const predRes = await predictMatchup({
        team_a_id: teamA,
        team_a_season: seasonA,
        team_b_id: teamB,
        team_b_season: seasonB,
      });

      // Render probabilities & statistical prediction immediately
      setPrediction(predRes);
      setLoadingPredict(false);

      // 2. Fetch Layer 2 explanation separately (non-blocking)
      if (predRes && predRes.prediction_id) {
        setLoadingExplanation(true);
        try {
          const expRes = await fetchExplanation(predRes.prediction_id);
          setExplanation(expRes);
        } catch (expErr) {
          // Graceful handling of LLM failure without crashing prediction
          setExplanation({
            prediction_id: predRes.prediction_id,
            narrative_available: false,
            status_message: 'LLM explanation service is unconfigured or unavailable. Statistical prediction remains fully valid.',
          });
        } finally {
          setLoadingExplanation(false);
        }
      }
    } catch (err) {
      setPredictError(err.message || 'Prediction failed');
      setLoadingPredict(false);
    }
  }, [teamA, seasonA, teamB, seasonB]);

  if (loadingInit) {
    return (
      <div className="app-container">
        <Header />
        <main className="main-content">
          <div className="card loading-card">
            <p>Loading Premier League teams and historical data...</p>
          </div>
        </main>
      </div>
    );
  }

  if (initError) {
    return (
      <div className="app-container">
        <Header />
        <main className="main-content">
          <div className="card error-card">
            <h3>Error Loading Application</h3>
            <p>{initError}</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        <MatchupSelector
          teams={teams}
          teamSeasons={teamSeasons}
          teamA={teamA}
          setTeamA={setTeamA}
          seasonA={seasonA}
          setSeasonA={setSeasonA}
          teamB={teamB}
          setTeamB={setTeamB}
          seasonB={seasonB}
          setSeasonB={setSeasonB}
          onPredict={handlePredict}
          loading={loadingPredict}
        />

        {predictError && (
          <div className="card error-card">
            <h3>Prediction Error</h3>
            <p>{predictError}</p>
          </div>
        )}

        {prediction && (
          <div className="results-container">
            <DataHonestyBadge reducedConfidence={prediction.reduced_confidence} />
            <ProbabilityDisplay prediction={prediction} />
            <FeatureAttribution
              features={prediction.top_features}
              teamA={prediction.team_a}
              teamB={prediction.team_b}
            />
            <ExplanationNarratives
              explanation={explanation}
              loading={loadingExplanation}
              teamA={prediction.team_a}
              teamB={prediction.team_b}
            />
          </div>
        )}
      </main>
    </div>
  );
}
