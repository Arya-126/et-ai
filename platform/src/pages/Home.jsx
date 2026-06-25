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

        {/* the two tools */}
        <div className="mt-10 grid md:grid-cols-2 gap-4">
          <Card
            to="/shield"
            accent="border-emerald-500/40"
            tag="CITIZEN SIDE"
            tagColor="text-emerald-400"
            title="Citizen Fraud Shield"
            body="Paste a suspicious call, SMS or message and get an instant verdict — HIGH RISK, SUSPICIOUS or LIKELY SAFE — with red flags, advice and a one-tap report to 1930."
            cta="Open the chat →"
          />
          <Card
            to="/command"
            accent="border-red-500/40"
            tag="LAW ENFORCEMENT SIDE"
            tagColor="text-red-400"
            title="Command Dashboard"
            body="Watch reports form a live fraud graph. Run Louvain to light up rings across districts, and PageRank to flag the central mule account — then export a court-ready intelligence package."
            cta="Open the dashboard →"
          />
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
