# History Log

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-29

- Started task184 from `origin/main` at
  `df45842edade40c19fd0496f3844ef20653a94cc`.
- Replaced the first Qwen eval repro gate local-only MMLU-Pro calibration
  `raw_artifact_paths` with portable checked `vm4vpn:` references and
  `remote_artifact_check.status: pm_verified`.
- Removed the production-load skip workaround from
  `tests/recipes/super3/test_qwen_eval_repro_gate.py`.
- Added focused test coverage proving production raw artifact refs no longer
  depend on the local-only code-reading workspace and remote refs remain
  PM-verified.
- Ran focused Qwen eval repro gate pytest, py_compile, Ruff, structured
  portability probe, product local-only artifact grep, added-line live-surface
  scan, and `git diff --check`.
- Opened PR #291 to `main`: https://github.com/songCNMS/Nemotron/pull/291.
- No live endpoint/eval run, live artifact probe, curl/wget/requests,
  HF/download, data prep, train/eval, W&B, cluster, deploy, artifact
  upload/download, direct `main`/`master` push, or self-merge was performed.

## Session 2 - 2026-05-29

- Recorded closeout after PR #291 was merged and verified on `main` at
  `f74e7c05668f96766d10c730fcd14ddec7191350`.
- Synced local `origin/main` and `main` to
  `f74e7c05668f96766d10c730fcd14ddec7191350`.
- PM reported tested/merged replacement base/head:
  `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa` /
  `9456ed889081611380971457f2c579196f08390c`; superseded head
  `1de97978412d564f93e3e39a45199fb77ea48c98` was ignored.
- PM merged-main verification passed: focused Qwen eval repro gate pytest 50
  passed, py_compile, Ruff, git diff checks, and structured probe
  `PM_MERGED_QWEN_EVAL_REPRO_ARTIFACT_PORTABILITY_PROBE_PASS`.
- Set intern status to Idle / Current Task None. No live endpoint/eval/artifact
  probe/download, data prep, train/eval, W&B, cluster, deploy, artifact ops,
  direct `main`/`master` push, or self-merge was performed.
