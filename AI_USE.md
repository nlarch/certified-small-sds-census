# Statement on the use of artificial intelligence

OpenAI Codex was used extensively as a computational research and
software-engineering assistant in this project. Its roles included:

- proposing candidate search, character, quotient, and SAT strategies;
- writing and revising source code, tests, validators, documentation, and the
  first draft of the accompanying note;
- executing local experiments and organizing their outputs;
- checking internal consistency, provenance fields, and cryptographic hashes;
- helping structure the release and reproducibility materials.

No language-model output is treated as mathematical evidence. Positive claims
are accepted only when an explicit coefficient vector passes two structurally
independent deterministic validators that recompute the full defining
equation. Negative claims are accepted only when supported by a reconstructible
complete enumeration or an exact CNF/DRAT certificate checked by independently
compiled proof-checking software. Search failure, model judgment, and unchecked
solver output are excluded from the final census.

The human author selected the research objective, authorized the computational
work, reviewed the framing, and remains responsible for the mathematical
claims and for any public release. AI assistance should be disclosed in any
derived manuscript, preprint, repository release, or submission, subject also
to the policy of the receiving venue.

## Attribution and verification limits (September 21, 2026 revision)

The AI contribution extended to proposing research approaches and implementing
the computations, not only to editing prose. The project record identifies
OpenAI Codex but does not establish a particular model version for every
historical step; the manuscript does not assign one retrospectively.

The two principal classification theorems now use explicit constructions and
solver-free finite enumerations. The broader census also uses checked DRAT
certificates. Checking stored proof hashes and earlier checker outputs is an
integrity audit, not a fresh replay of those proofs.

Fabian Arévalo's external review independently reproduced the original
witness and quotient calculations. The local direct C6 x C6 program was
subsequently adapted from his review code and must not be counted as another
independent implementation. His review disclosed substantial AI assistance;
it did not audit the project's CNF encoder or the entire Zenodo archive.

Deterministic reruns and independent implementations provide evidence with
the scope described in the manuscript. They do not establish a formal
verification of the software stack or a separate line-by-line human audit of
every mathematical argument and program. No such human audit is asserted.
