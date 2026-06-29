import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitReport, screenCall } from "./api.js";

const LAKSHMI =
  "This is Inspector Sharma from CBI. Your Aadhaar is linked to a money laundering case. " +
  "You are under digital arrest — stay on this video call and do not disconnect or tell anyone. " +
  "Transfer a refundable security deposit to digitalarrest.a@okaxis to clear your name.";
const RANSOM =
  "Listen carefully, we have your son. He had an accident. Do not call the police. " +
  "Transfer 50000 to rescue.now@okaxis right now and do not disconnect.";

// each step: where to go, what to say, how long to hold, and an optional backend action
const STEPS = [
  { path: "/", cap: "Meet Lakshmi, a retired teacher in Bengaluru.", ms: 3200 },
  { path: "/shield", cap: "A caller claiming to be CBI says she's under ‘digital arrest’. She pastes it to Fraud Shield…", ms: 1200, act: () => submitReport(LAKSHMI, "whatsapp") },
  { path: "/shield", cap: "Instant verdict: HIGH RISK — and her report silently joins the national fraud graph.", ms: 4200 },
  { path: "/call", cap: "Minutes later an unknown number calls about her ‘son in an accident’…", ms: 1200, act: () => screenCall("+918882213007", RANSOM, false) },
  { path: "/call", cap: "Call Guard flags it HIGH RISK and alerts her family — before any money moves.", ms: 4200 },
  { path: "/command?auto=1", cap: "On the command graph, Louvain lights up the ring; PageRank names the mule account.", ms: 6500 },
  { path: "/map", cap: "The crime map shows hotspots and patrol priorities across districts.", ms: 4500 },
  { path: "/analytics", cap: "Analytics tracks every scam type and trend in real time…", ms: 4200 },
  { path: "/impact", cap: "…and the impact: crores in fraud intercepted. We built the loop that wasn't there.", ms: 6500 },
];

export default function DemoController() {
  const navigate = useNavigate();
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(null);
  const cancel = useRef(false);

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function run() {
    setRunning(true);
    cancel.current = false;
    for (let i = 0; i < STEPS.length; i++) {
      if (cancel.current) break;
      const s = STEPS[i];
      navigate(s.path);
      setStep({ i, cap: s.cap });
      if (s.act) { try { await s.act(); } catch { /* keep the demo flowing */ } }
      await sleep(s.ms);
    }
    setRunning(false);
    setStep(null);
  }

  function stop() { cancel.current = true; setRunning(false); setStep(null); }

  return (
    <>
      {!running && (
        <button onClick={run}
          className="btn-glow pulse-ring fixed bottom-5 right-5 z-50 rounded-full font-bold px-6 py-3.5 inline-flex items-center gap-2">
          <span className="text-base">▶</span> Run guided demo
        </button>
      )}
      {running && step && (
        <div className="fixed bottom-0 left-0 right-0 z-50 glass-strong border-t border-cyan-500/40 px-6 py-4 slide-in-right">
          <div className="max-w-5xl mx-auto flex items-center gap-4">
            <div className="shrink-0 inline-flex items-center gap-2 rounded-full bg-cyan-400/15 border border-cyan-400/30 px-3 py-1 text-cyan-300 font-bold text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" /> DEMO {step.i + 1}/{STEPS.length}
            </div>
            <div className="flex-1 text-slate-100 text-base font-medium">{step.cap}</div>
            <button onClick={stop} className="text-slate-400 hover:text-white text-sm shrink-0">✕ Stop</button>
          </div>
          <div className="max-w-5xl mx-auto mt-2.5 h-1.5 bg-slate-800/80 rounded-full overflow-hidden">
            <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${((step.i + 1) / STEPS.length) * 100}%`, background: "linear-gradient(90deg,#22d3ee,#818cf8)" }} />
          </div>
        </div>
      )}
    </>
  );
}
