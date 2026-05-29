# task184_qwen_eval_repro_gate_artifact_portability_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

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

- Base: `df45842edade40c19fd0496f3844ef20653a94cc`
- Branch: `intern_nem_dev_3/task184_qwen_eval_repro_gate_artifact_portability_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/291
- Head: `1de97978412d564f93e3e39a45199fb77ea48c98`
- Checks: focused Qwen eval repro gate pytest, py_compile, Ruff, structured
  portability probe, product local-only artifact grep, added-line live-surface
  scan, and `git diff --check` passed.
