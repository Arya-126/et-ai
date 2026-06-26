import { useEffect, useState } from "react";
import { fetchAnalytics } from "../api.js";
import { useEvents, debounce } from "../useEvents.js";

const VERDICT_COLOR = { "HIGH RISK": "#ef4444", SUSPICIOUS: "#f59e0b", "LIKELY SAFE": "#34d399" };

export default function Analytics() {
  const [a, setA] = useState(null);
  const [err, setErr] = useState(null);

  const load = () => fetchAnalytics().then(setA).catch(() => setErr("Cannot reach /analytics"));
  useEffect(() => { load(); }, []);
  useEvents(debounce(load, 500));

  if (err) return <Center>{err}</Center>;
  if (!a) return <Center>Loading analytics…</Center>;

  return (
    <div className="h-full overflow-y-auto bg-slate-950 text-slate-200">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">Command Centre</div>
        <h1 className="mt-1 text-3xl font-extrabold text-white">Fraud analytics & trends</h1>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
          <Kpi n={a.total_reports} l="Total reports" c="text-white" />
          <Kpi n={a.verdicts.find((v) => v.label === "HIGH RISK")?.count ?? 0} l="High-risk" c="text-red-400" />
          <Kpi n={a.alerts.total} l="Alerts generated" c="text-amber-400" />
          <Kpi n={a.scam_types.length} l="Scam types seen" c="text-cyan-400" />
        </div>

        <div className="mt-6 grid md:grid-cols-2 gap-5">
          <Panel title="Scam types"><Bars data={a.scam_types} /></Panel>
          <Panel title="Verdicts"><Bars data={a.verdicts} colorFor={(d) => VERDICT_COLOR[d.label] || "#22d3ee"} /></Panel>
          <Panel title="Channels"><Bars data={a.channels} /></Panel>
          <Panel title="Languages"><Bars data={a.languages} /></Panel>
          <Panel title="Top districts"><Bars data={a.top_districts} /></Panel>
          <Panel title="Alerts by kind"><Bars data={a.alerts.by_kind} colorFor={() => "#fb7185"} /></Panel>
        </div>

        {a.timeseries?.length > 1 && (
          <Panel title="Reports over time" className="mt-5">
            <Spark series={a.timeseries} />
          </Panel>
        )}
      </div>
    </div>
  );
}

function Center({ children }) {
  return <div className="h-full flex items-center justify-center bg-slate-950 text-slate-400">{children}</div>;
}
function Kpi({ n, l, c }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className={`text-3xl font-extrabold ${c}`}>{n}</div>
      <div className="text-xs text-slate-400 mt-1">{l}</div>
    </div>
  );
}
function Panel({ title, children, className = "" }) {
  return (
    <div className={`rounded-2xl border border-slate-800 bg-slate-900/60 p-5 ${className}`}>
      <div className="text-sm font-bold text-slate-300 mb-3">{title}</div>
      {children}
    </div>
  );
}
function Bars({ data, colorFor }) {
  if (!data?.length) return <div className="text-xs text-slate-500">No data.</div>;
  const max = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="space-y-2">
      {data.map((d, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <div className="w-32 shrink-0 text-slate-400 truncate" title={d.label}>{d.label}</div>
          <div className="flex-1 bg-slate-800 rounded h-4 overflow-hidden">
            <div className="h-4 rounded" style={{ width: `${(d.count / max) * 100}%`, background: colorFor ? colorFor(d) : "#22d3ee" }} />
          </div>
          <div className="w-8 text-right text-slate-300">{d.count}</div>
        </div>
      ))}
    </div>
  );
}
function Spark({ series }) {
  const max = Math.max(...series.map((s) => s.count), 1);
  const W = 600, H = 80, step = W / Math.max(series.length - 1, 1);
  const pts = series.map((s, i) => `${i * step},${H - (s.count / max) * (H - 8) - 4}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-20">
      <polyline points={pts} fill="none" stroke="#22d3ee" strokeWidth="2" />
      {series.map((s, i) => (
        <circle key={i} cx={i * step} cy={H - (s.count / max) * (H - 8) - 4} r="2.5" fill="#22d3ee" />
      ))}
    </svg>
  );
}
