// Generates docs/pitch-deck.pptx — dark "command-center" theme matching the dashboard.
// Run: node docs/build-deck.js
const path = require("path");
const PptxGenJS = require(path.join(
  process.env.APPDATA, "npm", "node_modules", "pptxgenjs"
));

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pptx.layout = "WIDE";

// palette
const BG = "0B1220", CARD = "111E36", CARD2 = "16223C";
const TXT = "E2E8F0", MUTED = "94A3B8", WHITE = "FFFFFF";
const CYAN = "22D3EE", RED = "EF4444", GREEN = "34D399", AMBER = "F59E0B";
const F = "Calibri", FB = "Calibri";

const W = 13.333;
function slide() { const s = pptx.addSlide(); s.background = { color: BG }; return s; }
function title(s, t, x = 0.6, y = 0.5, w = 12.1, size = 32) {
  s.addText(t, { x, y, w, h: 0.7, fontFace: FB, bold: true, fontSize: size, color: WHITE, align: "left" });
}
function badge(s, n, x, y, color = CYAN) {
  s.addShape(pptx.ShapeType.ellipse, { x, y, w: 0.42, h: 0.42, fill: { color } });
  s.addText(String(n), { x, y, w: 0.42, h: 0.42, align: "center", valign: "middle", bold: true, fontSize: 16, color: BG, fontFace: FB });
}
function card(s, x, y, w, h, fill = CARD, line) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: line ? { color: line, width: 1.25 } : { type: "none" } });
}

// ---------------------------------------------------------------- Slide 1 — title
(() => {
  const s = slide();
  s.addShape(pptx.ShapeType.ellipse, { x: 0.6, y: 0.55, w: 0.8, h: 0.8, fill: { color: CYAN } });
  s.addText("🛡", { x: 0.6, y: 0.55, w: 0.8, h: 0.8, align: "center", valign: "middle", fontSize: 30, color: BG });
  s.addText("FRAUD INTELLIGENCE", { x: 1.6, y: 0.72, w: 9, h: 0.4, fontFace: FB, fontSize: 14, color: CYAN, charSpacing: 3, bold: true });

  s.addText("A scared citizen's WhatsApp message", { x: 0.6, y: 2.2, w: 12, h: 0.9, fontFace: FB, bold: true, fontSize: 44, color: WHITE });
  s.addText("becomes the data that maps a criminal fraud network — in real time.",
    { x: 0.6, y: 3.15, w: 12, h: 0.9, fontFace: FB, bold: true, fontSize: 44, color: CYAN });

  s.addText("A closed loop between two of the five PS6 components: the Citizen Fraud Shield is both the front-end demo and the live data source for back-end Fraud Network Graph Intelligence.",
    { x: 0.6, y: 4.5, w: 11.2, h: 0.9, fontFace: F, fontSize: 16, color: MUTED });

  s.addText("ET AI Hackathon 2026  ·  Problem Statement 6  ·  Team Arya + 3",
    { x: 0.6, y: 6.5, w: 12, h: 0.4, fontFace: F, fontSize: 14, color: MUTED });
})();

// ---------------------------------------------------------------- Slide 2 — problem
(() => {
  const s = slide();
  title(s, "The problem: scams that are organised, victims who are alone");
  // big stat
  card(s, 0.6, 1.6, 5.6, 3.0, CARD, RED);
  s.addText("₹1,776 cr", { x: 0.8, y: 2.0, w: 5.2, h: 1.2, fontFace: FB, bold: true, fontSize: 60, color: RED });
  s.addText("lost to digital-arrest & impersonation scams in just 9 months",
    { x: 0.8, y: 3.3, w: 5.2, h: 0.9, fontFace: F, fontSize: 17, color: TXT });

  const rows = [
    ["Citizens", "get warned late, or not at all — fear and isolation are the scam's main weapons."],
    ["Investigators", "receive scattered FIRs across districts with no way to see the network behind them."],
    ["The gap", "the citizen's report and the investigator's map are never connected."],
  ];
  let y = 1.6;
  rows.forEach(([h, b], i) => {
    card(s, 6.5, y, 6.2, 0.92);
    badge(s, i + 1, 6.7, y + 0.25, i === 2 ? RED : CYAN);
    s.addText(h, { x: 7.3, y: y + 0.12, w: 5.2, h: 0.34, fontFace: FB, bold: true, fontSize: 16, color: WHITE });
    s.addText(b, { x: 7.3, y: y + 0.46, w: 5.2, h: 0.4, fontFace: F, fontSize: 13, color: MUTED });
    y += 1.06;
  });
})();

