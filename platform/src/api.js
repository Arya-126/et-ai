// Relative URLs: same-origin when served by FastAPI (prod), and Vite proxies
// these paths to :8000 in dev. So no API base / CORS needed in the unified flow.

export async function submitReport(rawText, channel = "whatsapp") {
  const res = await fetch(`/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, channel }),
  });
  if (!res.ok) throw new Error(`Report failed: ${res.status}`);
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`/health`);
  if (!res.ok) throw new Error(`health ${res.status}`);
  return res.json();
}

export async function fetchGraph() {
  const res = await fetch(`/graph`);
  if (!res.ok) throw new Error(`graph ${res.status}`);
  return res.json();
}

export async function fetchRings() {
  const res = await fetch(`/rings`);
  if (!res.ok) throw new Error(`rings ${res.status}`);
  return res.json();
}

export async function fetchPackage(ringId) {
  const res = await fetch(`/package/${ringId}`);
  if (!res.ok) throw new Error(`package ${res.status}`);
  return res.json();
}

export function packagePdfUrl(ringId) {
  return `/package/${ringId}/pdf`;
}
