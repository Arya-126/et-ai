import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHealth, fetchRings, fetchGraph } from "../api.js";
import AnimatedNumber from "../components/ui/AnimatedNumber.jsx";

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
    <div className="h-full overflow-y-auto text-slate-200">
      <div className="max-w-6xl mx-auto px-6 py-14">
        {/* hero */}
        <div className="fade-up inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-cyan-300 text-[11px] font-bold tracking-[0.2em] uppercase">
          <span className="w-2 h-2 rounded-full bg-cyan-400 pulse-ring" /> Digital Public Safety Platform
        </div>

        <h1 className="fade-up font-display mt-5 text-4xl md:text-6xl font-extrabold text-white leading-[1.05]" style={{ animationDelay: "60ms" }}>
          A scared citizen's message becomes the data that{" "}
          <span className="gradient-text">maps a criminal fraud network</span> — in real time.
        </h1>
        <p className="fade-up mt-6 text-lg text-slate-400 max-w-3xl leading-relaxed" style={{ animationDelay: "120ms" }}>
          One closed loop between two tools: the <b className="text-slate-200">Citizen Fraud Shield</b> protects
          people instantly, and every report it receives feeds the{" "}
          <b className="text-slate-200">Fraud Network Graph Intelligence</b> that helps law enforcement
          dismantle the ring behind it.
        </p>

        <div className="fade-up mt-8 flex flex-wrap gap-3" style={{ animationDelay: "160ms" }}>
          <Link to="/shield" className="btn-glow rounded-xl font-bold px-5 py-3 text-sm">Protect a citizen →</Link>
          <Link to="/command" className="rounded-xl font-bold px-5 py-3 text-sm glass text-white hover:border-cyan-400/40 card-hover">Open command dashboard</Link>
        </div>

        {/* live stats */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-3 stagger">
          <Stat n={stats.reports} l="Reports in graph" c="text-white" i={0} />
          <Stat n={stats.rings} l="Fraud rings detected" c="gradient-text" i={1} />
          <Stat n={stats.backend} l="Graph engine" c="text-emerald-400" i={2} />
          <Stat n={stats.llm == null ? "…" : stats.llm ? "LLM" : "rules"} l="Classifier" c="text-amber-400" i={3} />
        </div>

        {/* all five components */}
        <div className="mt-12 grid md:grid-cols-2 lg:grid-cols-3 gap-4 stagger">
          <Card to="/shield" i={0} icon="🛡️" glow="from-emerald-500/20" tag="CITIZEN · 12 LANGUAGES"
                tagColor="text-emerald-400" title="Citizen Fraud Shield"
                body="Instant scam verdicts over WhatsApp & IVR with red flags, advice and guided 1930 / NCRB reporting in 12 regional languages."
                cta="Open the chat" />
          <Card to="/shield" i={1} icon="🚓" glow="from-rose-500/20" tag="DETECTION + ALERTING"
                tagColor="text-rose-400" title="Digital Arrest Detection"
                body="Flags active digital-arrest sessions before money moves — spoofing signatures, video-call signals — and auto-generates MHA/I4C + telecom alerts."
                cta="Try a scam message" />
          <Card to="/currency" i={2} icon="💵" glow="from-amber-500/20" tag="COMPUTER VISION"
                tagColor="text-amber-400" title="Counterfeit Currency Agent"
                body="A CNN + OpenCV feature checks identify fake notes by microprint, security thread, UV patch and serial print — on mobile, POS or bank machines."
                cta="Scan a note" />
          <Card to="/command" i={3} icon="🕸️" glow="from-red-500/20" tag="LAW ENFORCEMENT"
                tagColor="text-red-400" title="Fraud Network Graph"
                body="Reports form a live graph. Louvain lights up rings across jurisdictions, PageRank flags the mule account, and a court-ready package exports."
                cta="Open the dashboard" />
          <Card to="/map" i={4} icon="🗺️" glow="from-cyan-500/20" tag="GEOSPATIAL"
                tagColor="text-cyan-400" title="Crime Pattern Map"
                body="Complaint hotspots, counterfeit seizures and patrol-priority ranking on a command-centre map for inter-district intelligence sharing."
                cta="Open the map" />
          <Card to="/command" i={5} icon="🔁" glow="from-indigo-500/20" tag="THE LOOP"
                tagColor="text-indigo-400" title="One connected platform"
                body="Every citizen report feeds the graph, the map and the alerts in real time — five components, one closed loop, one URL."
                cta="See it connect" />
        </div>

        {/* the loop */}
        <div className="fade-up mt-12 rounded-3xl glass p-7">
          <div className="text-sm font-bold text-slate-200 mb-5 flex items-center gap-2">
            <span className="w-1.5 h-4 rounded-full bg-gradient-to-b from-cyan-400 to-indigo-500" /> The closed loop
          </div>
          <div className="flex flex-wrap items-center gap-2.5 text-sm">
            {["Citizen pastes a scam", "Instant verdict + advice", "Report joins the graph",
              "Louvain finds the ring", "PageRank flags the kingpin", "Court-ready PDF"].map((s, i, a) => (
              <span key={i} className="flex items-center gap-2.5">
                <span className="rounded-xl glass-strong px-3.5 py-2.5 text-slate-100 font-medium border border-white/5 hover:border-cyan-400/40 transition">
                  <span className="text-cyan-400 font-bold mr-1.5">{i + 1}</span>{s}
                </span>
                {i < a.length - 1 && <span className="text-cyan-500 text-lg">→</span>}
              </span>
            ))}
          </div>
          <p className="mt-5 text-xs text-slate-500">
            Demonstration uses a disclosed synthetic dataset with planted rings; the detection is real.
          </p>
        </div>
      </div>
    </div>
  );
}

function Stat({ n, l, c, i }) {
  const display = n == null ? "…" : n;
  return (
    <div className="accent-top rounded-2xl glass card-hover p-5" style={{ "--i": i }}>
      <div className={`text-3xl md:text-4xl font-extrabold font-display ${c}`}>
        {typeof display === "number" ? <AnimatedNumber value={display} /> : display}
      </div>
      <div className="text-xs text-slate-400 mt-1.5">{l}</div>
    </div>
  );
}

function Card({ to, icon, glow, tag, tagColor, title, body, cta, i }) {
  return (
    <Link to={to} className="group relative block rounded-2xl glass card-hover p-6 overflow-hidden" style={{ "--i": i }}>
      <div className={`absolute -top-16 -right-16 w-40 h-40 rounded-full bg-gradient-to-br ${glow} to-transparent blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      <div className="relative">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl glass-strong flex items-center justify-center text-xl shrink-0">{icon}</div>
          <div className={`text-[11px] font-bold tracking-wider ${tagColor}`}>{tag}</div>
        </div>
        <div className="mt-4 text-xl font-bold text-white font-display">{title}</div>
        <p className="mt-2.5 text-sm text-slate-400 leading-relaxed">{body}</p>
        <div className="mt-4 text-cyan-400 font-semibold text-sm inline-flex items-center gap-1">
          {cta} <span className="transition-transform group-hover:translate-x-1">→</span>
        </div>
      </div>
    </Link>
  );
}
