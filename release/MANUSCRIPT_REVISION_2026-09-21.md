# Manuscript revision — September 21, 2026

Daniel Gordon recommended Ming Ming Tan's *Character and Multiplier
Obstructions for Circulant Weighing Matrices*,
[arXiv:2608.18468v2](https://arxiv.org/abs/2608.18468v2), as an example of
explicit AI attribution accompanied by exact verification. This revision
adapts the reporting approach to this project's documented workflow; it does
not import Tan's results or claim his author's verification history.

## Changes

- Expanded the manuscript's AI disclosure to distinguish research proposals,
  implementation, experiment execution, evidence organization, and drafting.
- Avoided assigning an unrecorded historical model version or asserting a
  complete line-by-line human audit.
- Added a claim-by-claim verification table, the missing combined-quotient
  command, exact-arithmetic bounds, and computational verification limits.
- Clarified that the local C6 x C6 program derives from Arévalo's review and
  is not an additional independent implementation.
- Distinguished the normalized local C3 x C12 check from the external review's
  all-marginal-pairs check, with the justification for normalization stated.
- Corrected the generic enumeration description to include squared-norm
  feasibility bounds, and limited the abstract's replication claim to the
  two theorems covered by the external review.
- Distinguished this revised manuscript from the published version 1.0 and
  its Zenodo trace archive; synchronized `AI_USE.md`.

## Verification performed for this revision

All five reruns passed using the existing Python 3.9.6 environment:

1. Census audit: 68 entries, 16 witnesses checked by both validators, and
   integrity checks of all 57 stored CNF/DRAT subcases.
2. Order-32 quotient reconstruction and full refinements.
3. Combined quotient verification, including the 420-candidate normalized
   C3 x C12 obstruction.
4. C18 reconstruction: 7,560 sum-and-norm candidates, zero solutions.
5. C6 x C6 direct enumeration: 36 marginal pairs, 16,964,640 candidates,
   zero solutions (approximately 78 seconds in this run).

The six constructions printed in the LaTeX appendix were separately parsed,
compared with their JSON vectors, and checked by both validators: all passed.
The PDF was rebuilt with Tectonic and its rendered pages inspected.

The machine-readable run summary and logs are under
`artifacts/audit/manuscript_revision_2026-09-21.json` and the adjacent
`manuscript_revision_2026-09-21/` directory. Fresh C18 and C6 x C6 outputs
were written there so the earlier evidence files remain intact.

The 57 DRAT proofs were not replayed: this rerun checked their stored files,
hashes, and prior checker results. It is not a new formal-proof audit or a
complete independent review of the mathematical arguments.

## Deliverable state

The current manuscript is `paper/two_small_order_classifications.tex`, with
its PDF in `output/pdf/two_small_order_classifications.pdf`. The earlier
Markdown draft remains historical. Previously built archives in `dist/`
were not rebuilt and do not contain this September 21 revision. No email,
GitHub push, release, arXiv submission, or journal submission was made as part
of this revision.
