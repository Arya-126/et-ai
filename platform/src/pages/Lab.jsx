import { useState } from "react";
import { zkpVerify, sipSamples, sipAnalyze, honeypotEngage, honeypotSinkhole, livenessDemo, federatedRun } from "../api.js";

const card = "rounded-2xl glass p-5";
const btn = "rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold px-4 py-2 text-sm disabled:opacity-50";
const btn2 = "rounded-lg glass-strong text-white font-bold px-4 py-2 text-sm hover:border-cyan-400/40 disabled:opacity-50";

export default function Lab() {
  return (
    <div className="h-full overflow-y-auto text-slate-200">
      <div className="max-w-5xl mx-auto px-6 py-12 space-y-5">
        <div>
          <div className="text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">Advanced Defense Lab</div>
          <h1 className="font-display mt-2 text-3xl md:text-4xl font-extrabold text-white">Research-grade countermeasures.</h1>
          <p className="mt-2 text-sm text-slate-400 max-w-3xl">
            Real algorithms — Schnorr zero-knowledge proofs, federated averaging, rPPG liveness,
            SIP/DPI forensics, an LLM scam-baiting agent. Live data sources (VoIP capture, camera,
            multi-org PII, PKI) are simulated and disclosed; the maths is real.
          </p>
        </div>
        <Zkp /><Sip /><Honeypot /><Liveness /><Federated />
      </div>
    </div>
  );
}

function Verdict({ ok, good, bad }) {
  return <span className={`font-bold ${ok ? "text-emerald-400" : "text-red-400"}`}>{ok ? good : bad}</span>;
}

function Zkp() {
  const [r, setR] = useState(null); const [busy, setBusy] = useState(false);
  const go = async (imp) => { setBusy(true); try { setR(await zkpVerify(imp)); } finally { setBusy(false); } };
  return (
    <div className={card}>
      <H n="1" t="Zero-Knowledge officer verification" s="Defeats fake-government-portal impersonation cryptographically (Schnorr / Fiat-Shamir)." />
      <div className="flex gap-2 mt-3">
        <button className={btn} disabled={busy} onClick={() => go(false)}>Genuine officer</button>
        <button className={btn2} disabled={busy} onClick={() => go(true)}>Impersonator</button>
      </div>
      {r && (
        <div className="mt-3 text-sm">
          <div>{r.claimant} → <Verdict ok={r.verified} good="✓ VERIFIED" bad="✗ REJECTED" /></div>
          <div className="text-slate-400 mt-1 text-xs">{r.explanation}</div>
          <div className="text-slate-500 mt-1 text-[11px] font-mono break-all">proof t={String(r.proof.t).slice(0, 28)}… s={String(r.proof.s).slice(0, 20)}…</div>
        </div>
      )}
    </div>
  );
}

