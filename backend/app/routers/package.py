"""Intelligence-package endpoints for one ring.
GET /package/{ring_id}      -> JSON (ring, subgraph, centrality, pdf_url)
GET /package/{ring_id}/pdf  -> the rendered PDF file
"""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agents import package as package_agent
from app.schema import GraphDTO, Ring, ScoredNode

router = APIRouter(tags=["intelligence"])


class PackageResponse(BaseModel):
    ring: Ring
    subgraph: GraphDTO
    centrality: list[ScoredNode]
    pdf_url: str


@router.get("/package/{ring_id}", response_model=PackageResponse)
def get_package(ring_id: str) -> PackageResponse:
    pkg = package_agent.build(ring_id)
    if pkg is None:
        raise HTTPException(404, f"Ring {ring_id} not found")
    return PackageResponse(
        ring=pkg.ring,
        subgraph=pkg.subgraph,
        centrality=pkg.centrality,
        pdf_url=f"/package/{ring_id}/pdf",
    )


@router.get("/package/{ring_id}/pdf")
def get_package_pdf(ring_id: str):
    pkg = package_agent.build(ring_id)
    if pkg is None or not os.path.exists(pkg.pdf_path):
        raise HTTPException(404, f"Package for {ring_id} not found")
    return FileResponse(
        pkg.pdf_path,
        media_type="application/pdf",
        filename=f"intelligence_package_{ring_id}.pdf",
    )
