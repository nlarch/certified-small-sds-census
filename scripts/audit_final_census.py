#!/usr/bin/env python3
"""Fast integrity and dual-validation audit of the completed 68-entry census."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sds.model import parse_name  # noqa: E402
from sds.validator_independent import validate as independent_validate  # noqa: E402
from sds.validator_reference import validate as reference_validate  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main() -> None:
    census_path = ROOT / "artifacts" / "census" / "current_census.json"
    census = json.loads(census_path.read_text())
    assert census["target_count"] == 68
    assert census["resolved_count"] == 68
    assert census["unresolved_count"] == 0
    assert census["complete"]
    assert len(census["entries"]) == 68
    assert len({entry["name"] for entry in census["entries"]}) == 68

    evidence_paths = set()
    for entry in census["entries"]:
        evidence = ROOT / entry["evidence_path"]
        assert evidence.exists(), evidence
        assert sha256(evidence) == entry["evidence_sha256"], evidence
        evidence_paths.add(evidence)

    witnesses = sorted((ROOT / "artifacts" / "witnesses").glob("*.json"))
    assert len(witnesses) == 16
    for path in witnesses:
        document = json.loads(path.read_text())
        instance = parse_name(document["instance"])
        vector = tuple(document["coefficient_vector"])
        reference = reference_validate(instance, vector)
        independent = independent_validate(instance, vector)
        assert reference["valid"] and independent["valid"], path
        assert reference["support"] == independent["support"] == instance.k
        assert reference["autocorrelation"] == independent["autocorrelation"]

    proof_subcases = 0
    for evidence in evidence_paths:
        if not evidence.name.endswith(".json"):
            continue
        document = json.loads(evidence.read_text())
        for node in walk(document):
            if not isinstance(node, dict):
                continue
            if not all(key in node for key in ("formula", "proof", "checker")):
                continue
            if not isinstance(node["formula"], dict) or "path" not in node["formula"]:
                continue
            assert node["checker"]["verified"]
            for section in ("formula", "proof"):
                path = ROOT / node[section]["path"]
                assert path.exists() and sha256(path) == node[section]["sha256"], path
            checker_output = ROOT / node["checker"]["output_path"]
            assert checker_output.exists()
            assert sha256(checker_output) == node["checker"]["output_sha256"]
            assert "s VERIFIED" in checker_output.read_text()
            proof_subcases += 1
    assert proof_subcases == 57

    novelty_path = ROOT / "artifacts" / "novelty" / "novelty_screen_2026-08-12.json"
    novelty = json.loads(novelty_path.read_text())
    assert novelty["counts"] == {"independently_replicated": 58, "novelty_supported": 10}
    assert len(novelty["entries"]) == 68
    assert {entry["instance"] for entry in novelty["entries"]} == {
        entry["name"] for entry in census["entries"]
    }

    outcome_counts = Counter(
        "EXISTS" if entry["result"] == "EXISTS" else "NONEXISTENT"
        for entry in census["entries"]
    )
    assert outcome_counts == {"EXISTS": 16, "NONEXISTENT": 52}
    report = {
        "schema": "certified-small-sds-final-audit-v1",
        "as_of": "2026-08-12",
        "status": "PASS",
        "census_path": str(census_path.relative_to(ROOT)),
        "census_sha256": sha256(census_path),
        "census_entries": len(census["entries"]),
        "outcomes": outcome_counts,
        "standalone_witnesses_dual_validated": len(witnesses),
        "checked_sat_subcases_integrity_audited": proof_subcases,
        "novelty_path": str(novelty_path.relative_to(ROOT)),
        "novelty_sha256": sha256(novelty_path),
        "novelty_supported": novelty["counts"]["novelty_supported"],
        "independently_replicated": novelty["counts"]["independently_replicated"],
    }
    output = ROOT / "artifacts" / "audit" / "final_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**report, "output": str(output.relative_to(ROOT)), "output_sha256": sha256(output)}, indent=2))


if __name__ == "__main__":
    main()
