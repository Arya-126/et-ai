import RiskBadge from "./RiskBadge.jsx";

export default function Verdict({ report }) {
  const high = report.verdict === "HIGH RISK";
  return (
    <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-white shadow-md p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-2">
        <RiskBadge verdict={report.verdict} confidence={report.confidence} />
        <span className="text-xs text-gray-400">Fraud Shield</span>
      </div>

      {report.scam_type && report.verdict !== "LIKELY SAFE" && (
        <div className="text-sm font-semibold text-gray-800 mb-1">{report.scam_type}</div>
      )}

      {report.red_flags?.length > 0 && (
        <ul className="mt-2 space-y-1">
          {report.red_flags.map((f, i) => (
            <li key={i} className="text-sm text-gray-700 flex gap-2">
              <span className="text-red-500">•</span>
              <span>{f}</span>
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
        <a
          href="tel:1930"
          className="mt-3 inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-white text-sm font-bold hover:bg-red-700"
        >
          📞 Report now — call 1930
        </a>
      )}
    </div>
  );
}
