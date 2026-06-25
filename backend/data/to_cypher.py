"""Emit a .cypher seed file from reports.json using the SAME node/edge logic as
the Neo4j store (app.graph.entities + the Report-node district attribute), so a
cypher-shell load reproduces exactly what GraphLinkerAgent would write. Used to
verify the real Neo4j + GDS path. Run: python -m data.to_cypher > data/seed.cypher
"""
from __future__ import annotations

import json
import os

from app.graph.entities import nid, report_graph
from app.schema import Report

HERE = os.path.dirname(__file__)


def esc(v: str) -> str:
    return v.replace("\\", "\\\\").replace("'", "\\'")


def main() -> None:
    with open(os.path.join(HERE, "reports.json"), encoding="utf-8") as f:
        raw = json.load(f)

    print("MATCH (n) DETACH DELETE n;")
    for d in raw:
        r = Report(**d)
        nodes, edges = report_graph(r)
        for label, value in nodes:
            print(f"MERGE (n:{label} {{id:'{esc(nid(label,value))}'}}) SET n.value='{esc(value)}';")
        # district attribute on the Report node (mirrors neo4j_store.write_report)
        if r.district:
            print(f"MATCH (n:Report {{id:'{esc(nid('Report', r.report_id))}'}}) "
                  f"SET n.district='{esc(r.district)}';")
        for s_label, s_val, etype, d_label, d_val in edges:
            print(f"MATCH (a:{s_label} {{id:'{esc(nid(s_label,s_val))}'}}), "
                  f"(b:{d_label} {{id:'{esc(nid(d_label,d_val))}'}}) MERGE (a)-[:{etype}]->(b);")


if __name__ == "__main__":
    main()
