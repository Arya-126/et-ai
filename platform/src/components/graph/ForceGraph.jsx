import { useMemo, useRef, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { communityColor, KINGPIN } from "../../colors.js";

export default function ForceGraph({ graph, detected, selectedRing, onPick, width, height }) {
  const fgRef = useRef();

  const data = useMemo(() => {
    const selComm = selectedRing ? Number(String(selectedRing).split("-").pop()) : null;
    return {
      nodes: graph.nodes.map((n) => ({
        ...n,
        _dim: detected && selComm !== null && n.community !== selComm,
      })),
      links: graph.edges.map((e) => ({ source: e.source, target: e.target, type: e.type })),
    };
  }, [graph, detected, selectedRing]);

  useEffect(() => {
    const t = setTimeout(() => fgRef.current?.zoomToFit(600, 60), 400);
    return () => clearTimeout(t);
  }, [graph]);

  // When a ring is selected, fly to just that ring's nodes.
  useEffect(() => {
    if (!selectedRing) return;
    const comm = Number(String(selectedRing).split("-").pop());
    const t = setTimeout(
      () => fgRef.current?.zoomToFit(800, 80, (n) => n.community === comm),
      300
    );
    return () => clearTimeout(t);
  }, [selectedRing]);

  return (
    <ForceGraph2D
      ref={fgRef}
      graphData={data}
      width={width}
      height={height}
      backgroundColor="#0b1220"
      cooldownTicks={120}
      linkColor={() => "rgba(148,163,184,0.18)"}
      linkWidth={0.6}
      nodeRelSize={4}
      nodeVal={(n) => (n.is_kingpin ? Math.max(n.size, 8) : n.size)}
      nodeLabel={(n) => `${n.label}: ${n.value}`}
      onNodeClick={(n) => onPick?.(n)}
      nodeCanvasObjectMode={(n) => (n.is_kingpin ? "after" : undefined)}
      nodeColor={(n) => {
        if (n.is_kingpin && detected) return KINGPIN;
        const c = communityColor(n.community, detected);
        return n._dim ? "#1f2937" : c;
      }}
      nodeCanvasObject={(n, ctx, scale) => {
        if (!n.is_kingpin || !detected) return;
        const r = Math.max(n.size, 8) / scale + 3;
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, 2 * Math.PI);
        ctx.strokeStyle = KINGPIN;
        ctx.lineWidth = 2 / scale;
        ctx.stroke();
        const label = `★ ${n.value}`;
        ctx.font = `${12 / scale}px sans-serif`;
        ctx.fillStyle = "#fecaca";
        ctx.textAlign = "center";
        ctx.fillText(label, n.x, n.y - r - 4 / scale);
      }}
    />
  );
}
