"""Advanced defense capabilities — real algorithms must behave correctly."""
from app.advanced import federated, honeypot, liveness, sip, zkp


def test_zkp_genuine_verifies_impostor_rejected():
    assert zkp.demo(impersonator=False)["verified"] is True
    assert zkp.demo(impersonator=True)["verified"] is False
    # primitive: a proof with the wrong secret never verifies
    x, y = zkp.keypair()
    fx, _ = zkp.keypair()
    assert zkp.verify(y, "m", zkp.prove(x, "m")) is True
    assert zkp.verify(y, "m", zkp.prove(fx, "m")) is False


def test_sip_flags_fraud_compound():
    fraud = sip.SAMPLES["fraud_compound"]
    legit = sip.SAMPLES["legit_carrier"]
    assert sip.analyze(fraud["sip"], fraud["meta"])["verdict"] == "ILLICIT GATEWAY"
    assert sip.analyze(legit["sip"], legit["meta"])["verdict"] == "CLEAN"


def test_honeypot_extracts_iocs():
    iocs = honeypot.extract_iocs("send to refund.cbi@okaxis account 50100234567890 call 9876543210")
    assert "refund.cbi@okaxis" in iocs.get("upi", [])
    assert "50100234567890" in iocs.get("account", [])
    out = honeypot.sinkhole(iocs)
    assert out["total_sinkholed"] >= 2


def test_liveness_distinguishes_live_from_spoof():
    assert liveness.demo(live=True)["live"] is True
    assert liveness.demo(live=False)["live"] is False


def test_federated_improves_without_sharing_data():
    r = federated.run(rounds=8)
    assert r["bytes_of_raw_data_shared"] == 0
    assert r["final_accuracy"] >= r["history"][0]["global_accuracy"]
    assert r["final_accuracy"] > 0.7