function Sip() {
  const [r, setR] = useState(null); const [busy, setBusy] = useState(false);
  const go = async (key) => {
    setBusy(true);
    try { const s = await sipSamples(); setR(await sipAnalyze(s[key].sip, s[key].meta)); }
    finally { setBusy(false); }
  };
  const color = { "ILLICIT GATEWAY": "text-red-400", SUSPICIOUS: "text-amber-400", CLEAN: "text-emerald-400" };
  return (
    <div className={card}>
      <H n="2" t="SIP / network telephony forensics" s="Inspects VoIP SIP headers + DPI metadata for spoofed routing and offshore fraud-compound origins." />
      <div className="flex gap-2 mt-3">
        <button className={btn2} disabled={busy} onClick={() => go("fraud_compound")}>Fraud-compound call</button>
        <button className={btn2} disabled={busy} onClick={() => go("legit_carrier")}>Legit carrier call</button>
      </div>
      {r && (
        <div className="mt-3 text-sm">
          <div>Verdict: <b className={color[r.verdict]}>{r.verdict}</b> · network-risk {r.network_risk}</div>
          <ul className="mt-1 space-y-0.5 text-xs text-slate-400">{r.findings.map((f, i) => <li key={i}>• {f}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

function Honeypot() {
  const [msg, setMsg] = useState("Madam, transfer 50000 to refund.cbi@okaxis and confirm OTP, account 50100234567890.");
  const [r, setR] = useState(null); const [sink, setSink] = useState(null); const [busy, setBusy] = useState(false);
  const engage = async () => { setBusy(true); try { setSink(null); setR(await honeypotEngage([], msg)); } finally { setBusy(false); } };
  const doSink = async () => { if (r?.extracted_iocs) setSink(await honeypotSinkhole(r.extracted_iocs)); };
  return (
    <div className={card}>
      <H n="3" t="Agentic scam-baiting honeypot + sinkholing" s="An LLM agent stalls the scammer, extracts payment IoCs, then burns the infrastructure (simulated telecom/bank push)." />
      <textarea value={msg} onChange={(e) => setMsg(e.target.value)} rows={2}
        className="mt-3 w-full rounded-lg bg-slate-900/70 border border-slate-700 p-2 text-sm text-slate-200" />
      <button className={btn} disabled={busy} onClick={engage}>Engage honeypot</button>
      {r && (
        <div className="mt-3 text-sm space-y-2">
          <div className="rounded-lg bg-slate-900/70 p-2 text-slate-200 text-sm">🎙️ “{r.reply}”</div>
          <div className="text-xs text-slate-400">⏱ time wasted: {r.time_wasted_seconds}s · IoCs extracted: {JSON.stringify(r.extracted_iocs)}</div>
          <button className={btn2} onClick={doSink}>Sinkhole these IoCs →</button>
          {sink && <div className="text-xs text-emerald-400">Sinkholed {sink.propagated.length} IoC(s): {sink.propagated.map((p) => `${p.ioc}→${p.propagated_to}`).join("; ")}</div>}
        </div>
      )}
    </div>
  );
}

function Liveness() {
  const [r, setR] = useState(null); const [busy, setBusy] = useState(false);
  const go = async (live) => { setBusy(true); try { setR(await livenessDemo(live)); } finally { setBusy(false); } };
  return (
    <div className={card}>
      <H n="4" t="rPPG deepfake-liveness rejection" s="Detects a real heartbeat pulse (blood-flow colour change) on the face — absent in deepfake overlays. AV-desync is the wired extension." />
      <div className="flex gap-2 mt-3">
        <button className={btn} disabled={busy} onClick={() => go(true)}>Real human</button>
        <button className={btn2} disabled={busy} onClick={() => go(false)}>Deepfake overlay</button>
      </div>
      {r && (
        <div className="mt-3 text-sm">
          <Verdict ok={r.live} good={`✓ LIVE — pulse detected at ${r.bpm} bpm`} bad="✗ SPOOF / DEEPFAKE — no physiological pulse" />
          <div className="text-xs text-slate-400 mt-1">signal SNR {r.snr} · in-band power {r.in_band_ratio} · {r.source}</div>
        </div>
      )}
    </div>
  );
}

function Federated() {
  const [r, setR] = useState(null); const [busy, setBusy] = useState(false);
  const go = async () => { setBusy(true); try { setR(await federatedRun()); } finally { setBusy(false); } };
  const max = r ? Math.max(...r.history.map((h) => h.global_accuracy)) : 1;
  return (
    <div className={card}>
      <H n="5" t="Privacy-preserving federated learning" s="Banks, telcos & police train one fraud model without sharing raw PII — only model weights move (FedAvg)." />
      <button className={btn} disabled={busy} onClick={go}>Run a federated round</button>
      {r && (
        <div className="mt-3 text-sm">
          <div className="text-xs text-slate-400 mb-2">Nodes: {r.nodes.join(" · ")} — raw bytes shared: <b className="text-emerald-400">{r.bytes_of_raw_data_shared}</b></div>
          <div className="flex items-end gap-1 h-24">
            {r.history.map((h) => (
              <div key={h.round} className="flex-1 flex flex-col items-center justify-end" title={`round ${h.round}: ${h.global_accuracy}`}>
                <div className="w-full rounded-t bg-gradient-to-t from-cyan-500 to-indigo-400" style={{ height: `${(h.global_accuracy / max) * 100}%` }} />
              </div>
            ))}
          </div>
          <div className="text-xs text-slate-400 mt-2">Global accuracy {r.history[0].global_accuracy} → <b className="text-white">{r.final_accuracy}</b> over {r.rounds} rounds. {r.privacy_note}</div>
        </div>
      )}
    </div>
  );
}

function H({ n, t, s }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-7 h-7 rounded-lg glass-strong flex items-center justify-center text-cyan-400 font-bold shrink-0">{n}</div>
      <div>
        <div className="font-bold text-white">{t}</div>
        <div className="text-xs text-slate-400">{s}</div>
      </div>
    </div>
  );
}
