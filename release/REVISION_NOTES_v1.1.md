# Revision notes for version 1.1

This revision incorporates the specialist feedback received from Daniel M.
Gordon and Fabian Arévalo after version 1.0.

## Mathematical changes

- The order-36 statement is now a single self-contained theorem: no abelian
  group of order 36 admits a signed `(36,29,4)` difference set.
- A new standard-library exhaustion proves that the necessary `C18` quotient
  system is empty. This excludes `C36` and `C2 x C18` simultaneously.
- A new solver-free direct search, adapted with attribution from Arévalo's
  MIT-licensed independent review code, checks all 36 marginal pairs for
  `C6 x C6`. It reproduces 16,964,640 candidates and zero solutions.
- The existing CNF/DRAT proof is retained as an independent supplementary
  certificate rather than the main proof of the `C6 x C6` case.

## Exposition changes

- The paper has been rewritten as a standalone LaTeX manuscript.
- The quotient projection lemma now cites Gordon's Lemma 5.2.
- Search spaces, pruning conditions, refinement rules, exact counts, and
  completeness arguments are stated in the body of the paper.
- The six order-32 constructions are printed explicitly in an appendix;
  cryptographic hashes are no longer part of the mathematical exposition.
- The scope of the independent replication and its AI-use disclosure are
  stated explicitly.

## Data changes

- The `SDS(25,12,1,[5,5])` witness now uses the same
  `group_invariant_factors` field as the other witness files.
- `release/gordon_v32_20_4_noncyclic_entries.json` contains the six positive
  order-32 entries in the La Jolla repository's `[P,N]` format.
- NumPy 2.0.2 is recorded as a dependency for the batched direct search.

Version 1.0 and its Zenodo proof archive remain immutable historical releases.
