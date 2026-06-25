"""Env-driven settings. The GRAPH_BACKEND switch and Ollama/Neo4j coords live here."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Graph backend: "neo4j" or "networkx"
    graph_backend: str = "neo4j"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "fraudpass"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 30

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    # Ring detection: minimum community size to call something a "ring"
    min_ring_size: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
