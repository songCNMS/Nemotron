# task147_omni3_text_rl_blend_path_cwd_independence_s1 history

<!-- METADATA:SESSION=8 -->

## Session 1 - 2026-05-29

- Created branch
  `intern_nem_dev_3/task147_omni3_text_rl_blend_path_cwd_independence_s1`
  from `origin/main` at `7145c7de80f03555259a9b5657cc4066812f50d0`.
- Updated Omni3 text RL `blend_path` to the repo-relative checked-in
  `data_blend_raw.json` path.
- Added an Omni3-local helper in `_data_prep_base.py` that resolves checked-in
  Omni3 data-prep source paths from any caller CWD while preserving absolute
  and arbitrary relative overrides.
- Extended focused config portability tests for raw YAML, non-repo CWD
  resolution, dataclass resolution, and override preservation.
- Verified focused Omni3 portability pytest, Omni3 CLI pytest, py_compile,
  Ruff, structured non-repo CWD probe, static stale-PWD grep, no
  `train_script.py` diff, added-line live-surface scan, and diff check before
  staging.
- Opened PR #254 to `main`: https://github.com/songCNMS/Nemotron/pull/254.

## Session 8 - 2026-05-29

- Added stop-hook bookkeeping for the already-open PR #254; no product or test
  code changes were made in this session.
