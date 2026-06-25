#!/usr/bin/env bash
# One-shot Neo4j + GDS verification, run entirely inside a single WSL invocation
# so the WSL VM (and the neo4j container) stays alive throughout.
set -e
CS="docker exec fraud-neo4j cypher-shell -u neo4j -p fraudpass --format plain"
SEED=/mnt/c/Users/arya1/OneDrive/Desktop/et/backend/data/seed.cypher

echo "=== start container ==="
docker start fraud-neo4j >/dev/null

echo "=== wait for GDS ==="
for i in $(seq 1 40); do
  if docker exec fraud-neo4j cypher-shell -u neo4j -p fraudpass "RETURN gds.version() AS v" 2>/dev/null | grep -q "2.6"; then
    echo "GDS ready"; break
  fi
  sleep 4
done

echo "=== load seed (real graph write) ==="
docker exec -i fraud-neo4j cypher-shell -u neo4j -p fraudpass < "$SEED" > /tmp/load.log 2>&1 || true
grep -i error /tmp/load.log | head -3 || true
echo -n "total nodes: "; $CS "MATCH (n) RETURN count(n) AS n" | tail -1
echo -n "report nodes: "; $CS "MATCH (r:Report) RETURN count(r) AS n" | tail -1

echo "=== GDS project (undirected) ==="
docker exec fraud-neo4j cypher-shell -u neo4j -p fraudpass \
  "CALL gds.graph.exists('fg') YIELD exists WITH exists WHERE exists CALL gds.graph.drop('fg') YIELD graphName RETURN graphName" 2>/dev/null || true
$CS "CALL gds.graph.project('fg','*',{ALL:{type:'*',orientation:'UNDIRECTED'}}) YIELD nodeCount, relationshipCount RETURN nodeCount, relationshipCount"

echo "=== LOUVAIN rings (communities by report count) ==="
$CS "CALL gds.louvain.stream('fg') YIELD nodeId, communityId WITH gds.util.asNode(nodeId) AS n, communityId WHERE n:Report RETURN communityId AS ring, count(*) AS reports, collect(DISTINCT n.district)[..3] AS districts ORDER BY reports DESC LIMIT 6"

echo "=== PAGERANK kingpin (the doc's query) ==="
$CS "CALL gds.pageRank.stream('fg') YIELD nodeId, score WITH gds.util.asNode(nodeId) AS n, score WHERE n:Account OR n:PhoneNumber OR n:UPI RETURN labels(n)[0] AS type, n.value AS entity, round(score,4) AS score ORDER BY score DESC LIMIT 5"

echo "=== DONE ==="
