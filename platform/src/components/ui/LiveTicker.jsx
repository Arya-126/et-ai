import { useRef, useState } from "react";
import { useEvents } from "../../useEvents.js";

// Global live-activity toasts. Subscribes once to the backend SSE stream and
// surfaces each new report / call / alert as a transient card — top-right,
// clear of the demo controls at the bottom.

const VERDICT = {
  "HIGH RISK": { dot: "bg-red-500", text: "text-red-300", ring: "border-red-500/40" },
  SUSPICIOUS: { dot: "bg-amber-400", text: "text-amber-300", ring: "border-amber-400/40" },
  "LIKELY SAFE": { dot: "bg-emerald-400", text: "text-emerald-300", ring: "border-emerald-400/40" },
};

function describe(e) {
  if (e.type === "report")
    return { icon: "🛡️", title: "New citizen report", sub: `${e.scam_type || "analysed"}${e.district ? " · " + e.district : ""}`, verdict: e.verdict };
  if (e.type === "call")
    return { icon: "📞", title: e.known ? "Known scammer called" : "Call screened", sub: e.caller || e.scam_type || "", verdict: e.verdict };
  if (e.type === "alert")
    return { icon: "🚨", title: `${e.kind} alert dispatched`, sub: e.district || "authorities notified", verdict: "HIGH RISK" };
  return null;
}

export default function LiveTicker() {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  useEvents((e) => {
    const d = describe(e);
    if (!d) return;
    const id = ++idRef.current;
    setToasts((t) => [{ id, ...d }, ...t].slice(0, 4));
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 5200);
  });

  if (!toasts.length) return null;

  return (
    <div className="fixed top-16 right-4 z-50 flex flex-col gap-2 w-[19rem] pointer-events-none">
      {toasts.map((t) => {
        const v = VERDICT[t.verdict] || VERDICT.SUSPICIOUS;
        return (
          <div key={t.id}
               className={`slide-in-right glass-strong rounded-xl border ${v.ring} px-3 py-2.5 shadow-xl shadow-black/40 pointer-events-auto`}>
            <div className="flex items-center gap-2.5">
              <span className="text-lg leading-none">{t.icon}</span>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-semibold text-white truncate">{t.title}</div>
                <div className="text-xs text-slate-400 truncate">{t.sub}</div>
              </div>
              <span className={`flex items-center gap-1.5 text-[10px] font-bold ${v.text}`}>
                <span className={`w-2 h-2 rounded-full ${v.dot} animate-pulse`} />
                {t.verdict}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
