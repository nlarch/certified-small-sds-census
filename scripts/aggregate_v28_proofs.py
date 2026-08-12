#!/usr/bin/env python3
"""Audit all twelve order-28 checked proof subcases."""

import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "artifacts" / "sat" / "v28_subcases"
OUTPUT = ROOT / "artifacts" / "runs" / "v28_certified_sat.json"

def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    reports=[]
    for case in range(3):
        for pattern in range(4):
            path=DIRECTORY/f"case_{case}_pattern_{pattern}.json"
            r=json.loads(path.read_text())
            assert r["case_index"]==case and r["pattern_index"]==pattern and r["result"]=="UNSAT" and r["checker"]["verified"]
            for node in (r["formula"],r["proof"]): assert sha256(ROOT/node["path"])==node["sha256"]
            assert sha256(ROOT/r["checker"]["output_path"])==r["checker"]["output_sha256"]
            reports.append(r)
    results=[]
    for case in range(3):
        subset=[r for r in reports if r["case_index"]==case]
        results.append({
            "instance":subset[0]["instance"],
            "result":"NONEXISTENT_BY_CHECKED_SAT_PROOFS",
            "patterns":[r["pattern"] for r in subset],
            "subcases":[{"pattern_index":r["pattern_index"],"formula":r["formula"],"proof":r["proof"],"checker":r["checker"],"solve_seconds":r["solve_seconds"]} for r in subset],
        })
    document={
        "schema":"v28-certified-nonexistence-v1",
        "completed_at_utc":max(r["completed_at_utc"] for r in reports),
        "result_count":3,
        "all_twelve_proofs_checked":True,
        "completeness_argument":[
            "For C2 x C14, the real-character quotient is C2^2 with four cosets of size seven.",
            "The principal character is normalized positive and each of three nonprincipal real characters is independently plus or minus sqrt(k-lambda).",
            "Inverse Walsh transformation leaves exactly four bounded integral cell-sum patterns for each parameter set; all are recorded.",
            "Each pattern CNF encodes the exact coefficient composition and every full autocorrelation equation. All twelve UNSAT proofs pass independent forward DRAT checking."
        ],
        "results":results,
    }
    OUTPUT.write_text(json.dumps(document,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"output":str(OUTPUT.relative_to(ROOT)),"sha256":sha256(OUTPUT),"results":[x["instance"] for x in results]},indent=2))

if __name__=="__main__": main()
