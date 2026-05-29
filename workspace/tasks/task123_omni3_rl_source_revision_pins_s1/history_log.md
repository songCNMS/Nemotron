# task123_omni3_rl_source_revision_pins_s1 - History Log

<!-- METADATA:SESSION=19 -->

## Session 1 - 2026-05-29

- Received PM assignment to pin Omni3 Stage1 RL MPO, Vision, and Text source
  revisions.
- Synced local `main` cleanly to `origin/main`
  `dc6e00e741c4189051bc4db4052283dbc78d0c13` and created branch
  `intern_nem_dev_2/task123_omni3_rl_source_revision_pins_s1`.
- Re-queried Hugging Face metadata without dataset download; all three SHAs
  matched PM's probe.
- Added `source_revision` pins to MPO, Vision, and Text configs and added a
  text blend `revision` pin.
- Threaded MPO/Vision source revision through RL-Omni setup/download/cache
  identity and artifact metadata.
- Added focused tests for `snapshot_download()` revision usage, run hash/config
  source identity, text blend revision preservation, and static Omni3 config
  pin coverage.
- Verified focused pytest, py_compile, Ruff, metadata probe, static unpinned
  source probe, and diff whitespace checks.

## Session 2 - 2026-05-29

- Received PM addendum before PR publication requiring the text-stage guard to
  fail when `cfg.source_revision` is set but `cfg.source_uri` has no matching
  dataset row in the loaded blend.
- Tightened `_prepare_text()` to raise a clear `ValueError` for missing blend
  rows and kept the wrong-revision error path explicit.
- Added focused negative coverage in the Omni3 portability shard and a
  structured local probe for the missing-row guard.
- Re-ran focused pytest, py_compile, Ruff, metadata source-pin probe, static
  unpinned-source probe, guard probe, and diff whitespace checks.
