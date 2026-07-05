# Known Bugs

For v0.2 fix candidates surfaced by the edge-case test suite.

- BOM handling fails for file starts (`test_bom_at_file_start`).
  UTF-8 BOM before the frontmatter fence is not stripped; rules saved by
  editors that emit BOM by default (some Windows tooling) won't index.
- Build + suggest is too slow on 500 rules (`test_500_rules_loads_in_under_500ms`).
  Synthetic benchmark hits ~570 ms; the 500 ms target is aspirational. K2
  attempted a disk-pickle cache to fix this; the cache landed only a 1.4×
  speedup at 2000 rules — not worth the added attack surface and
  invalidation complexity. Reverted. See git log for K2 revert notes. Real
  fix likely needs incremental indexing (only re-parse changed files), not
  a serialisation swap.

## Notes

Bugs are tracked in tests rather than in this file going forward — `pytest -k xfail`
shows what's outstanding. This file exists for prose context the test
comments can't carry.
