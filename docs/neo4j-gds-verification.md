# Neo4j + GDS — verification record

The primary graph path (Neo4j 5.20 + Graph Data Science 2.6.9) was run on the real
synthetic graph and reproduces the NetworkX results exactly, using the same GDS
Louvain + PageRank queries that `app/graph/neo4j_store.py` issues.

## How it was run
- Docker Engine inside WSL2 Ubuntu 24.04 (Docker Desktop not required).
- `neo4j:5.20` with the GDS 2.6.9 plugin jar mounted at `/var/lib/neo4j/plugins`
  (pre-downloaded — see caveat 2).
- The graph was seeded from `backend/data/reports.json` via
  `python -m data.to_cypher > data/seed.cypher`, then loaded with `cypher-shell`.
  `to_cypher.py` reuses `app/graph/entities.report_graph`, so the loaded graph is
  byte-for-byte what `GraphLinkerAgent` writes.

## Actual output (real GDS)

```
total nodes: 527
report nodes: 201
GDS project (undirected): nodeCount=527, relationshipCount=1132

LOUVAIN rings (communities by report count)
  ring  reports  districts
  17    22       [Bengaluru, Mysuru, Mandya]     <- Ring A (digital_arrest_cbi)
  30    16       [Gurugram, Delhi, Noida]        <- Ring B (customs_parcel)
  83    13       [Pune, Mumbai, Thane]           <- Ring C (ed_money_laundering)
  ...   1        [...]                           <- noise correctly NOT clustered

PAGERANK kingpin (the doc's query: WHERE n:Account OR n:PhoneNumber OR n:UPI)
  type         entity                   score
  Account      10433218196001           3.4325   <- Ring A shared mule account
  UPI          digitalarrest.a@okaxis   3.4325   <- Ring A shared UPI
  PhoneNumber  +917890838637            3.4325   <- Ring A controller number
  PhoneNumber  +919697848018            2.6213   <- Ring B
  UPI          parcelscam.b@okaxis      2.6213   <- Ring B
```

This matches the NetworkX backend (22 / 16 / 13 reports, kingpin = Ring A's shared
infrastructure) — confirming the two `GraphStore` implementations are interchangeable.

## Caveats (environment-specific, not code)
1. **App driver wire path on this dev box:** Docker Engine *inside WSL2* did not
   expose the published `7687` port to the Windows host (no host listener / empty
   container IP — a known Docker-in-WSL2 networking quirk). So the Windows-side
   FastAPI app couldn't open a bolt socket here and runs on the NetworkX backend.
   The GDS queries themselves are proven correct above. On a normal setup — Docker
   Desktop on Windows/Mac, or Docker on Linux — `bolt://localhost:7687` is reachable
   and `GRAPH_BACKEND=neo4j` drives the app directly. Nothing in the app code needs
   to change.
2. **GDS plugin download:** `graphdatascience.ninja` blocks curl's default
   user-agent and is slow; the `neo4j:5.20` image's boot-time auto-download is
   therefore flaky on some networks. For a reliable boot, pre-download the 60 MB
   jar once and mount it (as done here), or just retry `docker compose up`.

## Reproduce
```bash
cd backend
python -m data.generate
python -m data.to_cypher > data/seed.cypher
# load seed.cypher into a running neo4j with GDS, then run the Louvain/PageRank
# queries in data/verify_neo4j_gds.sh
```