// ---------------------------------------------------------------- Slide 3 — the insight (loop)
(() => {
  const s = slide();
  title(s, "The insight: don't build five silos — connect two");
  s.addText("Most teams ship the components disconnected. We make the citizen tool the sensor network that feeds fraud-network intelligence. That loop is the innovation no one else has.",
    { x: 0.6, y: 1.25, w: 12.1, h: 0.7, fontFace: F, fontSize: 16, color: MUTED });

  card(s, 0.8, 2.4, 4.4, 2.4, CARD, CYAN);
  s.addText("Citizen Fraud Shield", { x: 1.0, y: 2.65, w: 4.0, h: 0.4, fontFace: FB, bold: true, fontSize: 18, color: WHITE });
  s.addText("Paste a scam → instant verdict + advice.\nInstant protection at WhatsApp scale.", { x: 1.0, y: 3.15, w: 4.0, h: 1.3, fontFace: F, fontSize: 14, color: TXT });

  card(s, 8.1, 2.4, 4.4, 2.4, CARD, RED);
  s.addText("Fraud Network Graph", { x: 8.3, y: 2.65, w: 4.0, h: 0.4, fontFace: FB, bold: true, fontSize: 18, color: WHITE });
  s.addText("Reports become a live graph.\nLouvain finds rings, PageRank finds the kingpin.", { x: 8.3, y: 3.15, w: 4.0, h: 1.3, fontFace: F, fontSize: 14, color: TXT });

  // arrows between
  s.addShape(pptx.ShapeType.line, { x: 5.2, y: 3.25, w: 2.9, h: 0, line: { color: CYAN, width: 2.5, endArrowType: "triangle" } });
  s.addText("POST /report", { x: 5.2, y: 2.85, w: 2.9, h: 0.3, align: "center", fontFace: FB, bold: true, fontSize: 12, color: CYAN });
  s.addShape(pptx.ShapeType.line, { x: 5.2, y: 4.0, w: 2.9, h: 0, line: { color: RED, width: 2.5, beginArrowType: "triangle" } });
  s.addText("GET /graph · /package", { x: 5.2, y: 4.05, w: 2.9, h: 0.3, align: "center", fontFace: FB, bold: true, fontSize: 12, color: RED });

  s.addText("The same event that warns Lakshmi also grows the map that dismantles the ring.",
    { x: 0.6, y: 5.4, w: 12.1, h: 0.5, align: "center", italic: true, fontFace: F, fontSize: 18, color: CYAN });
})();

