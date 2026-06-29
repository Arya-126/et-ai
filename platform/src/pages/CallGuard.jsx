import { useEffect, useState } from "react";
import { screenCall, fetchBlocklist } from "../api.js";
import RiskBadge from "../components/chat/RiskBadge.jsx";

const BASE_SAMPLES = [
  { key: "ransom", label: "👨‍👦 Ransom", number: "+918882213007", saved: false,
    transcript: "Listen carefully, we have your son. He had an accident and is with us. If you call the police he is finished. Transfer 50000 to rescue.now@okaxis right now and do not disconnect." },
  { key: "otp", label: "🏦 OTP / UPI", number: "+919004551234", saved: false,
    transcript: "Sir I am calling from your bank. To reverse a wrong debit, approve the request on your UPI app and read me the 6-digit OTP to confirm the refund." },
  { key: "sextortion", label: "📷 Sextortion", number: "+917715559090", saved: false,
    transcript: "I recorded our video call and morphed your photos. Pay 20000 to me@ybl in one hour or I send them to your whole family and post them online." },
  { key: "loan", label: "💸 Loan-app", number: "+918001234567", saved: false,
    transcript: "This is recovery for the loan app. Your EMI is overdue. Pay today or we send your morphed photo to everyone in your contacts." },
  { key: "mom", label: "💚 Mom (saved)", number: "+919812345678", saved: true,
    transcript: "Beta, dinner is ready, when are you coming home?" },
];

export default function CallGuard() {
  const [samples, setSamples] = useState(BASE_SAMPLES);
  const [call, setCall] = useState(BASE_SAMPLES[0]);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  // pull a real known-scammer number from the graph for the "known number" demo
  useEffect(() => {
    fetchBlocklist().then((bl) => {
      if (bl?.length) {
        const known = {
          key: "known", label: "🚩 Known scammer", number: bl[0].phone, saved: false,
          transcript: "Hello sir, good morning. Just a normal courtesy call from our side.",
        };
        setSamples([known, ...BASE_SAMPLES]);
      }
    }).catch(() => {});
  }, []);

  function pick(s) { setCall(s); setResult(null); }

  async function screen() {
    setBusy(true);
    try {
      setResult(await screenCall(call.number, call.transcript, call.saved));
    } catch {
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  const rep = result?.reputation;
  const report = result?.report;

  return (
    <div className="h-full overflow-y-auto text-slate-200">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="fade-up text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase">Call Guard</div>
        <h1 className="fade-up font-display mt-2 text-3xl md:text-4xl font-extrabold text-white" style={{ animationDelay: "60ms" }}>Screen calls from unsaved numbers</h1>
        <p className="fade-up mt-2 text-slate-400 max-w-2xl text-sm" style={{ animationDelay: "100ms" }}>
          On-device AI checks an incoming call's transcript and the caller's number against the
          national fraud graph — a known scammer number is flagged before a word is spoken.
        </p>

        <div className="mt-7 grid md:grid-cols-2 gap-6 fade-up" style={{ animationDelay: "140ms" }}>
          {/* incoming call card */}
          <div className="rounded-3xl glass-strong p-6 text-center">
            <div className="text-xs text-slate-400 uppercase tracking-wider">Incoming call</div>
            <div className="mt-4 w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-3xl pulse-ring">
              {call.saved ? "👤" : "❓"}
            </div>
            <div className="mt-3 text-2xl font-bold text-white">{call.number}</div>
            <div className={`mt-1 inline-block text-xs px-2 py-0.5 rounded-full ${call.saved ? "bg-emerald-900 text-emerald-300" : "bg-amber-900 text-amber-300"}`}>
              {call.saved ? "In your contacts" : "Unsaved number"}
            </div>
            <div className="mt-4 text-sm text-slate-300 italic bg-slate-800/60 rounded-lg p-3 text-left min-h-[4.5rem]">
              “{call.transcript}”
            </div>
            <div className="mt-5 flex gap-3 justify-center">
              <button onClick={screen} disabled={busy}
                      className="btn-glow rounded-full font-bold px-6 py-2.5 disabled:opacity-50">
                {busy ? "Screening…" : "🛡️ Screen with AI"}
              </button>
            </div>
          </div>

          {/* verdict */}
          <div className="rounded-3xl glass p-6">
            {!result ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-sm text-center">
                Tap <span className="text-cyan-300 font-semibold mx-1">Screen with AI</span> to analyse this call.
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between">
                  <RiskBadge verdict={report.verdict} confidence={report.confidence} />
                  <span className="text-xs text-slate-400">{report.scam_type}</span>
                </div>

                {/* number reputation */}
                <div className={`mt-4 rounded-lg p-3 text-sm ${rep.known ? "bg-red-950/50 border border-red-500/40 text-red-200" : "bg-slate-800 text-slate-300"}`}>
                  {rep.known ? (
                    <>🚩 <b>Known scammer number</b> — linked to {rep.report_count} prior report(s)
                      {rep.in_ring && rep.ring_id ? <> · inside fraud ring <b>{rep.ring_id}</b></> : null}.</>
                  ) : (
                    <>🆕 New number — not seen in the fraud graph yet.</>
                  )}
                </div>

                {report.red_flags?.length > 0 && (
                  <ul className="mt-3 space-y-1">
                    {report.red_flags.slice(0, 5).map((f, i) => (
                      <li key={i} className="text-sm text-slate-300 flex gap-2"><span className="text-red-400">•</span><span>{f}</span></li>
                    ))}
                  </ul>
                )}

                {report.advice && <p className="mt-3 text-sm text-slate-400 border-t border-slate-800 pt-2">{report.advice}</p>}

                {report.verdict === "HIGH RISK" && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    <a href="tel:1930" className="rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-bold px-4 py-2">📞 Block & report 1930</a>
                    {report.alert && <span className="rounded-lg bg-slate-800 text-slate-300 text-xs px-3 py-2">🚨 Family + authorities alerted</span>}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* sample call chooser */}
        <div className="mt-6">
          <div className="text-xs text-slate-500 mb-2">Try an incoming call:</div>
          <div className="flex flex-wrap gap-2">
            {samples.map((s) => (
              <button key={s.key} onClick={() => pick(s)}
                      className={`text-sm rounded-full px-3 py-1.5 border ${call.key === s.key ? "border-cyan-400 bg-slate-800 text-white" : "border-slate-700 bg-slate-900 text-slate-300 hover:bg-slate-800"}`}>
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
