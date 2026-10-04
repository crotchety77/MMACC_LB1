import type { AnalyzeResponse, ExamplesResponse } from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error('API is unavailable');
  return res.json();
}

export async function fetchExamples(): Promise<ExamplesResponse> {
  const res = await fetch(`${API_BASE}/api/example`);
  if (!res.ok) throw new Error('Failed to load examples');
  return res.json();
}

export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown analysis error' }));
    throw new Error(err.detail || 'Analysis request failed');
  }
  return res.json();
}

export async function analyzeRankings(rankings: string[][]): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rankings }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown analysis error' }));
    throw new Error(err.detail || 'Analysis request failed');
  }
  return res.json();
}

export async function analyzeFile(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/analyze/file`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown file upload error' }));
    throw new Error(err.detail || 'File upload failed');
  }
  return res.json();
}
