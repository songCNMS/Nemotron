# task184_qwen_eval_repro_gate_artifact_portability_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Make the production Qwen eval reproduction gate loadable in clean workspaces
  without local-only raw artifact files under another intern workspace.
- Remove the production-load skip workaround from the focused test module.
- Preserve remote raw artifact semantics: `vm4vpn:` / `vpn:` refs still require
  `remote_artifact_check.status: pm_verified`, and synthetic missing local files
  still fail validation.

## Boundaries

- Static YAML/Python/tests/docs only.
- No live endpoint/eval run, live artifact probe, curl/wget/requests,
  HF/download, data prep, train/eval, W&B, cluster, deploy, artifact
  upload/download, direct `main`/`master` push, or self-merge.

## Status

- Original base: `df45842edade40c19fd0496f3844ef20653a94cc`
- Tested/merged replacement base:
  `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa`
- Branch: `intern_nem_dev_3/task184_qwen_eval_repro_gate_artifact_portability_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/291
- Tested/merged head: `9456ed889081611380971457f2c579196f08390c`
- Superseded head ignored:
  `1de97978412d564f93e3e39a45199fb77ea48c98`
- Merge SHA: `f74e7c05668f96766d10c730fcd14ddec7191350`
- Local main sync: `main` and `origin/main` updated to
  `f74e7c05668f96766d10c730fcd14ddec7191350`.
- Checks: focused Qwen eval repro gate pytest, py_compile, Ruff, structured
  portability probe, product local-only artifact grep, added-line live-surface
  scan, and `git diff --check` passed before PR; PM merged-main verification
  passed with focused pytest 50 passed, py_compile, Ruff, git diff checks, and
  `PM_MERGED_QWEN_EVAL_REPRO_ARTIFACT_PORTABILITY_PROBE_PASS`.
