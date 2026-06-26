import { useEffect, useState } from "react";
import { fetchImpact } from "../api.js";
import { useEvents, debounce } from "../useEvents.js";

const rupees = (n) => "₹" + Number(n).toLocaleString("en-IN");
function crores(n) {
  const cr = n / 1e7;
  if (cr >= 1000) return `₹${(cr / 1000).toFixed(2)} lakh cr`;
  if (cr >= 1) return `₹${cr.toFixed(2)} cr`;
  return rupees(n);
}

export default function Impact() {
  const [d, setD] = useState(null);
  const [err, setErr] = useState(null);

  const load = () => fetchImpact().then(setD).catch(() => setErr("Cannot reach /impact"));
  useEffect(() => { load(); }, []);
  const live = useEvents(debounce(load, 500));

  if (err) return <div className="h-full flex items-center justify-center bg-slate-950 text-slate-400">{err}</div>;
  if (!d) return <div className="h-full flex items-center justify-center bg-slate-950 text-slate-400">Loading impact…</div>;

  return (
    <div className="h-full overflow-y-auto bg-slate-950 text-slate-200">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">
          Business Impact {live && <span className="text-emerald-400 normal-case tracking-normal">● live</span>}
        </div>
        <h1 className="mt-1 text-3xl md:text-4xl font-extrabold text-white">Every flagged scam is money not lost.</h1>

        <div className="mt-8 grid md:grid-cols-3 gap-4">
          <Big v={crores(d.money_at_risk_saved)} l="Money at risk intercepted" c="text-emerald-400" big />
          <Big v={d.victims_protected} l="Victims protected" c="text-cyan-400" big />
          <Big v={`~${d.avg_response_seconds}s`} l="Avg time to verdict" c="text-amber-400" big />
        </div>

        <div className="mt-4 grid md:grid-cols-3 gap-4">
          <Big v={d.high_risk_intercepted} l="High-risk cases caught" c="text-red-400" />
          <Big v={d.alerts_generated} l="Alerts generated" c="text-rose-400" />
          <Big v={crores(d.national_annual_projection)} l="Projected national savings / yr" c="text-emerald-300" />
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="text-sm font-bold text-slate-300">Why this matters</div>
          <p className="mt-2 text-sm text-slate-400">
            ₹1,776 crore was lost to these scams in nine months because the citizen's warning and the
            investigator's map were never connected. This platform closes that loop — every report
            both protects a person <i>and</i> grows the intelligence that dismantles the network.
          </p>
          <p className="mt-3 text-xs text-slate-500">{d.disclaimer}</p>
        </div>
      </div>
    </div>
  );
}

function Big({ v, l, c, big }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className={`${big ? "text-4xl" : "text-3xl"} font-extrabold ${c}`}>{v}</div>
      <div className="text-xs text-slate-400 mt-1">{l}</div>
    </div>
  );
}
