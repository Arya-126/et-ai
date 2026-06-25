const STYLES = {
  "HIGH RISK": { bg: "bg-red-600", ring: "ring-red-300", icon: "🚨", text: "HIGH RISK" },
  SUSPICIOUS: { bg: "bg-amber-500", ring: "ring-amber-200", icon: "⚠️", text: "SUSPICIOUS" },
  "LIKELY SAFE": { bg: "bg-emerald-600", ring: "ring-emerald-200", icon: "✅", text: "LIKELY SAFE" },
};

export default function RiskBadge({ verdict, confidence, label }) {
  const s = STYLES[verdict] || STYLES.SUSPICIOUS;
  return (
    <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-white text-sm font-bold ring-4 ${s.bg} ${s.ring}`}>
      <span>{s.icon}</span>
      <span>{label || s.text}</span>
      {confidence != null && (
        <span className="opacity-80 font-normal">· {Math.round(confidence * 100)}%</span>
      )}
    </div>
  );
}
