# Pitch Deck Outline (~10 slides)

Structure: problem → the loop insight → live demo → tech → scalability → impact.

1. **Title** — "Fraud Network Intelligence + Citizen Fraud Shield." One line:
   *A scared citizen's WhatsApp message becomes the data that maps a criminal
   fraud network — in real time.* Team Arya + 3.

2. **The problem** — Digital-arrest & impersonation scams. **Rs 1,776 crore lost in
   9 months.** Citizens get warned (maybe) and investigators get scattered FIRs —
   but the two are never connected.

3. **The insight (the differentiator)** — Five sub-components, but the win is
   *connecting two*. The citizen tool is also the **sensor network** that feeds
   fraud-network intelligence. Nobody else closes this loop.

4. **Live demo** — (run `docs/demo-runbook.md`). Lakshmi → HIGH RISK verdict →
   report drops on the graph → Detect Rings → kingpin → Intelligence Package PDF.

5. **How it works** — the architecture diagram (`docs/architecture.md`). LangGraph
   pipeline: Intake → Classify → GraphLink, + on-demand Package.

6. **Technical excellence** — Real **GDS**: Louvain community detection finds rings,
   PageRank centrality finds the mule account. Multi-agent LangGraph orchestration.
   One `GraphStore` interface, Neo4j-primary with NetworkX fallback.

7. **Low false positives** — The rubric penalizes over-firing. Show benign messages
   ("Mom, dinner at 8?") returning LIKELY SAFE. Deterministic rule layer guarantees
   it even with the LLM offline. (`tests/test_rules_false_positive.py`.)

8. **Synthetic data, disclosed** — `docs/synthetic-disclosure.md`. Rings are
   planted; the *detection* of them is real. On real data, the pipeline is unchanged.

9. **Scalability / future scope** — The graph is the platform. Counterfeit-currency
   CV and geospatial crime mapping **plug into the same graph** as new node/edge
   types — zero rearchitecting. (One slide, zero build hours.)

10. **Impact & ask** — Instant citizen protection at WhatsApp scale + a live,
    prioritized target list for investigators. "We built the loop that wasn't there."

## Appendix slides (optional)
- The kingpin Cypher query and a Neo4j Browser screenshot.
- Resilience: Neo4j→NetworkX and Ollama→rules fallbacks.
