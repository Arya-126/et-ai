import { useEffect, useState } from "react";
import { fetchImpact } from "../api.js";
import { useEvents, debounce } from "../useEvents.js";
import AnimatedNumber from "../components/ui/AnimatedNumber.jsx";

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

  const load = () => fetchImpact().then((x) => { setD(x); setErr(null); }).catch(() => setErr("Cannot reach /impact"));
  useEffect(() => { load(); }, []);
  const live = useEvents(debounce(load, 500));

  if (err) return <div className="h-full flex items-center justify-center text-slate-400">{err}</div>;
  if (!d) return <div className="h-full flex items-center justify-center text-slate-400">Loading impact…</div>;

  return (
    <div className="h-full overflow-y-auto text-slate-200">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="fade-up flex items-center gap-2 text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">
          Business Impact {live && <span className="inline-flex items-center gap-1 text-emerald-400 normal-case tracking-normal"><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />live</span>}
        </div>
        <h1 className="fade-up font-display mt-2 text-3xl md:text-5xl font-extrabold text-white leading-tight" style={{ animationDelay: "60ms" }}>
          Every flagged scam is <span className="gradient-text">money not lost.</span>
        </h1>

        <div className="mt-9 grid md:grid-cols-3 gap-4 stagger">
          <Big v={d.money_at_risk_saved} fmt={crores} l="Money at risk intercepted" c="text-emerald-400" big i={0} />
          <Big v={d.victims_protected} l="Victims protected" c="gradient-text" big i={1} />
          <Big v={d.avg_response_seconds} fmt={(n) => `~${Math.round(n)}s`} l="Avg time to verdict" c="text-amber-400" big i={2} />
        </div>

        <div className="mt-4 grid md:grid-cols-3 gap-4 stagger">
          <Big v={d.high_risk_intercepted} l="High-risk cases caught" c="text-red-400" i={3} />
          <Big v={d.alerts_generated} l="Alerts generated" c="text-rose-400" i={4} />
          <Big v={d.national_annual_projection} fmt={crores} l="Projected national savings / yr" c="text-emerald-300" i={5} />
        </div>

        <div className="fade-up mt-9 rounded-3xl glass p-6">
          <div className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <span className="w-1.5 h-4 rounded-full bg-gradient-to-b from-cyan-400 to-indigo-500" /> Why this matters
          </div>
          <p className="mt-3 text-sm text-slate-300 leading-relaxed">
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

function Big({ v, fmt, l, c, big, i }) {
  return (
    <div className="accent-top rounded-2xl glass card-hover p-5" style={{ "--i": i }}>
      <div className={`${big ? "text-3xl md:text-4xl" : "text-2xl md:text-3xl"} font-extrabold font-display ${c}`}>
        <AnimatedNumber value={v} format={fmt} duration={1100} />
      </div>
      <div className="text-xs text-slate-400 mt-1.5">{l}</div>
    </div>
  );
}