// ---------------------------------------------------------------- Slide 4 — live demo
(() => {
  const s = slide();
  title(s, "Live demo: one report, citizen → ring → court-ready PDF");
  const steps = [
    ["Lakshmi reports", "“CBI says my Aadhaar is in a laundering case, stay on the video call.”", CYAN],
    ["HIGH RISK verdict", "Digital Arrest Scam. Red flags + “Report to 1930” — in two seconds.", RED],
    ["Report joins the graph", "Her report links to others sharing the same UPI handle.", CYAN],
    ["Detect Rings", "Louvain lights up 24 reports across 3 districts = one operation.", AMBER],
    ["Kingpin", "PageRank flags the single UPI tying all 24 victims — priority #1.", RED],
    ["Intelligence Package", "Court-ready PDF: ring, linked reports, targets, confidence.", GREEN],
  ];
  let x = 0.6, y = 1.7;
  steps.forEach(([h, b, c], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const cx = 0.6 + col * 4.15, cy = 1.7 + row * 2.45;
    card(s, cx, cy, 3.85, 2.15);
    badge(s, i + 1, cx + 0.22, cy + 0.22, c);
    s.addText(h, { x: cx + 0.8, y: cy + 0.22, w: 2.9, h: 0.5, fontFace: FB, bold: true, fontSize: 16, color: WHITE });
    s.addText(b, { x: cx + 0.22, y: cy + 0.95, w: 3.4, h: 1.05, fontFace: F, fontSize: 13, color: MUTED });
  });
})();

// ---------------------------------------------------------------- Slide 5 — how it works
(() => {
  const s = slide();
  title(s, "How it works: a legible LangGraph pipeline");
  const pipe = [
    ["IntakeAgent", "regex normalize → Report\n(phone · UPI · authority)", CYAN],
    ["ClassifierAgent", "Ollama few-shot + rule layer\n→ verdict, flags, advice", CYAN],
    ["GraphLinkerAgent", "MERGE nodes/edges\nshared infra → rings form", CYAN],
    ["PackageAgent", "GDS + ReportLab\nevidence PDF (on-demand)", RED],
  ];
  let x = 0.6;
  pipe.forEach(([h, b, c], i) => {
    card(s, x, 1.9, 2.85, 1.9, CARD2, c);
    s.addText(h, { x: x + 0.15, y: 2.05, w: 2.6, h: 0.4, fontFace: FB, bold: true, fontSize: 15, color: WHITE });
    s.addText(b, { x: x + 0.15, y: 2.5, w: 2.6, h: 1.2, fontFace: F, fontSize: 12, color: MUTED });
    if (i < 3) s.addShape(pptx.ShapeType.line, { x: x + 2.85, y: 2.85, w: 0.3, h: 0, line: { color: MUTED, width: 2, endArrowType: "triangle" } });
    x += 3.15;
  });
  card(s, 0.6, 4.25, 6.0, 2.5, CARD);
  s.addText("GraphStore — one interface, two engines", { x: 0.8, y: 4.45, w: 5.6, h: 0.4, fontFace: FB, bold: true, fontSize: 16, color: CYAN });
  s.addText([
    { text: "▸ Neo4j + GDS  ", options: { bold: true, color: TXT } }, { text: "(primary — real graph DB)\n", options: { color: MUTED } },
    { text: "▸ NetworkX  ", options: { bold: true, color: TXT } }, { text: "(auto-fallback, zero infra)\n\n", options: { color: MUTED } },
    { text: "Frontends & PDF never import a concrete store.", options: { color: MUTED, italic: true } },
  ], { x: 0.8, y: 4.95, w: 5.6, h: 1.6, fontFace: F, fontSize: 14 });

  card(s, 6.9, 4.25, 5.8, 2.5, CARD);
  s.addText("Resilience (live-demo insurance)", { x: 7.1, y: 4.45, w: 5.4, h: 0.4, fontFace: FB, bold: true, fontSize: 16, color: GREEN });
  s.addText([
    { text: "Neo4j down → NetworkX fallback\n", options: {} },
    { text: "Ollama down → deterministic rule layer\n", options: {} },
    { text: "In-memory backend auto-seeds on startup\n", options: {} },
    { text: "Live demo fails → pre-recorded video", options: {} },
  ], { x: 7.1, y: 4.95, w: 5.4, h: 1.6, fontFace: F, fontSize: 14, color: TXT });
})();

