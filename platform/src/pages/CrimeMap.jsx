import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";
import { fetchGeo } from "../api.js";

// India lat/lng bounds for the offline SVG projection
const BOUNDS = { latMin: 6, latMax: 37.5, lngMin: 67, lngMax: 98 };

function HeatLayer({ points }) {
  const map = useMap();
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) map.removeLayer(ref.current);
    const data = points.map((p) => [p.lat, p.lng, Math.min(1, 0.3 + p.high_risk / 12)]);
    ref.current = L.heatLayer(data, { radius: 28, blur: 22, maxZoom: 8 });
    ref.current.addTo(map);
    return () => { if (ref.current) map.removeLayer(ref.current); };
  }, [points, map]);
  return null;
}

export default function CrimeMap() {
  const [geo, setGeo] = useState({ hotspots: [], seizures: [], patrol_priority: [] });
  const [offline, setOffline] = useState(false);
  const tileErrors = useRef(0);

  useEffect(() => { fetchGeo().then(setGeo).catch(() => setOffline(true)); }, []);

  return (
    <div className="h-full flex text-slate-200">
      <aside className="w-72 shrink-0 glass-strong border-r border-white/10 flex flex-col">
        <div className="p-4 border-b border-white/10">
          <h1 className="font-display text-lg font-bold text-white">Crime Pattern Map</h1>
          <p className="text-xs text-slate-400">Geospatial command centre</p>
        </div>
        <div className="p-4 space-y-3 overflow-y-auto flex-1">
          <div className="text-xs uppercase tracking-wider text-slate-500">Patrol priority</div>
          {geo.patrol_priority.map((p, i) => (
            <div key={p.district} className="rounded-lg bg-slate-800 px-3 py-2">
              <div className="flex justify-between">
                <span className="font-semibold text-slate-100">{i + 1}. {p.district}</span>
                <span className="text-red-300 text-sm">{p.high_risk} HR</span>
              </div>
              <div className="text-xs text-slate-400">{p.state} · {p.count} complaints</div>
            </div>
          ))}
          <div className="pt-2 text-xs text-slate-500 space-y-1">
            <div><span className="inline-block w-2 h-2 rounded-full bg-cyan-400 mr-2" />Complaint hotspot</div>
            <div><span className="inline-block w-2 h-2 rounded-full bg-orange-400 mr-2" />Counterfeit seizure</div>
          </div>
          <button onClick={() => setOffline((o) => !o)}
                  className="mt-2 w-full text-xs rounded-lg bg-slate-700 hover:bg-slate-600 py-1.5">
            {offline ? "Try live map" : "Offline map view"}
          </button>
        </div>
      </aside>

      <main className="flex-1 relative">
        {offline ? (
          <SvgIndia geo={geo} />
        ) : (
          <MapContainer center={[22.5, 80]} zoom={5} style={{ height: "100%", width: "100%", background: "#0b1220" }}>
            <TileLayer
              url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap"
              eventHandlers={{ tileerror: () => { if (++tileErrors.current > 4) setOffline(true); } }}
            />
            <HeatLayer points={geo.hotspots} />
            {geo.hotspots.map((p) => (
              <CircleMarker key={"h" + p.district} center={[p.lat, p.lng]}
                            radius={6 + Math.min(p.count, 24) / 2}
                            pathOptions={{ color: "#22d3ee", fillColor: "#22d3ee", fillOpacity: 0.5 }}>
                <Popup>{p.district}, {p.state}<br />{p.count} complaints · {p.high_risk} high-risk</Popup>
              </CircleMarker>
            ))}
            {geo.seizures.map((p, i) => (
              <CircleMarker key={"s" + i} center={[p.lat, p.lng]} radius={7}
                            pathOptions={{ color: "#fb923c", fillColor: "#fb923c", fillOpacity: 0.8 }}>
                <Popup>Counterfeit seizure · {p.district}</Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        )}
        <div className="absolute top-3 left-3 z-[500] text-xs text-slate-300 bg-slate-900/80 rounded px-2 py-1">
          {offline ? "Offline map mode — coordinates plotted on India" : "Live map · complaint heat + seizures"}
        </div>
      </main>
    </div>
  );
}

function SvgIndia({ geo }) {
  const W = 800, H = 760;
  const proj = (lat, lng) => [
    ((lng - BOUNDS.lngMin) / (BOUNDS.lngMax - BOUNDS.lngMin)) * W,
    ((BOUNDS.latMax - lat) / (BOUNDS.latMax - BOUNDS.latMin)) * H,
  ];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-full" style={{ background: "#0b1220" }}>
      <rect x="40" y="20" width={W - 80} height={H - 40} rx="16" fill="#0f1b30" stroke="#1e293b" />
      <text x={W / 2} y="48" textAnchor="middle" fill="#475569" fontSize="14">India — offline coordinate plot</text>
      {geo.hotspots.map((p) => {
        const [x, y] = proj(p.lat, p.lng);
        return (
          <g key={p.district}>
            <circle cx={x} cy={y} r={6 + Math.min(p.count, 24) / 2} fill="#22d3ee" fillOpacity="0.45" stroke="#22d3ee" />
            <text x={x + 8} y={y + 3} fill="#cbd5e1" fontSize="10">{p.district} ({p.count})</text>
          </g>
        );
      })}
      {geo.seizures.map((p, i) => {
        const [x, y] = proj(p.lat, p.lng);
        return <circle key={i} cx={x} cy={y} r="6" fill="#fb923c" />;
      })}
    </svg>
  );
}
