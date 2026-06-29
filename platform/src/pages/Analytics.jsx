import { useEffect, useState } from "react";
import { fetchAnalytics } from "../api.js";
import { useEvents, debounce } from "../useEvents.js";
import AnimatedNumber from "../components/ui/AnimatedNumber.jsx";

const VERDICT_COLOR = { "HIGH RISK": "#ef4444", SUSPICIOUS: "#f59e0b", "LIKELY SAFE": "#34d399" };

export default function Analytics() {
  const [a, setA] = useState(null);
  const [err, setErr] = useState(null);

  const load = () => fetchAnalytics().then((d) => { setA(d); setErr(null); }).catch(() => setErr("Cannot reach /analytics"));
  useEffect(() => { load(); }, []);
  const live = useEvents(debounce(load, 500));

  if (err) return <Center>{err}</Center>;
  if (!a) return <Center>Loading analytics…</Center>;

  return (
    <div className="h-full overflow-y-auto text-slate-200">
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="fade-up flex items-center gap-2 text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">
          Command Centre
          {live && <span className="inline-flex items-center gap-1 text-emerald-400 normal-case tracking-normal"><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />live</span>}
        </div>
        <h1 className="fade-up font-display mt-2 text-3xl md:text-4xl font-extrabold text-white" style={{ animationDelay: "60ms" }}>Fraud analytics &amp; trends</h1>

        <div className="mt-7 grid grid-cols-2 md:grid-cols-4 gap-3 stagger">
          <Kpi n={a.total_reports} l="Total reports" c="text-white" i={0} />
          <Kpi n={a.verdicts.find((v) => v.label === "HIGH RISK")?.count ?? 0} l="High-risk" c="text-red-400" i={1} />
          <Kpi n={a.alerts.total} l="Alerts generated" c="text-amber-400" i={2} />
          <Kpi n={a.scam_types.length} l="Scam types seen" c="gradient-text" i={3} />
        </div>

        <div className="mt-6 grid md:grid-cols-2 gap-5 stagger">
          <Panel title="Scam types" i={0}><Bars data={a.scam_types} /></Panel>
          <Panel title="Verdicts" i={1}><Bars data={a.verdicts} colorFor={(d) => VERDICT_COLOR[d.label] || "#22d3ee"} /></Panel>
          <Panel title="Channels" i={2}><Bars data={a.channels} /></Panel>
          <Panel title="Languages" i={3}><Bars data={a.languages} /></Panel>
          <Panel title="Top districts" i={4}><Bars data={a.top_districts} /></Panel>
          <Panel title="Alerts by kind" i={5}><Bars data={a.alerts.by_kind} colorFor={() => "#fb7185"} /></Panel>
        </div>

        {a.timeseries?.length > 1 && (
          <Panel title="Reports over time" className="mt-5"><Spark series={a.timeseries} /></Panel>
        )}
      </div>
    </div>
  );
}

function Center({ children }) {
  return <div className="h-full flex items-center justify-center text-slate-400">{children}</div>;
}
function Kpi({ n, l, c, i }) {
  return (
    <div className="accent-top rounded-2xl glass card-hover p-5" style={{ "--i": i }}>
      <div className={`text-3xl md:text-4xl font-extrabold font-display ${c}`}><AnimatedNumber value={n} /></div>
      <div className="text-xs text-slate-400 mt-1.5">{l}</div>
    </div>
  );
}
function Panel({ title, children, className = "", i = 0 }) {
  return (
    <div className={`rounded-2xl glass p-5 ${className}`} style={{ "--i": i }}>
      <div className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
        <span className="w-1.5 h-4 rounded-full bg-gradient-to-b from-cyan-400 to-indigo-500" />{title}
      </div>
      {children}
    </div>
  );
}
function Bars({ data, colorFor }) {
  if (!data?.length) return <div className="text-xs text-slate-500">No data.</div>;
  const max = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="space-y-2.5">
      {data.map((d, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <div className="w-32 shrink-0 text-slate-400 truncate" title={d.label}>{d.label}</div>
          <div className="flex-1 bg-slate-800/70 rounded-full h-3.5 overflow-hidden">
            <div className="h-3.5 rounded-full origin-left"
                 style={{
                   width: `${(d.count / max) * 100}%`,
                   background: `linear-gradient(90deg, ${colorFor ? colorFor(d) : "#22d3ee"}, ${colorFor ? colorFor(d) : "#818cf8"})`,
                   animation: "grow-x .7s cubic-bezier(.22,.61,.36,1) both",
                   animationDelay: `${i * 50}ms`,
                 }} />
          </div>
          <div className="w-8 text-right text-slate-200 font-semibold">{d.count}</div>
        </div>
      ))}
    </div>
  );
}
function Spark({ series }) {
  const max = Math.max(...series.map((s) => s.count), 1);
  const W = 600, H = 90, step = W / Math.max(series.length - 1, 1);
  const pts = series.map((s, i) => `${i * step},${H - (s.count / max) * (H - 12) - 6}`);
  const line = pts.join(" ");
  const area = `0,${H} ${line} ${W},${H}`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-24">
      <defs>
        <linearGradient id="sparkfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="sparkline" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#22d3ee" />
          <stop offset="100%" stopColor="#818cf8" />
        </linearGradient>
      </defs>
      <polygon points={area} fill="url(#sparkfill)" />
      <polyline points={line} fill="none" stroke="url(#sparkline)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {series.map((s, i) => (
        <circle key={i} cx={i * step} cy={H - (s.count / max) * (H - 12) - 6} r="3" fill="#0b1220" stroke="#22d3ee" strokeWidth="2" />
      ))}
    </svg>
  );
}
