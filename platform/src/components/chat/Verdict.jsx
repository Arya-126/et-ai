import RiskBadge from "./RiskBadge.jsx";
import { verdictLabel, ui } from "../../i18n.js";
import { downloadComplaint } from "../../api.js";

export default function Verdict({ report, lang = "en" }) {
  const high = report.verdict === "HIGH RISK";
  return (
    <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-white shadow-md p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-2">
        <RiskBadge verdict={report.verdict} confidence={report.confidence}
                   label={verdictLabel(report.verdict, lang)} />
        <span className="text-xs text-gray-400">Fraud Shield</span>
      </div>

      {report.scam_type && report.verdict !== "LIKELY SAFE" && (
        <div className="text-sm font-semibold text-gray-800 mb-1">{report.scam_type}</div>
      )}

      {/* Component 1: automated alert banner */}
      {report.alert && (
        <div className="my-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
          🚨 <b>Stop — do not transfer money.</b> Automated alert generated:
          {" "}MHA/I4C escalation{report.phone ? " · telecom flag on caller number" : ""}.
        </div>
      )}

      {report.red_flags?.length > 0 && (
        <ul className="mt-2 space-y-1">
          {report.red_flags.map((f, i) => (
            <li key={i} className="text-sm text-gray-700 flex gap-2">
              <span className="text-red-500">•</span><span>{f}</span>
            </li>
          ))}
        </ul>
      )}

      {report.advice && (
        <p className="mt-3 text-sm text-gray-600 leading-relaxed border-t border-gray-100 pt-2">
          {report.advice}
        </p>
      )}

      {high && (
        <div className="mt-3 flex flex-wrap gap-2">
          <a href="tel:1930"
             className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-white text-sm font-bold hover:bg-red-700">
            📞 {ui("report_cta", lang)}
          </a>
          <button onClick={() => downloadComplaint(report)}
                  className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2 text-white text-sm font-bold hover:bg-slate-900">
            📄 {ui("file_complaint", lang)}
          </button>
        </div>
      )}
    </div>
  );
}
