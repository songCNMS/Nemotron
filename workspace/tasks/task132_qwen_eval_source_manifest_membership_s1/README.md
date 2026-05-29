# task132_qwen_eval_source_manifest_membership_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Enforce that every Qwen eval evidence record `source_manifest` is declared in
  the top-level `source_manifests` list.
- Preserve existing source-manifest path hardening and raw artifact validation
  behavior from prior Qwen eval gate tasks.
- Add focused static tests for production membership and undeclared existing
  repo YAML rejection.

## Boundaries

- Static/offline validation only.
- No live benchmark/eval, endpoint calls, W&B, cluster jobs, data prep,
  training, artifact download, deployment, direct `main`/`master` push, or
  self-merge.

## Status

- Branch: `intern_nem_dev_3/task132_qwen_eval_source_manifest_membership_s1`
- Base: `df587d239f573503347f7e36f5f8354ff581a186`
- PR: https://github.com/songCNMS/Nemotron/pull/238
