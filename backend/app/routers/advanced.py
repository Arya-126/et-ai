"""Advanced defense capabilities (the 'Defense Lab').
  POST /advanced/zkp/verify-officer     Schnorr ZK officer verification
  GET  /advanced/sip/samples            sample SIP captures
  POST /advanced/sip                    SIP/DPI forensic analysis
  POST /advanced/honeypot/engage        scam-baiting agent reply + IoC extraction
  POST /advanced/honeypot/sinkhole      propagate IoCs (simulated) + block-list
  GET  /advanced/honeypot/sinkholed     all sinkholed IoCs
  POST /advanced/liveness               rPPG liveness on an uploaded clip
  GET  /advanced/liveness/demo          rPPG on a disclosed synthetic signal
  GET  /advanced/federated              FedAvg collaborative-training round
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.advanced import federated, honeypot, liveness, sip, zkp

router = APIRouter(prefix="/advanced", tags=["advanced"])


# ---- ZKP ----------------------------------------------------------------
class ZkpReq(BaseModel):
    impersonator: bool = False
    message: str = "I am a verified officer requesting to speak with you."


@router.post("/zkp/verify-officer")
def zkp_verify(req: ZkpReq) -> dict:
    return zkp.demo(req.impersonator, message=req.message)


# ---- SIP / DPI ----------------------------------------------------------
class SipReq(BaseModel):
    sip_text: str
    packet_meta: dict | None = None


@router.get("/sip/samples")
def sip_samples() -> dict:
    return sip.SAMPLES


@router.post("/sip")
def sip_analyze(req: SipReq) -> dict:
    return sip.analyze(req.sip_text, req.packet_meta)


# ---- honeypot -----------------------------------------------------------
class EngageReq(BaseModel):
    history: list[dict] = []
    message: str


@router.post("/honeypot/engage")
def honeypot_engage(req: EngageReq) -> dict:
    return honeypot.engage(req.history, req.message)


class SinkholeReq(BaseModel):
    iocs: dict[str, list[str]]


@router.post("/honeypot/sinkhole")
def honeypot_sinkhole(req: SinkholeReq) -> dict:
    return honeypot.sinkhole(req.iocs)


@router.get("/honeypot/sinkholed")
def honeypot_sinkholed() -> list[dict]:
    return honeypot.sinkhole_store.all()


# ---- liveness -----------------------------------------------------------
@router.post("/liveness")
async def liveness_video(file: UploadFile = File(...)) -> dict:
    res = liveness.analyze_video(await file.read())
    if res is None:
        raise HTTPException(503, "Liveness engine unavailable (OpenCV missing).")
    return res


@router.get("/liveness/demo")
def liveness_demo(live: bool = True) -> dict:
    return liveness.demo(live)


# ---- federated ----------------------------------------------------------
@router.get("/federated")
def federated_round(rounds: int = 8) -> dict:
    return federated.run(rounds=max(1, min(rounds, 30)))