// ---------------------------------------------------------------- Slide 6 — technical excellence
(() => {
  const s = slide();
  title(s, "Technical excellence: real GDS, not a toy");
  const items = [
    ["Louvain community detection", "Clusters reports into fraud rings from shared infrastructure. “These 24 reports across 3 districts are one operation.”", CYAN],
    ["PageRank centrality", "Surfaces the mule account / controller UPI at the centre of a ring. “This one node ties 24 victims together — arrest priority #1.”", RED],
    ["Multi-agent LangGraph", "Intake → Classify → GraphLink, with on-demand Package. A clean, legible agent graph.", AMBER],
    ["Pluggable backends", "One GraphStore ABC; Neo4j+GDS and NetworkX return identical DTOs. JP Morgan-grade graph engineering.", GREEN],
  ];
  let y = 1.7;
  items.forEach(([h, b, c], i) => {
    const cy = 1.7 + (i % 2) * 2.45, cx = 0.6 + Math.floor(i / 2) * 6.25;
    card(s, cx, cy, 5.9, 2.15);
    s.addShape(pptx.ShapeType.ellipse, { x: cx + 0.25, y: cy + 0.28, w: 0.3, h: 0.3, fill: { color: c } });
    s.addText(h, { x: cx + 0.75, y: cy + 0.22, w: 4.9, h: 0.45, fontFace: FB, bold: true, fontSize: 17, color: WHITE });
    s.addText(b, { x: cx + 0.25, y: cy + 0.85, w: 5.4, h: 1.15, fontFace: F, fontSize: 13.5, color: MUTED });
  });
})();

// ---------------------------------------------------------------- Slide 7 — low false positives
(() => {
  const s = slide();
  title(s, "Low false positives: the citizen tool you can trust");
  s.addText("The rubric penalises over-firing. A deterministic rule layer guarantees benign messages stay safe — even with the LLM offline.",
    { x: 0.6, y: 1.25, w: 12.1, h: 0.6, fontFace: F, fontSize: 16, color: MUTED });

  card(s, 0.6, 2.1, 6.0, 4.4, CARD, GREEN);
  s.addText("LIKELY SAFE — never flagged", { x: 0.85, y: 2.3, w: 5.5, h: 0.4, fontFace: FB, bold: true, fontSize: 17, color: GREEN });
  ["“Mom, dinner at 8? I'll bring dessert.”", "“Your OTP is 482913. Do not share it with anyone.”", "“Team standup at 10am, don't be late.”", "“Out for delivery today.”"].forEach((t, i) =>
    s.addText(t, { x: 0.85, y: 2.95 + i * 0.7, w: 5.5, h: 0.6, fontFace: F, fontSize: 14, color: TXT }));

  card(s, 6.9, 2.1, 5.8, 4.4, CARD, RED);
  s.addText("HIGH RISK — caught", { x: 7.15, y: 2.3, w: 5.3, h: 0.4, fontFace: FB, bold: true, fontSize: 17, color: RED });
  ["“CBI… you are under digital arrest, stay on the video call.”", "“Customs seized a parcel with drugs in your name.”", "“Transfer a refundable security deposit to clear your name.”", "“Aadhaar linked to money laundering — non-bailable warrant.”"].forEach((t, i) =>
    s.addText(t, { x: 7.15, y: 2.95 + i * 0.7, w: 5.3, h: 0.6, fontFace: F, fontSize: 14, color: TXT }));

  s.addText("Guarded by tests/test_rules_false_positive.py — benign inputs can never read HIGH RISK.",
    { x: 0.6, y: 6.7, w: 12.1, h: 0.4, italic: true, fontFace: F, fontSize: 13, color: MUTED });
})();

