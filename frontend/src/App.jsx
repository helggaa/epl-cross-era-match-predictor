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

  // Unified simulation state
  const [prediction, setPrediction] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loadingSimulation, setLoadingSimulation] = useState(false);
  const [simulationPhase, setSimulationPhase] = useState(0);
  const [predictError, setPredictError] = useState(null);

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

  // Multi-phase simulation status cycler during active simulation
  useEffect(() => {
    if (!loadingSimulation) {
      setSimulationPhase(0);
      return;
    }
    const timer1 = setTimeout(() => setSimulationPhase(1), 600);
    const timer2 = setTimeout(() => setSimulationPhase(2), 1400);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [loadingSimulation]);

  const handlePredict = useCallback(async () => {
    if (!teamA || !seasonA || !teamB || !seasonB || loadingSimulation) return;

    try {
      setLoadingSimulation(true);
      setPredictError(null);
      setSimulationPhase(0);

      // 1. Calculate statistical probabilities and Elo
      const predRes = await predictMatchup({
        team_a_id: teamA,
        team_a_season: seasonA,
        team_b_id: teamB,
        team_b_season: seasonB,
      });

      // 2. Concurrently fetch LLM tactical explanation before revealing full dashboard
      let expRes = null;
      if (predRes && predRes.prediction_id) {
        try {
          expRes = await fetchExplanation(predRes.prediction_id);
        } catch (expErr) {
          expRes = {
            prediction_id: predRes.prediction_id,
            narrative_available: false,
            status_message: 'Tactical narrative service unavailable. Statistical prediction remains fully valid.',
          };
        }
      }

      // 3. Synchronously reveal both prediction results and LLM explanation together
      setPrediction(predRes);
      setExplanation(expRes);
    } catch (err) {
      setPredictError(err.message || 'Prediction simulation failed');
    } finally {
      setLoadingSimulation(false);
    }
  }, [teamA, seasonA, teamB, seasonB, loadingSimulation]);

  if (loadingInit) {
    return (
      <div className="app-container">
        <Header />
        <main className="main-content">
          <div className="card loading-card">
            <div className="loading-spinner"></div>
            <p>Loading historical Premier League database...</p>
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
            <h3>Error Loading Historical Database</h3>
            <p>{initError}</p>
          </div>
        </main>
      </div>
    );
  }

  const phaseMessages = [
    'Computing Bivariate Poisson goal distribution & era-adjusted Elo ratings...',
    'Evaluating era tactical differentials, pressing metrics, and squad features...',
    'Synthesizing pundit tactical report and matchup breakdown...',
  ];

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
          loading={loadingSimulation}
        />

        {predictError && (
          <div className="card error-card">
            <h3>Prediction Error</h3>
            <p>{predictError}</p>
          </div>
        )}

        {/* Dedicated Loading State while simulation is in flight */}
        {loadingSimulation && (
          <div className="card simulation-loader-card">
            <div className="sim-loader-header">
              <div className="sim-pulse-dot"></div>
              <span className="sim-loader-tag">CROSS-ERA SIMULATION IN PROGRESS</span>
            </div>
            <h3 className="sim-loader-title">
              Simulating {teamA} ({seasonA}) vs {teamB} ({seasonB})
            </h3>
            <p className="sim-loader-status">{phaseMessages[simulationPhase]}</p>
            <div className="sim-progress-track">
              <div className="sim-progress-fill" />
            </div>
            <div className="sim-steps-row">
              <span className={`sim-step ${simulationPhase >= 0 ? 'step-active' : ''}`}>
                1. Elo & Poisson Model
              </span>
              <span className={`sim-step ${simulationPhase >= 1 ? 'step-active' : ''}`}>
                2. Tactical Factors
              </span>
              <span className={`sim-step ${simulationPhase >= 2 ? 'step-active' : ''}`}>
                3. Tactical Breakdown
              </span>
            </div>
          </div>
        )}

        {/* Results Container: Revealed only after the entire simulation completes */}
        {!loadingSimulation && prediction && (
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
              loading={false}
              teamA={prediction.team_a}
              teamB={prediction.team_b}
            />
          </div>
        )}
      </main>
    </div>
  );
}
