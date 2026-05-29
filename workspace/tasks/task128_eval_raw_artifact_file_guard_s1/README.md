# task128_eval_raw_artifact_file_guard_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Harden Qwen eval raw artifact validation so local `raw_artifact_paths` must
  be regular files, not merely existing paths.
- Preserve `vm4vpn:` and `vpn:` remote artifact reference handling and existing
  PM-verified metadata checks.
- Cover both Qwen eval repro gate and benchmark-alignment callers through the
  shared raw artifact path helper.

## Boundaries

- No live eval, training, data prep, endpoint calls, W&B, cluster jobs,
  artifact downloads, deployments, direct `main`/`master` push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task128_eval_raw_artifact_file_guard_s1`
- Base: `22d33bf428bed321c0277badc5d193ada62abf00`
- PR: pending
