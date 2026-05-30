# task204_qwen_live_eval_smoke_s1

<!-- METADATA:STATUS=ReadyForPM,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Evidence-only live validation shard for Qwen eval smoke.
- Run corrected AIME/HMMT eval config compile dry-run.
- Run M1/M2/Qwen ledger validators.
- Probe endpoint/model availability from local config without printing secrets.
- Run one minimal sanitized chat-completions endpoint smoke only if an available
  Qwen chat endpoint/model/key is found.

## Boundaries

- No full benchmark sweep.
- No training, W&B, cluster, deploy, artifact upload, direct `main`/`master`
  push, or self-merge.
- No code edits unless a concrete bug is found and reported before expanding
  scope.

## Status

- Base SHA: `0460c1f0262875fb27ae530d30cd80d805752851`
- Branch: `intern_nem_dev_3/task204_qwen_live_eval_smoke_s1`
- Artifacts root: `/tmp/nemotron-live-validation/task204`
- Evidence:
  - Corrected AIME/HMMT dry-run command -> passed; runtime
    `real 2.252 user 8.968 sys 0.337`
  - Qwen/M1/M2 validator shard -> 136 passed, 8 warnings; runtime
    `real 4.242 user 4.008 sys 0.232`
  - Endpoint availability probe -> no Qwen chat endpoint/model/key advertised in
    `/work-agents/endpoints.txt` or `/work-agents/.env`; no live endpoint
    request was made
  - Structured evidence summary:
    `/tmp/nemotron-live-validation/task204/task204_evidence_summary.md`
  - Structured evidence JSON:
    `/tmp/nemotron-live-validation/task204/task204_evidence_summary.json`
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
