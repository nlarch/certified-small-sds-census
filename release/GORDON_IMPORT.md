# Import fragment for the La Jolla repository

`gordon_v32_20_4_noncyclic_entries.json` contains the six positive
`SDS(32,20,4,G)` entries in the format used by Daniel Gordon's
`signed-difference-sets/sds.json` file.

For every entry:

- `status` is `Yes`, because the fragment supplies at least one construction;
- `sets` is a list containing one `[P,N]` pair;
- every noncyclic group element is a coordinate list in invariant-factor
  order, with the final coordinate varying fastest;
- `G_rep` is omitted because the coordinates already use the invariant
  factors in the entry name.

Regenerate the fragment and validate every source witness with both project
validators:

```text
python3 scripts/export_gordon_v32_witnesses.py
```

The fragment is intended to be merged entry-by-entry into Gordon's top-level
JSON object, replacing the corresponding six `Open` records. It is not a
complete replacement for his `sds.json` file.
