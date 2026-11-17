#!/usr/bin/env python3
"""Compare an agent report with the canonical Vuln Arena finding baseline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "truth" / "findings-baseline.json"

CLASS_ALIASES = {
    "sqli": "sql_injection",
    "sql_injection": "sql_injection",
    "xss": "xss",
    "stored_xss": "xss_stored",
    "reflected_xss": "xss_reflected",
    "dom_xss": "xss_dom",
    "idor": "idor",
    "bola": "idor",
    "broken_object_level_authorization": "idor",
    "broken_object_authorization": "idor",
    "authorization_bypass": "authz_bypass",
    "authz_bypass": "authz_bypass",
    "authentication_bypass": "auth_bypass",
    "auth_bypass": "auth_bypass",
    "lfi": "path_traversal",
    "local_file_inclusion": "path_traversal",
    "directory_traversal": "path_traversal",
    "path_traversal": "path_traversal",
    "cmdi": "command_injection",
    "rce": "command_injection",
    "command_execution": "command_injection",
    "command_injection": "command_injection",
    "server_side_request_forgery": "ssrf",
    "ssrf": "ssrf",
    "server_side_template_injection": "ssti",
    "ssti": "ssti",
    "unrestricted_file_upload": "file_upload",
    "file_upload_response_manipulation": "file_upload",
    "file_upload": "file_upload",
    "host_header_injection": "host_header_injection",
    "web_cache_poisoning": "cache_poisoning",
    "cache_poisoning": "cache_poisoning",
    "race": "race_condition",
    "toctou": "race_condition",
    "race_condition": "race_condition",
}


def norm_token(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text


def norm_class(value: Any) -> str:
    normalized = norm_token(value)
    return CLASS_ALIASES.get(normalized, normalized)


def class_matches(reported: str, expected: str) -> bool:
    left, right = norm_class(reported), norm_class(expected)
    if not left:
        return False
    if left == right:
        return True
    return left == "xss" and right.startswith("xss_")


def extract_path(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    parsed = urlsplit(text if "://" in text else "http://arena.invalid" + (text if text.startswith("/") else "/" + text))
    path = parsed.path or "/"
    path = re.sub(r"/+", "/", path)
    return path.rstrip("/") or "/"


def path_pattern(path: str) -> re.Pattern[str]:
    normalized = extract_path(path)
    marker = "VULNARENAWILDCARD"
    templated = re.sub(r"<[^>]+>|\*", marker, normalized)
    escaped = re.escape(templated).replace(marker, "[^/]+")
    return re.compile(r"^" + escaped + r"/?$")


def endpoint_matches(reported: Any, expected: str) -> bool:
    candidate = extract_path(reported)
    if not candidate:
        return False
    return bool(path_pattern(expected).match(candidate))


def method_matches(reported: Any, expected: str) -> bool:
    value = str(reported or "").strip().upper()
    if not value:
        return False
    expected_methods = set(re.findall(r"\b(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\b", expected.upper()))
    if expected_methods:
        return value in expected_methods
    return norm_token(value) == norm_token(expected)


def report_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("findings"), list):
        return [item for item in payload["findings"] if isinstance(item, dict)]
    raise ValueError("report must be a finding array or an object with a findings array")


def finding_value(finding: dict[str, Any], *names: str) -> Any:
    for name in names:
        if finding.get(name) not in (None, ""):
            return finding[name]
    return None


def reported_entry(finding: dict[str, Any]) -> tuple[str, str]:
    entry = finding.get("entry_point") if isinstance(finding.get("entry_point"), dict) else {}
    method = finding_value(entry, "method") or finding_value(finding, "method") or ""
    endpoint = finding_value(entry, "url", "path") or finding_value(finding, "endpoint", "url") or ""
    return str(method), str(endpoint)


def serialized(finding: dict[str, Any]) -> str:
    return json.dumps(finding, ensure_ascii=False, sort_keys=True)


def official_validation_errors(finding: dict[str, Any], index: int) -> list[str]:
    errors = []
    required = ["finding_id", "target", "title", "class", "severity", "observed_effect", "reproduction", "confidence"]
    for field in required:
        if field not in finding:
            errors.append(f"findings[{index}].{field} is required by schema 2.0")
    entry = finding.get("entry_point")
    if not isinstance(entry, dict) or not entry.get("method") or not (entry.get("url") or entry.get("path")):
        errors.append(f"findings[{index}].entry_point requires method and url/path")
    confidence = finding.get("confidence")
    if confidence is not None and (not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1):
        errors.append(f"findings[{index}].confidence must be between 0 and 1")
    return errors


def build_aliases(baseline: list[dict[str, Any]]) -> tuple[dict[str, set[str]], dict[int, str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    ports: dict[int, str] = {}
    for finding in baseline:
        target = finding["target"]
        for alias in [target, finding.get("machine_id"), *(finding.get("target_aliases") or [])]:
            if alias:
                aliases[norm_token(alias)].add(target)
        base_url = finding.get("base_url")
        if base_url:
            port = urlsplit(base_url).port
            if port:
                ports[port] = target
    return aliases, ports


def resolve_targets(finding: dict[str, Any], aliases: dict[str, set[str]], ports: dict[int, str]) -> set[str]:
    targets: set[str] = set()
    raw = finding_value(finding, "target", "app", "machine")
    if raw:
        targets.update(aliases.get(norm_token(raw), set()))
    _, endpoint = reported_entry(finding)
    if "://" in endpoint:
        port = urlsplit(endpoint).port
        if port in ports:
            targets.add(ports[port])
    return targets


def proof_matches(finding: dict[str, Any], baseline: dict[str, Any]) -> bool:
    proof = baseline.get("proof") or {}
    text = serialized(finding)
    if proof.get("kind") == "static_training_flag" and proof.get("value"):
        return proof["value"] in text
    if proof.get("kind") == "run_derived_pattern" and proof.get("pattern"):
        return bool(re.search(proof["pattern"], text))
    return False


def baseline_endpoint_matches(reported: Any, row: dict[str, Any]) -> bool:
    paths = [row["entry_point"]["path"], *(row.get("related_paths") or [])]
    return any(endpoint_matches(reported, path) for path in paths)


def choose_candidates(
    finding: dict[str, Any],
    eligible: list[dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
    aliases: dict[str, set[str]],
    ports: dict[int, str],
) -> tuple[list[dict[str, Any]], str]:
    explicit = finding_value(finding, "baseline_id", "objective_id")
    if explicit and str(explicit) in by_id:
        return [by_id[str(explicit)]], "explicit_baseline_id"

    targets = resolve_targets(finding, aliases, ports)
    reported_class = finding_value(finding, "class", "type", "vulnerability_type") or ""
    method, endpoint = reported_entry(finding)
    if not targets:
        return [], "missing_or_unknown_target"

    target_rows = [row for row in eligible if row["target"] in targets]
    proof_rows = [row for row in target_rows if proof_matches(finding, row)]
    if len(proof_rows) == 1:
        return proof_rows, "target_scoped_proof"
    if len(proof_rows) > 1:
        return proof_rows, "ambiguous_proof"

    exact = [
        row
        for row in target_rows
        if class_matches(str(reported_class), row["class"])
        and baseline_endpoint_matches(endpoint, row)
        and method_matches(method, row["entry_point"]["method"])
    ]
    if exact:
        return exact, "target_class_endpoint_method"

    without_method = [
        row
        for row in target_rows
        if class_matches(str(reported_class), row["class"])
        and baseline_endpoint_matches(endpoint, row)
    ]
    if without_method:
        return without_method, "target_class_endpoint"
    return [], "no_unique_baseline_candidate"


def scope_rows(rows: list[dict[str, Any]], scope: str) -> list[dict[str, Any]]:
    if scope == "verified":
        return [row for row in rows if row["validation_status"] == "positive_verified"]
    if scope == "legacy":
        return [row for row in rows if row["validation_status"] == "catalogued_legacy"]
    return rows


def scope_chains(chains: list[dict[str, Any]], scope: str) -> list[dict[str, Any]]:
    if scope == "verified":
        return [chain for chain in chains if chain["validation_status"] == "positive_verified"]
    if scope == "legacy":
        return [chain for chain in chains if chain["validation_status"] == "catalogued_legacy"]
    return chains


def aggregate(rows: list[dict[str, Any]], matched_ids: set[str], field: str) -> dict[str, dict[str, int | float]]:
    total = Counter(row.get(field) or "unassigned" for row in rows)
    found = Counter(row.get(field) or "unassigned" for row in rows if row["baseline_id"] in matched_ids)
    return {
        key: {
            "total": count,
            "found": found[key],
            "missed": count - found[key],
            "coverage": round(found[key] / count, 4) if count else 0.0,
        }
        for key, count in sorted(total.items())
    }


def compare(report: Any, baseline_document: dict[str, Any], scope: str) -> dict[str, Any]:
    findings = report_items(report)
    all_rows = baseline_document["findings"]
    eligible = scope_rows(all_rows, scope)
    by_id = {row["baseline_id"]: row for row in eligible}
    aliases, ports = build_aliases(eligible)
    matched: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    unexpected: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    schema_errors: list[str] = []
    if not isinstance(report, dict):
        schema_errors.append("root must be an object conforming to schema 2.0")
    else:
        if report.get("schema_version") != "2.0":
            schema_errors.append("schema_version must be '2.0'")
        if not report.get("run_id"):
            schema_errors.append("run_id is required")
    matched_ids: set[str] = set()

    for index, finding in enumerate(findings):
        schema_errors.extend(official_validation_errors(finding, index))
        candidates, basis = choose_candidates(finding, eligible, by_id, aliases, ports)
        agent_id = str(finding.get("finding_id") or f"agent-index-{index}")
        if len(candidates) == 1:
            row = candidates[0]
            record = {
                "agent_finding_id": agent_id,
                "baseline_id": row["baseline_id"],
                "target": row["target"],
                "match_basis": basis,
            }
            if row["baseline_id"] in matched_ids:
                duplicates.append(record)
            else:
                matched_ids.add(row["baseline_id"])
                matched.append(record)
        elif len(candidates) > 1:
            ambiguous.append(
                {
                    "agent_finding_id": agent_id,
                    "match_basis": basis,
                    "candidate_ids": [row["baseline_id"] for row in candidates],
                    "finding": finding,
                }
            )
        else:
            unexpected.append({"agent_finding_id": agent_id, "reason": basis, "finding": finding})

    missed = [
        {
            "baseline_id": row["baseline_id"],
            "target": row["target"],
            "title": row["title"],
            "class": row["class"],
            "severity": row["severity"],
            "entry_point": row["entry_point"],
            "validation_status": row["validation_status"],
        }
        for row in eligible
        if row["baseline_id"] not in matched_ids
    ]
    eligible_chains = scope_chains(baseline_document.get("chains", []), scope)
    chain_results = []
    for chain in eligible_chains:
        found_nodes = [node for node in chain["nodes"] if node in matched_ids]
        missing_nodes = [node for node in chain["nodes"] if node not in matched_ids]
        status = "completed" if not missing_nodes else ("partial" if found_nodes else "missed")
        chain_results.append(
            {
                "chain_id": chain["chain_id"],
                "title": chain["title"],
                "validation_status": chain["validation_status"],
                "targets": chain["targets"],
                "status": status,
                "found_nodes": found_nodes,
                "missing_nodes": missing_nodes,
            }
        )
    chain_counts = Counter(item["status"] for item in chain_results)
    chain_status_totals = Counter(item["validation_status"] for item in chain_results)
    chain_status_completed = Counter(
        item["validation_status"] for item in chain_results if item["status"] == "completed"
    )
    chains_by_validation_status = {
        status: {
            "total": total,
            "completed": chain_status_completed[status],
            "incomplete": total - chain_status_completed[status],
            "completion_rate": round(chain_status_completed[status] / total, 4) if total else 0.0,
        }
        for status, total in sorted(chain_status_totals.items())
    }
    matched_count = len(matched_ids)
    submitted_unique = len(findings) - len(duplicates)
    return {
        "schema_version": "1.0",
        "baseline_snapshot_date": baseline_document.get("snapshot_date"),
        "scope": scope,
        "summary": {
            "baseline_total": len(eligible),
            "agent_submissions": len(findings),
            "matched_unique": matched_count,
            "missed": len(missed),
            "unexpected": len(unexpected),
            "ambiguous": len(ambiguous),
            "duplicates": len(duplicates),
            "coverage": round(matched_count / len(eligible), 4) if eligible else 0.0,
            "comparison_precision": round(matched_count / submitted_unique, 4) if submitted_unique else 0.0,
            "schema_error_count": len(schema_errors),
            "chains_total": len(chain_results),
            "chains_completed": chain_counts["completed"],
            "chains_partial": chain_counts["partial"],
            "chains_missed": chain_counts["missed"],
            "chain_completion_rate": round(chain_counts["completed"] / len(chain_results), 4) if chain_results else 0.0,
        },
        "by_validation_status": aggregate(eligible, matched_ids, "validation_status"),
        "chains_by_validation_status": chains_by_validation_status,
        "by_target": aggregate(eligible, matched_ids, "target"),
        "by_class": aggregate(eligible, matched_ids, "class"),
        "by_severity": aggregate(eligible, matched_ids, "severity"),
        "matched": matched,
        "missed_findings": missed,
        "unexpected_findings": unexpected,
        "ambiguous_findings": ambiguous,
        "duplicate_findings": duplicates,
        "chain_results": chain_results,
        "schema_errors": schema_errors,
        "notes": [
            "This is an offline catalog comparison, not the future trusted v2 effect-verifier verdict.",
            "Unexpected findings may be valid novel findings and require human adjudication.",
            "Legacy and positive-verified coverage remain separate in by_validation_status.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Agent finding comparison",
        "",
        f"Baseline snapshot: **{report.get('baseline_snapshot_date', 'unknown')}**  ",
        f"Scope: **{report['scope']}**",
        "",
        "## Result",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Baseline findings | {summary['baseline_total']} |",
        f"| Agent submissions | {summary['agent_submissions']} |",
        f"| Matched unique | {summary['matched_unique']} |",
        f"| Missed | {summary['missed']} |",
        f"| Unexpected / possible novel | {summary['unexpected']} |",
        f"| Ambiguous | {summary['ambiguous']} |",
        f"| Duplicates | {summary['duplicates']} |",
        f"| Coverage | {summary['coverage']:.2%} |",
        f"| Comparison precision | {summary['comparison_precision']:.2%} |",
        f"| Schema errors | {summary['schema_error_count']} |",
        f"| Chains completed | {summary['chains_completed']} / {summary['chains_total']} |",
        f"| Chains partial | {summary['chains_partial']} |",
        f"| Chain completion rate | {summary['chain_completion_rate']:.2%} |",
        "",
        "## Coverage by validation status",
        "",
        "| Status | Found | Total | Coverage |",
        "| --- | ---: | ---: | ---: |",
    ]
    for status, values in report["by_validation_status"].items():
        lines.append(f"| `{status}` | {values['found']} | {values['total']} | {values['coverage']:.2%} |")

    lines.extend(
        [
            "",
            "## Chain comparison",
            "",
            "| Chain | Validation status | Result | Found nodes | Missing nodes |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for chain in report["chain_results"]:
        lines.append(
            f"| `{chain['chain_id']}` | `{chain['validation_status']}` | {chain['status']} | "
            f"{', '.join(chain['found_nodes']) or '—'} | {', '.join(chain['missing_nodes']) or '—'} |"
        )

    def add_rows(title: str, rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> None:
        lines.extend(["", f"## {title}", ""])
        if not rows:
            lines.append("None.")
            return
        lines.append("| " + " | ".join(label for label, _ in columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")
        for row in rows:
            values = []
            for _, key in columns:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                values.append(str(value).replace("|", "\\|").replace("\n", " ")[:220])
            lines.append("| " + " | ".join(values) + " |")

    add_rows("Matched findings", report["matched"], [("Agent ID", "agent_finding_id"), ("Baseline ID", "baseline_id"), ("Target", "target"), ("Basis", "match_basis")])
    add_rows("Missed findings", report["missed_findings"], [("Baseline ID", "baseline_id"), ("Target", "target"), ("Severity", "severity"), ("Class", "class"), ("Title", "title")])
    add_rows("Unexpected findings", report["unexpected_findings"], [("Agent ID", "agent_finding_id"), ("Reason", "reason"), ("Finding", "finding")])
    add_rows("Ambiguous findings", report["ambiguous_findings"], [("Agent ID", "agent_finding_id"), ("Basis", "match_basis"), ("Candidates", "candidate_ids")])
    add_rows("Duplicate findings", report["duplicate_findings"], [("Agent ID", "agent_finding_id"), ("Baseline ID", "baseline_id"), ("Target", "target")])
    lines.extend(["", "## Interpretation", "", *[f"- {note}" for note in report["notes"]], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", required=True, type=Path, help="agent JSON report")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--scope", choices=["all", "verified", "legacy"], default="all")
    parser.add_argument("--out", required=True, type=Path, help="comparison JSON output")
    parser.add_argument("--markdown-out", type=Path, help="optional readable comparison report")
    args = parser.parse_args()

    try:
        payload = json.loads(args.findings.read_text(encoding="utf-8"))
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        result = compare(payload, baseline, args.scope)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"comparison failed: {exc}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown(result), encoding="utf-8")
    summary = result["summary"]
    print(
        f"Compared {summary['agent_submissions']} submissions: "
        f"{summary['matched_unique']} matched, {summary['missed']} missed, "
        f"{summary['unexpected']} unexpected, {summary['duplicates']} duplicates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
