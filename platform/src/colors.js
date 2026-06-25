// Distinct, high-contrast colors for fraud rings (communities).
const PALETTE = [
  "#22d3ee", "#f472b6", "#a3e635", "#fbbf24", "#818cf8",
  "#fb7185", "#34d399", "#e879f9", "#60a5fa", "#f59e0b",
];

const GREY = "#3b4252";

export function communityColor(community, detected) {
  if (!detected) return GREY;
  if (community === null || community === undefined) return GREY;
  return PALETTE[Math.abs(community) % PALETTE.length];
}

export const KINGPIN = "#ef4444";
export const NEUTRAL = GREY;
