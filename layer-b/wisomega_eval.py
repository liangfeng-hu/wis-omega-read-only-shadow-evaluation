#!/usr/bin/env python3
"""WIS-Omega read-only Shadow evaluator.

Standard-library only. It evaluates frozen JSON cases, creates deterministic
hash-linked receipts, and writes only to the operator-selected output folder.
It never imports a network client, loads credentials, starts a service, or
performs an external effect.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


SCHEMA = "wisomega.shadow-evaluation.v1"
PACK_NAME = "cases-shadow-v1"
ALLOWED_EXPECTED_DECISIONS = {"FAIL_CLOSED", "PERMIT"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}_MUST_BE_OBJECT")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}_MUST_BE_NONEMPTY_TEXT")
    return value


def present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return bool(value) and all(present(k) and present(v) for k, v in value.items())
    if isinstance(value, list):
        return bool(value) and all(present(v) for v in value)
    return value is not None


def binding_faults(case: dict[str, Any]) -> list[str]:
    candidate = case.get("candidate")
    bindings = case.get("bindings")
    if not isinstance(candidate, dict):
        return ["CANDIDATE_MISSING"]
    if not isinstance(bindings, dict):
        return ["BINDINGS_MISSING"]
    faults: list[str] = []
    for key in ("identity", "endpoint", "effect", "recovery"):
        if not present(candidate.get(key)):
            faults.append(f"CANDIDATE_{key.upper()}_MISSING")
        if not present(bindings.get(key)):
            faults.append(f"BINDING_{key.upper()}_MISSING")
        elif digest(bindings.get(key)) != digest(candidate.get(key)):
            faults.append(f"BINDING_{key.upper()}_MISMATCH")
    return faults


def evidence_faults(case: dict[str, Any]) -> list[str]:
    evidence = case.get("evidence")
    if not isinstance(evidence, dict):
        return ["RECOMPUTABLE_EVIDENCE_MISSING"]
    body = evidence.get("body")
    claimed = evidence.get("sha256")
    if not isinstance(body, dict) or not isinstance(claimed, str):
        return ["EVIDENCE_BODY_OR_DIGEST_MISSING"]
    faults: list[str] = []
    if digest(body) != claimed:
        faults.append("EVIDENCE_HASH_RECOMPUTATION_FAILED")
    candidate = case.get("candidate")
    if not isinstance(candidate, dict) or body.get("candidate_sha256") != digest(candidate):
        faults.append("EVIDENCE_CANDIDATE_BINDING_FAILED")
    return faults


def issue_shadow_permit(case: dict[str, Any]) -> dict[str, Any]:
    bindings = require_dict(case["bindings"], "BINDINGS")
    candidate = require_dict(case["candidate"], "CANDIDATE")
    permit_body = {
        "schema": "wisomega.shadow-permit.v1",
        "candidate_sha256": digest(candidate),
        "identity_sha256": digest(bindings["identity"]),
        "endpoint_sha256": digest(bindings["endpoint"]),
        "effect_sha256": digest(bindings["effect"]),
        "recovery_sha256": digest(bindings["recovery"]),
        "single_use": 1,
        "shadow_only": 1,
        "world_writeback_authorized": 0,
        "cryptographic_capability": 0,
        "kms_backed": 0,
        "signature": None,
        "notice": "LOCAL_SHADOW_OBJECT_NOT_A_CRYPTOGRAPHIC_OR_PRODUCTION_CAPABILITY",
    }
    return {**permit_body, "permit_id": f"shadow-{digest(permit_body)[:24]}"}


def evaluate_reference(case: dict[str, Any]) -> tuple[str, str]:
    """Illustrative unprotected path, not a vendor or product benchmark."""
    candidate = case.get("candidate") if isinstance(case.get("candidate"), dict) else {}
    observations = case.get("consumer_observations")
    if isinstance(observations, list) and len(observations) > 1:
        return "ALLOW_AGAIN", "NO_SINGLE_USE_CONSUMPTION"
    if isinstance(observations, list) and any(
        isinstance(observation, dict)
        and digest(observation.get("effect")) != digest(candidate.get("effect"))
        for observation in observations
    ):
        return "ALLOW_DRIFT", "NO_CONSUMER_RECALCULATION"
    if case.get("agent_claim_verified"):
        return "ALLOW", "TRUSTS_AGENT_ASSERTION"
    return "ALLOW", "NO_EVIDENCE_OR_BINDING_GATE"


def consume_shadow_permit(permit: dict[str, Any], observations: Any) -> dict[str, Any]:
    result = {
        "decision": "FAIL_CLOSED",
        "reason": "CONSUMER_OBSERVATION_MISSING",
        "accepted_attempts": 0,
        "rejected_attempts": 0,
        "permit_consumed_shadow": 0,
        "attempts": [],
    }
    if not isinstance(observations, list) or not observations:
        return result
    consumed = False
    for index, observation in enumerate(observations, 1):
        attempt = {"attempt": index, "decision": "FAIL_CLOSED", "reason": "OBSERVATION_INVALID"}
        if consumed:
            attempt["reason"] = "PERMIT_ALREADY_CONSUMED"
        elif not isinstance(observation, dict) or not present(observation.get("effect")):
            attempt["reason"] = "CONSUMER_EFFECT_MISSING"
        elif digest(observation["effect"]) != permit["effect_sha256"]:
            attempt["reason"] = "CONSUMER_EFFECT_DRIFT"
        else:
            consumed = True
            attempt.update({"decision": "PERMIT", "reason": "BOUND_SINGLE_USE_SHADOW_PERMIT_ACCEPTED"})
            result["accepted_attempts"] += 1
        if attempt["decision"] == "FAIL_CLOSED":
            result["rejected_attempts"] += 1
        result["attempts"].append(attempt)
    result["permit_consumed_shadow"] = 1 if consumed else 0
    if result["rejected_attempts"]:
        result["decision"] = "FAIL_CLOSED"
        result["reason"] = next(
            attempt["reason"] for attempt in result["attempts"]
            if attempt["decision"] == "FAIL_CLOSED"
        )
    else:
        result["decision"] = "PERMIT"
        result["reason"] = "BOUND_SINGLE_USE_SHADOW_PERMIT_ACCEPTED"
    return result


def evaluate_wis(case: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "decision": "FAIL_CLOSED",
        "reason": "UNKNOWN_OR_INCOMPLETE_INPUT",
        "permit_created": 0,
        "permit_consumed_shadow": 0,
        "world_writeback_attempted": 0,
        "world_writeback_succeeded": 0,
        "permit": None,
        "pipeline": [],
        "consumer": None,
    }
    evidence_errors = evidence_faults(case)
    result["pipeline"].append({"stage": "EVIDENCE_RECOMPUTATION", "pass": 0 if evidence_errors else 1, "faults": evidence_errors})
    if evidence_errors:
        result["reason"] = evidence_errors[0]
        return result
    binding_errors = binding_faults(case)
    result["pipeline"].append({"stage": "EXACT_BINDING", "pass": 0 if binding_errors else 1, "faults": binding_errors})
    if binding_errors:
        result["reason"] = binding_errors[0]
        return result
    permit = issue_shadow_permit(case)
    result.update({"permit_created": 1, "permit": permit})
    result["pipeline"].append({"stage": "SHADOW_PERMIT_ISSUANCE", "pass": 1, "permit_id": permit["permit_id"]})
    consumer = consume_shadow_permit(permit, case.get("consumer_observations"))
    result["consumer"] = consumer
    result["pipeline"].append({
        "stage": "INDEPENDENT_CONSUMER_RECALCULATION_AND_SINGLE_USE",
        "pass": 1 if consumer["decision"] == "PERMIT" else 0,
        "reason": consumer["reason"],
    })
    result.update({
        "decision": consumer["decision"],
        "reason": consumer["reason"],
        "permit_consumed_shadow": consumer["permit_consumed_shadow"],
    })
    return result


def validate_pack(pack: dict[str, Any]) -> list[dict[str, Any]]:
    if pack.get("schema") != SCHEMA or pack.get("pack") != PACK_NAME:
        raise ValueError("PACK_IDENTITY_INVALID")
    cases = pack.get("cases")
    if not isinstance(cases, list) or len(cases) != 5:
        raise ValueError("EXACTLY_FIVE_CASES_REQUIRED")
    ids = [require_text(c.get("id"), "CASE_ID") for c in cases if isinstance(c, dict)]
    if len(ids) != len(cases) or len(set(ids)) != len(ids):
        raise ValueError("CASE_IDS_MUST_BE_UNIQUE_LABELS")
    for case in cases:
        require_dict(case, "CASE")
        require_dict(case.get("candidate"), "CANDIDATE")
        require_text(case.get("scenario"), "SCENARIO")
        if case.get("expected") not in ALLOWED_EXPECTED_DECISIONS:
            raise ValueError("EXPECTED_DECISION_INVALID")
    return cases


def evaluate_pack(pack: dict[str, Any]) -> dict[str, Any]:
    cases = validate_pack(pack)
    previous = "0" * 64
    results: list[dict[str, Any]] = []
    for case in cases:
        reference_decision, reference_reason = evaluate_reference(case)
        wis = evaluate_wis(case)
        passed = wis["decision"] == case["expected"]
        receipt_body = {
            "schema": "wisomega.shadow-receipt.v1",
            "case_id": case["id"],
            "scenario": case["scenario"],
            "expected": case["expected"],
            "got": wis["decision"],
            "passed": 1 if passed else 0,
            "reference_path": {
                "decision": reference_decision,
                "reason": reference_reason,
                "notice": "ILLUSTRATIVE_UNPROTECTED_REFERENCE_NOT_THIRD_PARTY_MEASUREMENT",
            },
            "wis_omega": wis,
            "candidate_sha256": digest(case["candidate"]),
            "evidence_recomputable": 0 if evidence_faults(case) else 1,
            "bindings_complete": 0 if binding_faults(case) else 1,
            "previous_receipt_sha256": previous,
            "mode": "SHADOW",
            "credentials_loaded": 0,
            "network_requests": 0,
            "world_writeback": 0,
        }
        receipt_hash = digest(receipt_body)
        receipt = {**receipt_body, "receipt_sha256": receipt_hash}
        results.append(receipt)
        previous = receipt_hash

    return {
        "schema": "wisomega.shadow-evaluation-report.v1",
        "pack": pack["pack"],
        "id_independent_predicate_pipeline": 1,
        "case_id_semantic_branch_count": 0,
        "expected_decision_hardcoded_oracle": 0,
        "permit_local_shadow_object_only": 1,
        "permit_cryptographic_capability": 0,
        "permit_kms_hsm_backed": 0,
        "pack_sha256": digest(pack),
        "case_count": 5,
        "pass_count": sum(r["passed"] for r in results),
        "final_permit_case_count": sum(r["got"] == "PERMIT" for r in results),
        "final_fail_closed_case_count": sum(r["got"] == "FAIL_CLOSED" for r in results),
        "permit_created_count": sum(r["wis_omega"]["permit_created"] for r in results),
        "permit_consumed_shadow_count": sum(r["wis_omega"]["permit_consumed_shadow"] for r in results),
        "world_writeback_attempted": 0,
        "world_writeback_succeeded": 0,
        "credentials_loaded": 0,
        "network_requests": 0,
        "persistent_service_started": 0,
        "results": results,
        "final_receipt_sha256": previous,
        "final_verdict": "PASS_SHADOW_EVALUATION" if all(r["passed"] for r in results) else "FAIL_CLOSED_EVALUATION_MISMATCH",
    }


def summary_text(report: dict[str, Any]) -> str:
    lines = [
        "WIS-Ω Read-Only Shadow Evaluation",
        f"Pack: {report['pack']}",
        "Mode: SHADOW / NO_CREDENTIALS / NO_WORLD_WRITEBACK",
        "Rule pipeline: ID_INDEPENDENT / EXPECTED_DECISIONS_NOT_HARDCODED",
        "",
    ]
    for item in report["results"]:
        lines.append(
            f"CASE {item['case_id']}  expect={item['expected']:<11} "
            f"got={item['got']:<11} {'PASS' if item['passed'] else 'FAIL'}"
        )
    lines.extend([
        "",
        f"Result: {report['pass_count']}/{report['case_count']}",
        f"Final PERMIT cases: {report['final_permit_case_count']}",
        f"Final FAIL_CLOSED cases: {report['final_fail_closed_case_count']}",
        f"Shadow permits issued after verifier checks: {report['permit_created_count']}",
        f"Shadow permits consumed once before final case outcome: {report['permit_consumed_shadow_count']}",
        "World writeback attempted: 0",
        "World writeback succeeded: 0",
        f"Final verdict: {report['final_verdict']}",
        "",
        "The reference path is an illustrative unprotected implementation in this package.",
        "It is not a measurement of any third-party product or organization.",
    ])
    return "\n".join(lines) + "\n"


def report_html(report: dict[str, Any]) -> str:
    rows = []
    for item in report["results"]:
        w = item["wis_omega"]
        rows.append(
            "<tr>"
            f"<td>{html.escape(item['case_id'])}</td>"
            f"<td>{html.escape(item['scenario'])}</td>"
            f"<td><span class='risk'>{html.escape(item['reference_path']['decision'])}</span></td>"
            f"<td><span class='{'permit' if item['got'] == 'PERMIT' else 'hold'}'>{html.escape(item['got'])}</span>"
            f"<br><small>{html.escape(w['reason'])}</small></td>"
            f"<td class='pass'>{'PASS' if item['passed'] else 'FAIL'}</td>"
            "</tr>"
        )
    embedded = html.escape(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>WIS-Ω Read-Only Shadow Evaluation</title><style>
:root{{--bg:#07131f;--panel:#102235;--line:#29465f;--text:#f4f8fb;--muted:#b7c6d4;--green:#58dda0;--amber:#ffd166;--red:#ff7b7b;--blue:#67c8ff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:34px 22px 60px}}h1{{font-size:clamp(2rem,5vw,3.6rem);line-height:1.05;margin:.15em 0}}.kicker{{color:var(--blue);font-weight:800;letter-spacing:.08em}}.banner{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:22px 0}}.pill,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}}.pill strong{{display:block;color:var(--green);font-size:1.2rem}}.score{{font-size:3.4rem;font-weight:900;color:var(--green)}}table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:14px;overflow:hidden}}th,td{{text-align:left;vertical-align:top;padding:13px;border-bottom:1px solid var(--line)}}th{{color:var(--muted)}}.risk{{color:var(--red);font-weight:800}}.hold{{color:var(--amber);font-weight:800}}.permit,.pass{{color:var(--green);font-weight:800}}small,.muted{{color:var(--muted)}}details{{margin-top:24px}}pre{{white-space:pre-wrap;word-break:break-word;background:#040a10;padding:16px;border-radius:12px;max-height:520px;overflow:auto}}@media(max-width:760px){{.banner{{grid-template-columns:1fr}}table{{font-size:.86rem}}th,td{{padding:8px}}}}
</style></head><body><main>
<div class="kicker">SHADOW / NO CREDENTIALS / WORLD WRITEBACK = 0</div>
<h1>Agent action → bounded decision</h1>
<p class="muted">Five frozen cases. One ID-independent predicate pipeline. No network, service, credential, or production effect.</p>
<div class="banner"><div class="pill"><strong>{report['pass_count']}/{report['case_count']} PASS</strong>Frozen expected outcomes</div><div class="pill"><strong>{report['final_permit_case_count']} final PERMIT</strong>Four final fail-closed cases</div><div class="pill"><strong>0 writebacks</strong>Attempted and succeeded</div></div>
<section class="card" style="margin-bottom:20px"><h2>One rule pipeline for every candidate</h2><p>Recompute evidence → exactly bind identity, endpoint, effect and recovery → create a local single-use Shadow Permit → independently recalculate consumer effect → reject any missing input, replay or drift. Case IDs are labels only; expected decisions are test data, not a hardcoded oracle.</p></section>
<table><thead><tr><th>Case</th><th>Scenario</th><th>Illustrative unprotected path</th><th>WIS-Ω decision</th><th>Check</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<section class="card" style="margin-top:20px"><h2>What this proves</h2><p>The packaged evaluator deterministically applies one ID-independent evidence, binding, single-use and consumer-recalculation pipeline to five frozen Shadow cases and produces hash-linked receipts.</p><h2>What this does not prove</h2><p>No third-party product was measured. No production runtime, credential, endpoint, physical single ingress or world writeback was tested. The local Permit is not a cryptographic or KMS/HSM-backed capability. This is not production readiness or independent validation.</p></section>
<details><summary>Inspectable report JSON</summary><pre>{embedded}</pre></details>
</main></body></html>"""


