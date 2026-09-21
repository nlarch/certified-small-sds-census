# v1.1.0 — Revised manuscript and solver-free order-36 proof

This release publishes the September 21, 2026 revision of *Two Small-Order
Classification Theorems for Signed Difference Sets* and its corresponding
reproducibility package.

## Main changes

- The order-32 theorem classifies signed `(32,20,4)` difference sets in every
  abelian group of order 32: existence holds exactly in the six noncyclic
  groups.
- The order-36 theorem is now self-contained: no abelian group of order 36
  admits a signed `(36,29,4)` difference set.
- An empty `C18` quotient system excludes `C36` and `C2 x C18`; an empty
  `C2 x C3^2` quotient system excludes `C3 x C12`; and a direct solver-free
  enumeration excludes `C6 x C6` after checking all 36 marginal pairs and
  16,964,640 candidates.
- The six positive order-32 cases are printed explicitly and remain available
  as machine-readable witnesses.
- The manuscript now gives fuller completeness arguments, claim-by-claim
  verification information, reproducibility limits, and a detailed disclosure
  of the substantive use of OpenAI Codex.
- Fabian Arévalo's separately authored review and the code adapted from it are
  attributed with their stated scope and limitations. Daniel M. Gordon's
  discussion of prior art and encouragement to submit are not presented as
  formal verification, acceptance, or a guarantee of novelty.

## Verification for this release

The untouched September 21 transfer package passed its 63-file integrity
manifest and both deterministic validators for all 16 witnesses. In a separate
working copy, the full quotient suite and the direct `C6 x C6` enumeration were
rerun with Python 3.12.14 and NumPy 2.0.2; all checks passed. The direct search
examined 16,964,640 candidates and found no solution.

The 57 historical CNF/DRAT proofs supporting other entries in the broader
68-case census were not replayed during this release preparation because the
large proof payload was absent from the transfer ZIP. Their August 12, 2026
clean-environment audit remains preserved in version 1.0 and the Zenodo archive.
This release does not relabel that historical audit as a fresh replay.

## Release assets

- `two_small_order_classifications.pdf` — revised manuscript;
- `ESM_1_reproducibility.zip` — exact programs, witnesses, outputs,
  instructions, and integrity manifest for the two classification theorems;
- `SHA256SUMS_v1.1.0.txt` — checksums for the two assets above.

Version 1.0 and the Zenodo CNF/DRAT archive remain immutable historical
releases. The ten cases in the two principal theorems are supported as new by
the documented prior-art search, but this is not a guarantee of novelty. The
other 58 cases are described as independent replications.
