const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function submitReport(rawText, channel = "whatsapp") {
  const res = await fetch(`${API_BASE}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, channel }),
  });
  if (!res.ok) throw new Error(`Report failed: ${res.status}`);
  return res.json();
}
