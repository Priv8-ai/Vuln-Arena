from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request


ROOT = Path(__file__).resolve().parent
PROFILE_IDS = {item["id"] for item in json.loads((ROOT / "profiles.json").read_text(encoding="utf-8"))}
RUN_SEED = os.getenv("ARENA_RUN_SEED", "local-training-seed")
app = Flask(__name__)


def digest(site: str, label: str, length: int) -> str:
    return hmac.new(RUN_SEED.encode(), f"{site}:{label}".encode(), hashlib.sha256).hexdigest()[:length]


@app.get("/status")
def status():
    return jsonify(ok=True, service="cms-private-metadata")


@app.get("/token")
def token():
    site = request.args.get("site", "")
    if site not in PROFILE_IDS:
        return jsonify(error="known site required"), 404
    return jsonify(
        site=site,
        integration_token=digest(site, "integration-token", 24),
        proof=f"ARENA{{{site}-cms-04-{digest(site, 'CMS-04', 12)}}}",
        audience="cms-role-sync",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, threaded=True)
