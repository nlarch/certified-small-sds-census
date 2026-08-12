#!/usr/bin/env python3
"""Freeze the dated entry-by-entry novelty and independent-replication screen."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "artifacts" / "census" / "current_census.json"
PRIOR = ROOT / "sources" / "novelty-farev-matematica"
VALUES = PRIOR / "conjectures" / "signed-difference-sets" / "data" / "values.csv"
THEORY = PRIOR / "conjectures" / "signed-difference-sets" / "data" / "theory_closures.csv"
OUTPUT = ROOT / "artifacts" / "novelty" / "novelty_screen_2026-08-12.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    census = json.loads(CENSUS.read_text())
    prior = {}
    for row in csv.DictReader(VALUES.open()):
        prior[row["name"]] = {
            "decision": row["decision"],
            "method": row["method"],
            "source_path": str(VALUES.relative_to(ROOT)),
        }
    for row in csv.DictReader(THEORY.open()):
        prior.setdefault(
            row["name"],
            {
                "decision": "NONEXIST",
                "method": "character criterion",
                "criterion": row["criterion"],
                "source_path": str(THEORY.relative_to(ROOT)),
            },
        )

    rows = []
    disagreements = []
    for entry in census["entries"]:
        project_decision = "EXIST" if entry["result"] == "EXISTS" else "NONEXIST"
        row = {
            "instance": entry["name"],
            "project_decision": project_decision,
            "project_evidence_path": entry["evidence_path"],
        }
        if entry["name"] in prior:
            comparison = prior[entry["name"]]
            row.update(
                {
                    "novelty_class": "INDEPENDENT_REPLICATION_OF_PRIOR_PUBLIC_DECISION",
                    "contribution_level": "INDEPENDENTLY_REPLICATED",
                    "prior_public_decision": comparison,
                }
            )
            if comparison["decision"] != project_decision:
                disagreements.append(entry["name"])
        else:
            row.update(
                {
                    "novelty_class": "NOVELTY_SUPPORTED_NO_PRIOR_EXACT_RESOLUTION_FOUND",
                    "contribution_level": "NOVELTY_SUPPORTED_RESULT",
                    "prior_public_decision": None,
                }
            )
        rows.append(row)
    assert not disagreements

    triples = sorted({(entry["v"], entry["k"], entry["lambda"]) for entry in census["entries"]})
    prior_commit = subprocess.check_output(
        ["git", "-C", str(PRIOR), "rev-parse", "HEAD"], text=True
    ).strip()
    assert prior_commit == "a6a0805686e97f4a05bd7d9870d6e1648186afaf"
    counts = {
        "independently_replicated": sum(
            row["contribution_level"] == "INDEPENDENTLY_REPLICATED" for row in rows
        ),
        "novelty_supported": sum(
            row["contribution_level"] == "NOVELTY_SUPPORTED_RESULT" for row in rows
        ),
    }
    assert counts == {"independently_replicated": 58, "novelty_supported": 10}

    document = {
        "schema": "certified-small-sds-novelty-screen-v1",
        "as_of": "2026-08-12",
        "scope": "Every one of the 68 frozen Open entries with v <= 36",
        "important_limitation": "Search and citation indexes are not proofs of novelty; novelty-supported means no prior exact resolution was found in the documented screen.",
        "counts": counts,
        "prior_exact_result_source": {
            "repository": "https://github.com/farev/Matematica",
            "commit": prior_commit,
            "first_relevant_commits": [
                {
                    "commit": "06e07baa2e0432b9c82a23e915e52f8dc54727f3",
                    "timestamp_utc": "2026-08-09T12:31:09Z",
                    "scope": "character-criterion closures",
                },
                {
                    "commit": "84237919b028f143e2f2212b4e863e99ea55aca7",
                    "timestamp_utc": "2026-08-09T12:36:37Z",
                    "scope": "batch decisions including exact small entries",
                },
            ],
            "values_path": str(VALUES.relative_to(ROOT)),
            "values_sha256": sha256(VALUES),
            "theory_path": str(THEORY.relative_to(ROOT)),
            "theory_sha256": sha256(THEORY),
            "overlap_count": counts["independently_replicated"],
            "decision_disagreements": disagreements,
        },
        "frozen_repository_currency": {
            "repository": "https://github.com/dmgordo/signed-difference-sets",
            "observed_main_commit": "e3bf810c5ee6826cf5030f983f6adf23b0ffd20e",
            "observed_branches": ["main"],
            "observed_issue_count": 0,
            "observed_pull_request_count": 0,
            "last_push_utc": "2026-04-24T17:51:16Z",
            "observation_method": "git ls-remote plus GitHub public API",
        },
        "literature_screen": {
            "foundational_doi": "10.1007/s10623-022-01171-8",
            "followup_doi": "10.1007/s10623-024-01389-8",
            "openalex_observation": "OpenAlex returned one citing work for the foundational paper (the He-Chen-Ge follow-up) and zero citing works for that follow-up.",
            "followup_source_check": "The complete arXiv source of 2306.05631 was searched for the target orders 27, 32, and 36; none occurred as parameter results.",
        },
        "exact_web_queries": {
            "query_template": "exact phrase 'signed difference set' plus exact '(v,k,lambda)'",
            "parameter_triples": triples,
            "result": "No exact-resolution hits for any of the 30 triples; unrelated false positives were discarded.",
        },
        "global_github_code_queries_for_prior_absent_families": [
            {"query": "SDS(32,20,4", "result_count": 0},
            {"query": "SDS(36,29,4", "result_count": 0},
        ],
        "adversarial_screen": {
            "strongest_objection": "An exhaustive negative result might omit a symmetry orbit or use a quotient action that does not lift.",
            "decisive_tests": [
                "The v=32 verifier independently reconstructs each affine orbit cover and fully refines every normalized-parent survivor; an initially unjustified second quotient was detected and removed before acceptance.",
                "The v=36 C2xC18 and C3xC12 claims have independent quotient enumerations; the C6xC6 claim uses the complete unique quotient orbit plus an independently checked DRAT proof.",
                "All six novelty-supported existence results are explicit vectors accepted by both full unsymmetrized validators.",
            ],
            "equivalence_check": "Global sign, translation, inversion, and group automorphisms preserve the exact named (v,k,lambda,G) entry, so they cannot move a result to a different frozen entry; all final validators ignore discovery normalization and check the full equation.",
        },
        "entries": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "counts": counts,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
