# Failed or non-evidentiary artifacts

The four top-level order-24 files matching
`artifacts/sat/sds_24_18_2_*.cnf` were written before the DIMACS comment-prefix
bug was fixed. They are intentionally preserved for failure provenance but do
not parse as DIMACS and are not evidence. The valid, checked order-24 formulas
are under `artifacts/sat/v24_c2c12_subcases/`.

`artifacts/runs/sat_v24_totalizer.json` records delayed raw solver outcomes
against the in-memory clauses. Its `UNSAT_UNCERTIFIED` results are also not
accepted as evidence; the order-24 census decisions use the checked subcase
proof aggregate and the independent Walsh obstruction instead.
