import { useEffect, useState } from "react";
import { NavLink, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Shield from "./pages/Shield.jsx";
import Command from "./pages/Command.jsx";
import Currency from "./pages/Currency.jsx";
import CrimeMap from "./pages/CrimeMap.jsx";
import CallGuard from "./pages/CallGuard.jsx";
import Analytics from "./pages/Analytics.jsx";
import Impact from "./pages/Impact.jsx";
import Lab from "./pages/Lab.jsx";
import DemoController from "./DemoController.jsx";
import LiveTicker from "./components/ui/LiveTicker.jsx";
import { fetchHealth } from "./api.js";

const NAV = [
  { to: "/", label: "Home", end: true },
  { to: "/shield", label: "Citizen Shield" },
  { to: "/call", label: "Call Guard" },
  { to: "/currency", label: "Currency Check" },
  { to: "/command", label: "Command Dashboard" },
  { to: "/map", label: "Crime Map" },
  { to: "/analytics", label: "Analytics" },
  { to: "/impact", label: "Impact" },
  { to: "/lab", label: "Defense Lab" },
];

function ShieldLogo() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" className="drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]">
      <defs>
        <linearGradient id="shieldg" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
          <stop stopColor="#67e8f9" />
          <stop offset="0.6" stopColor="#22d3ee" />
          <stop offset="1" stopColor="#6366f1" />
        </linearGradient>
      </defs>
      <path d="M12 2.2 4.5 5v6.2c0 4.6 3.1 8.4 7.5 10.1 4.4-1.7 7.5-5.5 7.5-10.1V5L12 2.2Z"
            fill="url(#shieldg)" opacity="0.96" />
      <path d="M8.4 12.2l2.5 2.5 4.7-4.9" stroke="#042f3a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function StatusDot() {
  const [up, setUp] = useState(null); // null = checking, true/false
  useEffect(() => {
    let alive = true;
    const ping = () => fetchHealth().then(() => alive && setUp(true)).catch(() => alive && setUp(false));
    ping();
    const t = setInterval(ping, 15000);
    return () => { alive = false; clearInterval(t); };
  }, []);
  const color = up == null ? "bg-slate-500" : up ? "bg-emerald-400" : "bg-red-500";
  const label = up == null ? "connecting" : up ? "systems live" : "offline";
  return (
    <span className="hidden md:inline-flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
      <span className="relative flex w-2 h-2">
        {up && <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60 animate-ping" />}
        <span className={`relative inline-flex rounded-full w-2 h-2 ${color}`} />
      </span>
      {label}
    </span>
  );
}

export default function App() {
  return (
    <div className="h-full flex flex-col relative z-10">
      <header className="shrink-0 h-14 flex items-center gap-4 px-4 glass-strong border-b border-white/10 sticky top-0 z-40">
        <div className="flex items-center gap-2.5 shrink-0">
          <ShieldLogo />
          <div className="leading-none">
            <span className="font-display font-extrabold text-white text-[15px] tracking-tight">Fraud<span className="gradient-text">Shield</span></span>
            <span className="block text-[10px] text-slate-500 font-medium tracking-wide">DIGITAL PUBLIC SAFETY</span>
          </div>
        </div>

        <nav className="flex items-center gap-1 ml-1 overflow-x-auto no-scrollbar">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                `relative px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition ${
                  isActive
                    ? "text-slate-900 bg-cyan-400 shadow-[0_6px_20px_-6px_rgba(34,211,238,0.8)]"
                    : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto shrink-0">
          <StatusDot />
        </div>
      </header>

      <div className="flex-1 min-h-0">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/shield" element={<Shield />} />
          <Route path="/call" element={<CallGuard />} />
          <Route path="/currency" element={<Currency />} />
          <Route path="/command" element={<Command />} />
          <Route path="/map" element={<CrimeMap />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/impact" element={<Impact />} />
          <Route path="/lab" element={<Lab />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      <LiveTicker />
      <DemoController />
    </div>
  );
}
