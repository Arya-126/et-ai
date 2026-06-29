"""Privacy-preserving collaborative training via Federated Averaging (FedAvg).

Banks, telcos and law-enforcement can't pool raw PII to build one fraud model.
Here each organisation ("edge node") holds its OWN data and trains a local logistic
-regression fraud classifier; only the model WEIGHTS (never the rows) are sent to a
central server, which averages them (FedAvg). Accuracy climbs each round while raw
data never leaves the node — the real privacy guarantee of federated learning.

Real numpy implementation over disclosed synthetic per-node datasets.
"""
from __future__ import annotations

import numpy as np

NODES = ["HDFC Bank", "Airtel Telecom", "State Police Cyber Cell", "Paytm Payments"]
N_FEATURES = 6   # e.g. [unsaved_caller, authority_claim, otp_request, upi_paid, intl_route, urgency]


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _make_node_data(rng, n=400):
    """Synthetic labelled samples: a hidden 'true' weight maps features → fraud.
    Returns X augmented with an intercept (bias) column so the model can fit the
    decision threshold."""
    true_w = np.array([2.4, 1.8, 2.9, 2.1, 1.6, 1.2])
    X = rng.random((n, N_FEATURES))
    p = _sigmoid(X @ true_w - 4.0)
    y = (rng.random(n) < p).astype(float)
    X_aug = np.hstack([X, np.ones((n, 1))])      # intercept column
    return X_aug, y


def _train_local(X, y, w, lr=1.5, epochs=15):
    """A few local gradient steps starting from the global weights."""
    w = w.copy()
    for _ in range(epochs):
        grad = X.T @ (_sigmoid(X @ w) - y) / len(y)
        w -= lr * grad
    return w


def _accuracy(w, X, y):
    return float(((_sigmoid(X @ w) >= 0.5).astype(float) == y).mean())


def run(rounds: int = 8) -> dict:
    """Run FedAvg across the edge nodes; return the convergence curve + privacy facts."""
    rng = np.random.default_rng(42)
    node_data = [_make_node_data(rng) for _ in NODES]
    # shared held-out test set (eval only)
    Xt, yt = _make_node_data(rng, n=600)

    global_w = np.zeros(N_FEATURES + 1)   # +1 intercept
    history = []
    for r in range(1, rounds + 1):
        local_ws, sizes = [], []
        for (X, y) in node_data:
            local_ws.append(_train_local(X, y, global_w))
            sizes.append(len(y))
        # FedAvg: size-weighted mean of the local weights (no raw data shared)
        sizes = np.array(sizes, dtype=float)
        global_w = np.average(np.stack(local_ws), axis=0, weights=sizes)
        history.append({"round": r, "global_accuracy": round(_accuracy(global_w, Xt, yt), 3)})

    return {
        "nodes": NODES,
        "rounds": rounds,
        "history": history,
        "final_accuracy": history[-1]["global_accuracy"],
        "samples_per_node": int(len(node_data[0][1])),
        "bytes_of_raw_data_shared": 0,
        "weights_shared_per_round": N_FEATURES,
        "privacy_note": (
            "Only model weights leave each node — raw customer rows never move. "
            "The shared global model still learns the fraud signal across all four "
            "organisations (federated averaging)."
        ),
    }
