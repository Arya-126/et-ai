import { useEffect, useState } from "react";
import { fetchSamples, scanCurrency } from "../api.js";

const VERDICT_STYLE = {
  GENUINE: { bg: "bg-emerald-600", text: "GENUINE", icon: "✅" },
  COUNTERFEIT: { bg: "bg-red-600", text: "COUNTERFEIT", icon: "🚫" },
  UNCERTAIN: { bg: "bg-amber-500", text: "UNCERTAIN", icon: "⚠️" },
};

export default function Currency() {
  const [samples, setSamples] = useState([]);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => { fetchSamples().then(setSamples).catch(() => setErr("Backend offline")); }, []);

  async function scanBlob(blob, previewUrl) {
    setBusy(true); setResult(null); setPreview(previewUrl); setErr(null);
    try {
      setResult(await scanCurrency(blob));
    } catch {
      setErr("Scan failed");
    } finally {
      setBusy(false);
    }
  }

  async function scanSample(s) {
    const blob = await (await fetch(s.url)).blob();
    scanBlob(blob, s.url);
  }

  function onUpload(e) {
    const f = e.target.files?.[0];
    if (f) scanBlob(f, URL.createObjectURL(f));
  }

  const vs = result ? VERDICT_STYLE[result.verdict] : null;

  return (
    <div className="h-full overflow-y-auto text-slate-200">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="fade-up text-cyan-400 text-xs font-bold tracking-widest uppercase">Counterfeit Currency Agent</div>
        <h1 className="fade-up font-display mt-2 text-3xl md:text-4xl font-extrabold text-white" style={{ animationDelay: "60ms" }}>Scan a note for authenticity</h1>
        <p className="fade-up mt-2 text-slate-400 text-sm max-w-2xl" style={{ animationDelay: "100ms" }}>
          A CNN checks the note and OpenCV explains each security feature — microprint, security thread,
          UV patch, serial print. Same endpoint deploys on mobile cameras, POS terminals and bank counting machines.
        </p>

        <div className="mt-7 grid md:grid-cols-2 gap-6 fade-up" style={{ animationDelay: "140ms" }}>
          {/* left: pick / upload */}
          <div>
            <div className="text-sm font-semibold text-slate-300 mb-2">Demo samples (synthetic)</div>
            <div className="grid grid-cols-2 gap-3">
              {samples.map((s) => (
                <button key={s.id} onClick={() => scanSample(s)}
                        className="rounded-lg overflow-hidden border border-slate-700 hover:border-cyan-400 bg-slate-900 text-left">
                  <img src={s.url} alt={s.id} className="w-full h-20 object-cover" />
                  <div className="px-2 py-1 text-xs flex justify-between">
                    <span className="text-slate-300">{s.denomination}</span>
                    <span className={s.expected === "COUNTERFEIT" ? "text-red-400" : "text-emerald-400"}>{s.expected}</span>
                  </div>
                </button>
              ))}
            </div>
            <label className="mt-4 block">
              <span className="text-sm font-semibold text-slate-300">Or upload an image</span>
              <input type="file" accept="image/*" onChange={onUpload}
                     className="mt-1 block w-full text-xs text-slate-400 file:mr-3 file:rounded file:border-0 file:bg-cyan-500 file:px-3 file:py-1.5 file:text-slate-900 file:font-bold" />
            </label>
            {err && <div className="mt-3 text-xs text-red-300">{err}</div>}
          </div>

          {/* right: result */}
          <div className="rounded-2xl glass p-5 min-h-[18rem]">
            {preview && <img src={preview} alt="scanned" className="w-full h-28 object-cover rounded mb-3 border border-slate-700" />}
            {busy && <div className="text-slate-400 text-sm">Analysing…</div>}
            {!busy && !result && <div className="text-slate-500 text-sm">Pick a sample or upload a note to scan.</div>}
            {result && vs && (
              <>
                <div className="flex items-center gap-3">
                  <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-white text-sm font-bold ${vs.bg}`}>
                    {vs.icon} {vs.text}
                  </span>
                  <span className="text-slate-400 text-sm">{result.denomination} · {Math.round(result.confidence * 100)}% · {result.model}</span>
                </div>
                <div className="mt-4 space-y-2">
                  {result.features.map((f, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-xs">
                        <span className={f.passed ? "text-slate-200" : "text-red-300"}>
                          {f.passed ? "✓" : "✗"} {f.name} <span className="text-slate-500">({f.detail})</span>
                        </span>
                        <span className="text-slate-400">{Math.round(f.score * 100)}%</span>
                      </div>
                      <div className="h-1.5 rounded bg-slate-800 mt-1">
                        <div className={`h-1.5 rounded ${f.passed ? "bg-emerald-500" : "bg-red-500"}`} style={{ width: `${Math.round(f.score * 100)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
        <p className="mt-6 text-xs text-slate-500">
          Demonstration uses a disclosed synthetic note dataset; the CNN and feature checks are real.
        </p>
      </div>
    </div>
  );
}
