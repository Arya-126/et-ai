"""Force the NetworkX backend for tests so they never need Docker/Neo4j, and
reset the global store between tests."""
import os

os.environ.setdefault("GRAPH_BACKEND", "networkx")

import pytest

from app.graph import factory


@pytest.fixture(autouse=True)
def fresh_store():
    factory.reset_store()
    yield
    factory.reset_store()
