const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `API request failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchTeams() {
  const response = await fetch(`${API_BASE_URL}/teams`);
  return handleResponse(response);
}

export async function fetchTeamSeasons() {
  const response = await fetch(`${API_BASE_URL}/team-seasons`);
  return handleResponse(response);
}

export async function predictMatchup(payload) {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function fetchExplanation(predictionId) {
  const response = await fetch(`${API_BASE_URL}/predict/${predictionId}/explanation`);
  return handleResponse(response);
}
