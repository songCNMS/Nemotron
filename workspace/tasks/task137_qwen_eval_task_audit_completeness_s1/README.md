# task137_qwen_eval_task_audit_completeness_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Make `qwen_chat_contract.task_audit` classify every runnable task in
  `m1_full_basket_launcher_available.yaml`.
- Prefer exact one-bucket classification for runnable tasks.
- Add static tests that detect missing, duplicated, and extra audit task names.

## Boundaries

- Static/config/test-only.
- No live benchmark/eval run, endpoint call, W&B, cluster job, data prep,
  training, artifact download, deployment, direct `main`/`master` push, or
  self-merge.

## Status

- Branch: `intern_nem_dev_3/task137_qwen_eval_task_audit_completeness_s1`
- Base: `c917636a006c0d3e5f7bcff6db97189bad6f8c13`
- PR: https://github.com/songCNMS/Nemotron/pull/244
