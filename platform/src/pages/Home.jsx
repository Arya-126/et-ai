import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHealth, fetchRings, fetchGraph } from "../api.js";

export default function Home() {
  const [stats, setStats] = useState({ reports: null, rings: null, backend: "…", llm: null });

  useEffect(() => {
    (async () => {
      try {
        const [h, rings, graph] = await Promise.all([fetchHealth(), fetchRings(), fetchGraph()]);
        setStats({
          reports: graph.nodes.filter((n) => n.label === "Report").length,
          rings: rings.length,
          backend: h.graph_backend?.replace("Store", "") ?? "—",
          llm: h.llm_up,
        });
      } catch {
        setStats((s) => ({ ...s, backend: "offline" }));
      }
    })();
  }, []);

  return (
    <div className="h-full overflow-y-auto bg-slate-950 text-slate-200">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="inline-flex items-center gap-2 text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">
          <span className="w-2 h-2 rounded-full bg-cyan-400" /> Digital Public Safety Platform
        </div>

        <h1 className="mt-4 text-4xl md:text-5xl font-extrabold text-white leading-tight">
          A scared citizen's message becomes the data that{" "}
          <span className="text-cyan-400">maps a criminal fraud network</span> — in real time.
        </h1>
        <p className="mt-5 text-lg text-slate-400 max-w-3xl">
          One closed loop between two tools: the <b className="text-slate-200">Citizen Fraud Shield</b> protects
          people instantly, and every report it receives feeds the{" "}
          <b className="text-slate-200">Fraud Network Graph Intelligence</b> that helps law enforcement
          dismantle the ring behind it.
        </p>

        {/* live stats */}
        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-3">
          <Stat n={stats.reports ?? "…"} l="Reports in graph" c="text-white" />
          <Stat n={stats.rings ?? "…"} l="Fraud rings detected" c="text-cyan-400" />
          <Stat n={stats.backend} l="Graph engine" c="text-emerald-400" />
          <Stat n={stats.llm == null ? "…" : stats.llm ? "LLM" : "rules"} l="Classifier" c="text-amber-400" />
        </div>

        {/* all five components */}
        <div className="mt-10 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card to="/shield" accent="border-emerald-500/40" tag="CITIZEN · 12 LANGUAGES"
                tagColor="text-emerald-400" title="Citizen Fraud Shield"
                body="Instant scam verdicts over WhatsApp & IVR with red flags, advice and guided 1930 / NCRB reporting in 12 regional languages."
                cta="Open the chat →" />
          <Card to="/shield" accent="border-rose-500/40" tag="DETECTION + ALERTING"
                tagColor="text-rose-400" title="Digital Arrest Detection"
                body="Flags active digital-arrest sessions before money moves — spoofing signatures, video-call signals — and auto-generates MHA/I4C + telecom alerts."
                cta="Try a scam message →" />
          <Card to="/currency" accent="border-amber-500/40" tag="COMPUTER VISION"
                tagColor="text-amber-400" title="Counterfeit Currency Agent"
                body="A CNN + OpenCV feature checks identify fake notes by microprint, security thread, UV patch and serial print — on mobile, POS or bank machines."
                cta="Scan a note →" />
          <Card to="/command" accent="border-red-500/40" tag="LAW ENFORCEMENT"
                tagColor="text-red-400" title="Fraud Network Graph"
                body="Reports form a live graph. Louvain lights up rings across jurisdictions, PageRank flags the mule account, and a court-ready package exports."
                cta="Open the dashboard →" />
          <Card to="/map" accent="border-cyan-500/40" tag="GEOSPATIAL"
                tagColor="text-cyan-400" title="Crime Pattern Map"
                body="Complaint hotspots, counterfeit seizures and patrol-priority ranking on a command-centre map for inter-district intelligence sharing."
                cta="Open the map →" />
          <Card to="/command" accent="border-indigo-500/40" tag="THE LOOP"
                tagColor="text-indigo-400" title="One connected platform"
                body="Every citizen report feeds the graph, the map and the alerts in real time — five components, one closed loop, one URL."
                cta="See it connect →" />
        </div>

        {/* the loop */}
        <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="text-sm font-bold text-slate-300 mb-4">The closed loop</div>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            {["Citizen pastes a scam", "Instant verdict + advice", "Report joins the graph",
              "Louvain finds the ring", "PageRank flags the kingpin", "Court-ready PDF"].map((s, i, a) => (
              <span key={i} className="flex items-center gap-3">
                <span className="rounded-lg bg-slate-800 px-3 py-2 text-slate-200">{s}</span>
                {i < a.length - 1 && <span className="text-cyan-500">→</span>}
              </span>
            ))}
          </div>
          <p className="mt-4 text-xs text-slate-500">
            Demonstration uses a disclosed synthetic dataset with planted rings; the detection is real.
          </p>
        </div>
      </div>
    </div>
  );
}

function Stat({ n, l, c }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className={`text-3xl font-extrabold ${c}`}>{n}</div>
      <div className="text-xs text-slate-400 mt-1">{l}</div>
    </div>
  );
}

function Card({ to, accent, tag, tagColor, title, body, cta }) {
  return (
    <Link to={to} className={`block rounded-2xl border ${accent} bg-slate-900/60 p-6 hover:bg-slate-900 transition`}>
      <div className={`text-xs font-bold tracking-wider ${tagColor}`}>{tag}</div>
      <div className="mt-1 text-2xl font-bold text-white">{title}</div>
      <p className="mt-3 text-sm text-slate-400">{body}</p>
      <div className="mt-4 text-cyan-400 font-semibold text-sm">{cta}</div>
    </Link>
  );
}
