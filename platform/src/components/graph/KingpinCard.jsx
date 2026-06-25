import { packagePdfUrl } from "../../api.js";

export default function KingpinCard({ pkg }) {
  if (!pkg) return null;
  const { ring, centrality } = pkg;
  return (
    <div className="rounded-xl border border-red-500/40 bg-gradient-to-b from-red-950/40 to-slate-900 p-4">
      <div className="text-xs uppercase tracking-wider text-red-300/80">Arrest priority #1</div>
      {ring.top_node ? (
        <>
          <div className="mt-1 text-lg font-bold text-red-200 break-all">★ {ring.top_node.value}</div>
          <div className="text-xs text-slate-400">
            {ring.top_node.label} · PageRank {ring.top_node.score}
          </div>
        </>
      ) : (
        <div className="text-slate-300">No dominant node.</div>
      )}

      <div className="mt-3 text-sm text-slate-300">
        Ties <span className="font-bold text-white">{ring.report_count}</span> victim reports across{" "}
        <span className="font-bold text-white">{ring.districts.length}</span> districts into one operation.
      </div>

      {centrality?.length > 0 && (
        <div className="mt-3">
          <div className="text-xs text-slate-400 mb-1">Top infrastructure (PageRank)</div>
          <ul className="space-y-1">
            {centrality.slice(0, 5).map((n, i) => (
              <li key={i} className="flex justify-between text-xs text-slate-300">
                <span className="break-all mr-2">{n.value} <span className="text-slate-500">({n.label})</span></span>
                <span className="text-cyan-300">{n.score}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <a
        href={packagePdfUrl(ring.ring_id)}
        target="_blank"
        rel="noreferrer"
        className="mt-4 block text-center rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold py-2"
      >
        📄 Generate Intelligence Package (PDF)
      </a>
    </div>
  );
}
