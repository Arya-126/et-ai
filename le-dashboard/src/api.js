const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export const apiBase = API_BASE;

export async function fetchGraph() {
  const res = await fetch(`${API_BASE}/graph`);
  if (!res.ok) throw new Error(`graph ${res.status}`);
  return res.json();
}

export async function fetchRings() {
  const res = await fetch(`${API_BASE}/rings`);
  if (!res.ok) throw new Error(`rings ${res.status}`);
  return res.json();
}

export async function fetchPackage(ringId) {
  const res = await fetch(`${API_BASE}/package/${ringId}`);
  if (!res.ok) throw new Error(`package ${res.status}`);
  return res.json();
}

export function packagePdfUrl(ringId) {
  return `${API_BASE}/package/${ringId}/pdf`;
}
