import { useEffect, useRef, useState } from "react";
import { fetchGraph, fetchRings, fetchPackage, fetchAlerts, alertPdfUrl, fetchBlocklist } from "../api.js";
import ForceGraph from "../components/graph/ForceGraph.jsx";
import RingPanel from "../components/graph/RingPanel.jsx";
import KingpinCard from "../components/graph/KingpinCard.jsx";

export default function Command() {
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [rings, setRings] = useState([]);
  const [detected, setDetected] = useState(false);
  const [selectedRing, setSelectedRing] = useState(null);
  const [pkg, setPkg] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [blocklist, setBlocklist] = useState([]);
  const [err, setErr] = useState(null);
  const stageRef = useRef(null);
  const [dims, setDims] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const ro = new ResizeObserver(([e]) =>
      setDims({ width: e.contentRect.width, height: e.contentRect.height })
    );
    if (stageRef.current) ro.observe(stageRef.current);
    return () => ro.disconnect();
  }, []);

  async function loadGraph() {
    try {
      setGraph(await fetchGraph());
      setAlerts(await fetchAlerts());
      setBlocklist(await fetchBlocklist());
      setErr(null);
    } catch (e) {
      setErr("Cannot reach backend on :8000 — is uvicorn running?");
    }
  }

  useEffect(() => { loadGraph(); }, []);

  async function detectRings() {
    try {
      setRings(await fetchRings());
      setDetected(true);
    } catch (e) {
      setErr("Ring detection failed.");
    }
  }

  async function selectRing(ringId) {
    setSelectedRing(ringId);
    setPkg(null);
    try {
      setPkg(await fetchPackage(ringId));
    } catch (e) {
      setErr(`Package for ${ringId} failed.`);
    }
  }

  const reportCount = graph.nodes.filter((n) => n.label === "Report").length;

  return (
    <div className="h-full flex text-slate-200">
      <aside className="w-80 shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h1 className="text-lg font-bold text-white">Command Dashboard</h1>
          <p className="text-xs text-slate-400">Fraud Network Intelligence</p>
        </div>

        <div className="p-4 grid grid-cols-2 gap-2 text-center">
          <Stat label="Reports" value={reportCount} />
          <Stat label="Rings" value={detected ? rings.length : "—"} />
        </div>

        <div className="px-4 flex gap-2">
          <button
            onClick={detectRings}
            className="flex-1 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold py-2"
          >
            🔍 Detect Rings
          </button>
          <button
            onClick={loadGraph}
            title="Refresh graph (after new reports)"
            className="rounded-lg bg-slate-700 hover:bg-slate-600 px-3 py-2"
          >
            ⟳
          </button>
        </div>

        <div className="p-4 overflow-y-auto flex-1 space-y-4">
          <RingPanel rings={rings} detected={detected} selectedRing={selectedRing} onSelect={selectRing} />
          <KingpinCard pkg={pkg} />

          {alerts.length > 0 && (
            <div className="rounded-xl border border-red-500/30 bg-slate-900 p-3">
              <div className="text-xs uppercase tracking-wider text-red-300/80 mb-2">
                🚨 Live alerts ({alerts.length})
              </div>
              <div className="space-y-2 max-h-56 overflow-y-auto">
                {alerts.map((a) => (
                  <a key={a.alert_id} href={alertPdfUrl(a.alert_id)} target="_blank" rel="noreferrer"
                     className="block rounded-lg bg-slate-800 hover:bg-slate-700 px-3 py-2">
                    <div className="flex justify-between text-xs">
                      <span className={a.kind === "MHA" ? "text-red-300 font-semibold" : "text-amber-300 font-semibold"}>{a.kind}</span>
                      <span className="text-slate-500">{a.district || "—"}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5 truncate">{a.target}</div>
                  </a>
                ))}
              </div>
            </div>
          )}

          {blocklist.length > 0 && (
            <div className="rounded-xl border border-amber-500/30 bg-slate-900 p-3">
              <div className="text-xs uppercase tracking-wider text-amber-300/80 mb-2">
                🚫 Known scammer numbers ({blocklist.length})
              </div>
              <div className="space-y-1 max-h-56 overflow-y-auto">
                {blocklist.map((b) => (
                  <div key={b.phone} className="flex justify-between text-xs bg-slate-800 rounded px-2 py-1.5">
                    <span className="text-slate-200">{b.phone}</span>
                    <span className="text-slate-400">
                      {b.report_count} reports{b.in_ring ? " · ring" : ""}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {err && <div className="p-3 text-xs text-red-300 bg-red-950/40 border-t border-red-900">{err}</div>}
      </aside>

      <main ref={stageRef} className="flex-1 relative">
        <div className="absolute top-3 left-3 z-10 text-xs text-slate-400 bg-slate-900/70 rounded px-2 py-1">
          {detected ? "Louvain communities + PageRank kingpins" : "Live report graph — click Detect Rings"}
        </div>
        <ForceGraph
          graph={graph}
          detected={detected}
          selectedRing={selectedRing}
          width={dims.width}
          height={dims.height}
        />
      </main>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-800 py-2">
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
}
