/**
 * CityTrack AI - Backend API Client
 * Clean HTTP client for vehicle Re-ID endpoints and corridor telemetry.
 */

const BASE_URL = '/api';

export async function fetchStatus() {
  const res = await fetch(`${BASE_URL}/status`);
  if (!res.ok) throw new Error(`Status check failed: HTTP ${res.status}`);
  return await res.json();
}

export async function fetchDemoCorridor() {
  const res = await fetch(`${BASE_URL}/dataset/demo`);
  if (!res.ok) throw new Error(`Failed to load corridor data: HTTP ${res.status}`);
  return await res.json();
}

export async function reviewMatch(matchId, action, notes = '') {
  const res = await fetch(`${BASE_URL}/matches/${encodeURIComponent(matchId)}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, notes })
  });
  if (!res.ok) throw new Error(`Match review update failed: HTTP ${res.status}`);
  return await res.json();
}

export async function updateCorridorConfig(params) {
  const res = await fetch(`${BASE_URL}/corridor/configure`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error(`Corridor configuration failed: HTTP ${res.status}`);
  return await res.json();
}

export async function uploadSurveillancePair(fileA, fileB) {
  const formData = new FormData();
  formData.append('camera_a', fileA);
  formData.append('camera_b', fileB);

  const res = await fetch(`${BASE_URL}/analyze/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Upload analysis failed: HTTP ${res.status}`);
  }
  return await res.json();
}

export async function fetchMethodology() {
  const res = await fetch(`${BASE_URL}/methodology`);
  if (!res.ok) throw new Error(`Failed to load methodology: HTTP ${res.status}`);
  return await res.json();
}

export async function fetchModelArchitecture() {
  const res = await fetch(`${BASE_URL}/model/architecture`);
  if (!res.ok) throw new Error(`Failed to load model architecture: HTTP ${res.status}`);
  return await res.json();
}

export async function fetchModelEmbeddings() {
  const res = await fetch(`${BASE_URL}/model/embeddings`);
  if (!res.ok) throw new Error(`Failed to load model embeddings: HTTP ${res.status}`);
  return await res.json();
}

export async function probeReidQuery(probeId) {
  const res = await fetch(`${BASE_URL}/model/probe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ probe_id: probeId })
  });
  if (!res.ok) throw new Error(`Probe query failed: HTTP ${res.status}`);
  return await res.json();
}

export async function randomizeCorridorDataset() {
  const res = await fetch(`${BASE_URL}/dataset/randomize`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to generate random traffic: HTTP ${res.status}`);
  return await res.json();
}

export async function fetchTrafficOdMatrix() {
  const res = await fetch(`${BASE_URL}/traffic/od-matrix`);
  if (!res.ok) throw new Error(`Failed to load OD matrix: HTTP ${res.status}`);
  return await res.json();
}
