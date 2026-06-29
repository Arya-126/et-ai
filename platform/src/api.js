// Relative URLs: same-origin when served by FastAPI (prod), Vite-proxied in dev.

export async function submitReport(rawText, channel = "whatsapp", language = "en") {
  const res = await fetch(`/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, channel, language }),
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

// --- alerts (Component 1) ---
export async function fetchAlerts() {
  const res = await fetch(`/alerts`);
  if (!res.ok) throw new Error(`alerts ${res.status}`);
  return res.json();
}
export function alertPdfUrl(id) {
  return `/alerts/${id}/pdf`;
}

// --- languages + complaint (Component 5) ---
export async function fetchLanguages() {
  const res = await fetch(`/languages`);
  if (!res.ok) throw new Error(`languages ${res.status}`);
  return res.json();
}
export async function downloadComplaint(report) {
  const res = await fetch(`/report/complaint`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  if (!res.ok) throw new Error(`complaint ${res.status}`);
  const blob = await res.blob();
  window.open(URL.createObjectURL(blob), "_blank");
}

// --- currency (Component 2) ---
export async function fetchSamples() {
  const res = await fetch(`/currency/samples`);
  if (!res.ok) throw new Error(`samples ${res.status}`);
  return res.json();
}
export async function scanCurrency(blob, filename = "note.png", district = null) {
  const fd = new FormData();
  fd.append("file", blob, filename);
  if (district) fd.append("district", district);
  const res = await fetch(`/currency/scan`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`scan ${res.status}`);
  return res.json();
}

// --- geo (Component 4) ---
export async function fetchGeo() {
  const res = await fetch(`/geo`);
  if (!res.ok) throw new Error(`geo ${res.status}`);
  return res.json();
}

// --- call guard ---
export async function screenCall(callerNumber, transcript, isSaved = false, language = "en") {
  const res = await fetch(`/call/screen`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ caller_number: callerNumber, transcript, is_saved: isSaved, language }),
  });
  if (!res.ok) throw new Error(`screen ${res.status}`);
  return res.json();
}
export async function fetchBlocklist() {
  const res = await fetch(`/call/blocklist`);
  if (!res.ok) throw new Error(`blocklist ${res.status}`);
  return res.json();
}

// --- analytics ---
export async function fetchAnalytics() {
  const res = await fetch(`/analytics/summary`);
  if (!res.ok) throw new Error(`analytics ${res.status}`);
  return res.json();
}

// --- advanced defense lab ---
async function _post(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`${path} ${res.status}`);
  return res.json();
}
async function _get(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} ${res.status}`);
  return res.json();
}
export const zkpVerify = (impersonator) => _post("/advanced/zkp/verify-officer", { impersonator });
export const sipSamples = () => _get("/advanced/sip/samples");
export const sipAnalyze = (sip_text, packet_meta) => _post("/advanced/sip", { sip_text, packet_meta });
export const honeypotEngage = (history, message) => _post("/advanced/honeypot/engage", { history, message });
export const honeypotSinkhole = (iocs) => _post("/advanced/honeypot/sinkhole", { iocs });
export const livenessDemo = (live) => _get(`/advanced/liveness/demo?live=${live}`);
export const federatedRun = () => _get("/advanced/federated");

// --- impact / ROI ---
export async function fetchImpact() {
  const res = await fetch(`/impact/summary`);
  if (!res.ok) throw new Error(`impact ${res.status}`);
  return res.json();
}

// --- screenshot OCR intake ---
export async function ocrReport(blob, filename = "screenshot.png", language = "en") {
  const fd = new FormData();
  fd.append("file", blob, filename);
  fd.append("language", language);
  const res = await fetch(`/report/ocr`, { method: "POST", body: fd });
  if (res.status === 503) throw new Error("OCR_UNAVAILABLE");
  if (!res.ok) throw new Error(`ocr ${res.status}`);
  return res.json();
}