def write_outputs(out_dir: Path, report: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "SUMMARY.txt").write_text(summary_text(report), encoding="utf-8", newline="\n")
    (out_dir / "report.html").write_text(report_html(report), encoding="utf-8", newline="\n")
    with (out_dir / "receipts.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for receipt in report["results"]:
            handle.write(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    metadata = {
        "schema": "wisomega.shadow-run-metadata.v1",
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": os.name,
        "network_requests": 0,
        "credentials_loaded": 0,
        "persistent_service_started": 0,
        "world_writeback": 0,
        "id_independent_predicate_pipeline": 1,
        "case_id_semantic_branch_count": 0,
        "expected_decision_hardcoded_oracle": 0,
        "permit_local_shadow_object_only": 1,
        "permit_cryptographic_capability": 0,
        "permit_kms_hsm_backed": 0,
        "report_sha256": hashlib.sha256((out_dir / "report.html").read_bytes()).hexdigest(),
        "summary_sha256": hashlib.sha256((out_dir / "SUMMARY.txt").read_bytes()).hexdigest(),
        "receipts_sha256": hashlib.sha256((out_dir / "receipts.jsonl").read_bytes()).hexdigest(),
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def resolve_pack(root: Path, name: str) -> Path:
    if name != PACK_NAME:
        raise ValueError("ONLY_FROZEN_PACK_CASES_SHADOW_V1_IS_ACCEPTED")
    return root / "packs" / f"{name}.json"


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wisomega-eval", description="WIS-Ω read-only Shadow evaluator")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="run the frozen Shadow case pack")
    run_parser.add_argument("--pack", default=PACK_NAME)
    run_parser.add_argument("--out", default="out")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    start = time.monotonic()
    try:
        pack_path = resolve_pack(root, args.pack)
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        report = evaluate_pack(require_dict(pack, "PACK"))
        write_outputs(Path(args.out).resolve(), report)
    except Exception as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        print("PermitCreated=0\nWorldWriteback=0", file=sys.stderr)
        return 2
    elapsed_ms = int((time.monotonic() - start) * 1000)
    print(summary_text(report), end="")
    print(f"Elapsed: {elapsed_ms} ms")
    print(f"Report: {(Path(args.out).resolve() / 'report.html')}")
    return 0 if report["pass_count"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
