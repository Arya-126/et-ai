import { communityColor } from "../../colors.js";

export default function RingPanel({ rings, detected, selectedRing, onSelect }) {
  if (!detected) {
    return (
      <p className="text-slate-400 text-sm">
        Click <span className="text-cyan-300 font-semibold">Detect Rings</span> to run
        Louvain community detection over the live report graph.
      </p>
    );
  }
  if (!rings.length) return <p className="text-slate-400 text-sm">No rings detected.</p>;

  return (
    <div className="space-y-2">
      {rings.map((r) => {
        const active = r.ring_id === selectedRing;
        return (
          <button
            key={r.ring_id}
            onClick={() => onSelect(r.ring_id)}
            className={`w-full text-left rounded-lg p-3 border transition ${
              active ? "border-cyan-400 bg-slate-800" : "border-slate-700 bg-slate-900 hover:bg-slate-800"
            }`}
          >
            <div className="flex items-center gap-2">
              <span
                className="inline-block w-3 h-3 rounded-full"
                style={{ background: communityColor(r.community, true) }}
              />
              <span className="font-semibold text-slate-100">{r.ring_id}</span>
              <span className="ml-auto text-xs text-slate-400">{r.report_count} reports</span>
            </div>
            <div className="mt-1 text-xs text-slate-400">
              {r.districts.length} districts: {r.districts.join(", ") || "—"}
            </div>
            {r.top_node && (
              <div className="mt-1 text-xs text-red-300">★ kingpin: {r.top_node.value}</div>
            )}
          </button>
        );
      })}
    </div>
  );
}
