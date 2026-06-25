import { NavLink, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Shield from "./pages/Shield.jsx";
import Command from "./pages/Command.jsx";

const NAV = [
  { to: "/", label: "Home", end: true },
  { to: "/shield", label: "Citizen Shield" },
  { to: "/command", label: "Command Dashboard" },
];

export default function App() {
  return (
    <div className="h-full flex flex-col bg-slate-950">
      <header className="shrink-0 h-12 flex items-center gap-4 px-4 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-2 text-white font-bold">
          <span className="text-cyan-400">🛡️</span> Fraud Shield
          <span className="text-slate-500 font-normal text-xs hidden sm:inline">· Digital Public Safety</span>
        </div>
        <nav className="flex items-center gap-1 ml-2">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  isActive ? "bg-cyan-500 text-slate-900" : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <div className="flex-1 min-h-0">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/shield" element={<Shield />} />
          <Route path="/command" element={<Command />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}