// ---------------------------------------------------------------- Slide 8 — synthetic data
(() => {
  const s = slide();
  title(s, "Synthetic data — disclosed, and honest about it");
  const cards = [
    ["What's planted", "3 fraud rings (digital-arrest, customs-parcel, ED-laundering), each sharing a UPI / account / device, across 2–3 districts.", CYAN],
    ["What's noise", "~150 isolated one-off scams + benign messages, so the algorithm must separate signal from noise.", AMBER],
    ["What's real", "Louvain & PageRank rediscover the rings with no hint where they are. The detection is genuine.", GREEN],
  ];
  let x = 0.6;
  cards.forEach(([h, b, c], i) => {
    card(s, x, 1.8, 3.95, 3.2);
    badge(s, i + 1, x + 0.25, 2.05, c);
    s.addText(h, { x: x + 0.85, y: 2.02, w: 2.9, h: 0.5, fontFace: FB, bold: true, fontSize: 17, color: WHITE });
    s.addText(b, { x: x + 0.25, y: 2.8, w: 3.5, h: 2.0, fontFace: F, fontSize: 14, color: MUTED });
    x += 4.15;
  });
  s.addText("Seeded (random.seed(42)) and reproducible. On real data, the pipeline runs unchanged — only the source differs.",
    { x: 0.6, y: 5.4, w: 12.1, h: 0.5, italic: true, fontFace: F, fontSize: 15, color: CYAN });
})();

// ---------------------------------------------------------------- Slide 9 — scalability
(() => {
  const s = slide();
  title(s, "Scalability: the graph is the platform");
  s.addText("The other PS6 components plug into the same graph as new node/edge types — zero rearchitecting.",
    { x: 0.6, y: 1.25, w: 12.1, h: 0.6, fontFace: F, fontSize: 16, color: MUTED });
  const fut = [
    ["Counterfeit currency CV", "Serial-number / image hits become Evidence nodes linked to the same rings.", CYAN],
    ["Geospatial crime mapping", "District attributes already on every report → heatmaps & movement patterns.", AMBER],
    ["National scale", "Stateless FastAPI + Neo4j cluster; the citizen app is just WhatsApp.", GREEN],
  ];
  let y = 1.95;
  fut.forEach(([h, b, c], i) => {
    card(s, 0.6, y, 12.1, 1.35);
    s.addShape(pptx.ShapeType.ellipse, { x: 0.85, y: y + 0.45, w: 0.45, h: 0.45, fill: { color: c } });
    s.addText(h, { x: 1.5, y: y + 0.2, w: 5.0, h: 0.9, valign: "middle", fontFace: FB, bold: true, fontSize: 19, color: WHITE });
    s.addText(b, { x: 6.5, y: y + 0.2, w: 6.0, h: 0.9, valign: "middle", fontFace: F, fontSize: 15, color: MUTED });
    y += 1.55;
  });
})();

// ---------------------------------------------------------------- Slide 10 — impact / close
(() => {
  const s = slide();
  s.addText("We built the loop that wasn't there.", { x: 0.6, y: 2.2, w: 12, h: 1.0, fontFace: FB, bold: true, fontSize: 46, color: WHITE });
  s.addText("Instant citizen protection at WhatsApp scale + a live, prioritised target list for investigators.",
    { x: 0.6, y: 3.4, w: 11.5, h: 0.8, fontFace: F, fontSize: 20, color: CYAN });

  const stats = [["25%", "Innovation — the closed loop"], ["25%", "Business impact — ₹1,776 cr"], ["20%", "Technical — real GDS + LangGraph"]];
  let x = 0.6;
  stats.forEach(([n, l]) => {
    card(s, x, 4.7, 3.95, 1.6);
    s.addText(n, { x: x + 0.25, y: 4.85, w: 3.5, h: 0.7, fontFace: FB, bold: true, fontSize: 40, color: CYAN });
    s.addText(l, { x: x + 0.25, y: 5.6, w: 3.5, h: 0.5, fontFace: F, fontSize: 13, color: MUTED });
    x += 4.15;
  });
  s.addText("ET AI Hackathon 2026 · PS6 · Team Arya + 3", { x: 0.6, y: 6.7, w: 12, h: 0.4, fontFace: F, fontSize: 14, color: MUTED });
})();

pptx.writeFile({ fileName: path.join(__dirname, "pitch-deck.pptx") }).then(f => console.log("wrote", f));
