# Certified Small SDS - v1.0 lightweight verification package

This package accompanies *Two Small-Order Classification Theorems for Signed
Difference Sets*. It contains the article, all 16 explicit witnesses from the
completed small-order census, two independent validators, and the compact
quotient artifacts and regenerating checkers.

The 1.1 GB CNF/DRAT archive is deliberately not duplicated here. Its full
clean-environment audit report and journal are included under
`artifacts/audit/`; the separate archive location and DOI should be added to
the release record after Zenodo deposition.

## Quick verification

Only Python 3 and the standard library are required:

```sh
python3 verify_package.py
```

This checks the package manifest and reruns both structurally independent
validators on all 16 witnesses.

The compact quotient enumerations can also be rebuilt. They take longer:

```sh
python3 verify_package.py --full-quotients
```

## Contents

- `paper/`: English article source and 10-page rendered PDF;
- `artifacts/witnesses/`: 16 standalone coefficient vectors with validation
  records;
- `src/sds/`: reference and mixed-radix validators;
- `artifacts/runs/`: compact final quotient artifacts and the `C6 x C6`
  certificate summary;
- `scripts/verify_*_quotients.py`: independent regenerating quotient checks;
- `artifacts/audit/`: fast census audit plus the clean 57-certificate DRAT
  audit report and complete journal;
- `SHA256SUMS`: cryptographic manifest of every payload file.

The software is MIT-licensed. The paper, project-authored documentation, and
project-authored research data are CC BY 4.0. See `LICENSE`, `CITATION.cff`,
and `AI_USE.md`.
