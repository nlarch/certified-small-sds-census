# Version 1.1.0 release-candidate verification

**Date:** 2026-09-21  
**Repository base:** public `main` at
`9b6c261dce8e36621fdf472137d5aff447b48af9`  
**Environment:** Python 3.12.14, NumPy 2.0.2, python-sat 1.9.dev13,
six 1.17.0

## Checks executed from the release candidate

- Validator unit tests: **PASS** (3 tests).
- Final census audit: **PASS** (68 entries; 16 witnesses validated by both
  project validators; integrity of 57 stored SAT/DRAT subcases checked).
- Order-27 mixed-radix quotient verification: **PASS** for all six recorded
  cases.
- Order-32 quotient verification: **PASS** for all four recorded cases.
- Combined order-36 quotient verification: **PASS**.
- Direct `C18` quotient reconstruction: **PASS**; 7,560 sum-and-norm
  candidates and zero solutions; runtime 1.295 seconds; generated artifact
  SHA-256 `78fe3e1d3d7ded6e90c79aa59148b5f6a8ec22d9c82966229a0572078da125bf`.
- Direct solver-free `C6 x C6` enumeration: **PASS**; 36 marginal pairs,
  16,964,640 candidates, and zero solutions; runtime 103.216 seconds;
  generated artifact SHA-256
  `b021f9a3f0d505d1c0566915f3cf045965b4e3faaf714fa27312a312afe04e62`.

The frozen La Jolla source required by the validator tests was checked out at
the documented commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e` and remained outside the Git
release tree.

## Frozen release-candidate files

- `paper/two_small_order_classifications.tex`:
  `cc828e29f2e2c96681ac81906e4ff04e56831c5ee2e1328c33726c1ee60811c4`
- `output/pdf/two_small_order_classifications.pdf`:
  `fdc01c046fa6bf555d8d5db3c086530fe63c8377540d92daf10ec0e9690abff5`
- `AI_USE.md`:
  `08d5b9c96b0fff3b52db57af676b788fd8bb46b3dc969ce63ce2198db78601fe`

## Boundary

The census audit checked stored formula, proof, checker-output, and manifest
integrity. It did not replay the 57 historical DRAT proofs. Their prior
clean-environment replay remains a version 1.0 historical record. The two
principal theorems in the revised manuscript rely on explicit constructions
and the solver-free enumerations rerun above.

No GitHub push, tag publication, release publication, arXiv submission, or
journal submission was performed during this check.
