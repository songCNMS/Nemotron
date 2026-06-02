# task297 current-main equivalence review report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=5 -->

## Decision

- Decision: `APPROVE_A_PROVED_NO_RERUN_WITH_RESIDUALS`
- Reviewed upstream PR: #359
- Reviewed upstream head:
  `b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06`
- Reviewed upstream state: `OPEN`, base `main`, merge state `CLEAN`
- Task297 PR:
  `https://github.com/songCNMS/Nemotron/pull/358`
- Current `origin/main`:
  `2d84ec75960fb51ba9091427638b00083625e137`

I approve task296's conclusion that current `origin/main` is equivalent to the
accepted task285/task293 evidence for the scoped current-main no-rerun decision.
This is not a fresh training/eval approval and does not authorize export,
endpoint launch, promotion, task243/live AIME eval, task255 reuse, 30B, or
8-GPU work.

## Scope And Freshness

The substantive task296 report was introduced at
`b45308e99db75620dd421c4cdc44560cdcda8eec`. The current reviewed #359 head is
`b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06`.

Freshness checks:

- `git diff --name-only b45308e9..b9c1af29 -- current_main_equivalence_audit_report.md`
  returned no output.
- `git diff --name-status b45308e9..b9c1af29` changed only worker_1 status plus
  task296 `history_log.md` and `task_knowledge.md`.
- `git diff --check b45308e9..b9c1af29` was clean.

Therefore the current #359 head is a metadata/status refresh over the same
substantive task296 audit evidence.

## Commands And Checks

Read-only review commands included:

```bash
git fetch origin main intern_nemotron_worker_1/task296_qwen_aime_v11_current_main_equivalence_audit_s1
gh pr view 359 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,url
git rev-parse origin/main
git log --oneline --decorate -5 origin/intern_nemotron_worker_1/task296_qwen_aime_v11_current_main_equivalence_audit_s1
git diff --name-status b45308e99db75620dd421c4cdc44560cdcda8eec..b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06
git diff --check b45308e99db75620dd421c4cdc44560cdcda8eec..b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06
git show b45308e99db75620dd421c4cdc44560cdcda8eec:workspace/tasks/task296_qwen_aime_v11_current_main_equivalence_audit_s1/current_main_equivalence_audit_report.md
gh pr view 312 --json number,state,baseRefName,headRefName,headRefOid,mergeCommit,mergedAt,url,files
git diff --name-status 5d8b8d850d26e785332f8b707c772d99881a1b5d..2d84ec75960fb51ba9091427638b00083625e137
git diff --stat 5d8b8d850d26e785332f8b707c772d99881a1b5d..2d84ec75960fb51ba9091427638b00083625e137
git diff --name-status c53095a639f0ccf8ce34afcec1bdf302cf45add6..2d84ec75960fb51ba9091427638b00083625e137 -- src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml src tests workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1 workspace/tasks/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1 workspace/tasks/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1
git diff --name-only c53095a639f0ccf8ce34afcec1bdf302cf45add6..2d84ec75960fb51ba9091427638b00083625e137 -- src tests | wc -l
git diff --name-status 87de0a97e6c0406a4b67520faab6b11d91d9131e..2d84ec75960fb51ba9091427638b00083625e137 -- workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_no_export_canary_probe.py src tests workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1 workspace/tasks/task292_qwen_aime_v11_task291_canary_route_review_s1 workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1
git diff --name-only 87de0a97e6c0406a4b67520faab6b11d91d9131e..2d84ec75960fb51ba9091427638b00083625e137 -- src tests | wc -l
git diff --name-status 87de0a97e6c0406a4b67520faab6b11d91d9131e..2d84ec75960fb51ba9091427638b00083625e137 -- workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py
gh pr view 350 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
gh pr view 351 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
gh pr view 356 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
gh pr view 357 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
sha256sum <task285 report-listed files>
sha256sum <task293 report-listed files>
jq '.' <task285 fail_closed_pre_optimizer_preflight_manifest.json>
jq '.' <task293 summary.json>
jq '.' <task293 command_env_manifest.json>
```

No training, canary, AIME/task243 eval, export, endpoint launch, promotion,
artifact mutation, shared deletion, main push, merge, 30B, or 8-GPU command was
run.

## Current Main Delta

PR #312 is merged into current main:

- PR: `https://github.com/songCNMS/Nemotron/pull/312`
- State: `MERGED`
- Head: `c7ada6134f63c88d1efcbf993452186d14ae24f3`
- Merge commit: `2d84ec75960fb51ba9091427638b00083625e137`
- MergedAt: `2026-06-02T12:13:44Z`

The delta from `5d8b8d850d26e785332f8b707c772d99881a1b5d` to current main
changed only coordinator workspace documentation:

- `workspace/interns/intern_nemotron_coordinator/status.md`
- `workspace/tasks/task_coordinator_nemotron_coordinator_06b9acba/history_log.md`
- `workspace/tasks/task_coordinator_nemotron_coordinator_06b9acba/session16_aime2025_qwen_handoff.md`
- `workspace/tasks/task_coordinator_nemotron_coordinator_06b9acba/task_knowledge.md`

No changed #312 file is product code, data prep, training, eval, harness,
model/recipe code, `src/`, `tests/`, or task285/task293 runner code.

## Task285 Equivalence

Task285 source head:
`c53095a639f0ccf8ce34afcec1bdf302cf45add6`.

Comparison to current main over `src`, `tests`,
`qwen_local_train.py`, `m1_agentic_train.yaml`, task276, task283, and task285
showed:

- `git diff --name-only ... -- src tests | wc -l` returned `0`.
- `qwen_local_train.py` and `m1_agentic_train.yaml` had no diff.
- The task276 packed-data task directory had no diff.
- Diff output was limited to task283/task285 README/report/history/knowledge
  files.

Task285 local artifact root checked:
`/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`.

Key recomputed hashes matched task296/task285 carried evidence:

| File | sha256 |
|---|---|
| `manifests/fail_closed_pre_optimizer_preflight_manifest.json` | `3b0a3bf3233eacfe8f727ad74e73c9062a86717be7a8c127e452b9fb6283c83c` |
| `logs/bridge_import_base_proof.log` | `cb1523fffcd97d2b9e5e3b76141624d0d67ad9d2fb1d061e150f15fc7fbf66e6` |
| `scripts/run_bounded_qwen4b_sft_smoke_retry3.sh` | `14ec9206372a292486ea2a5fff68ec9d35536b4ff80de5901a6e27ade2f12321` |
| `logs/bounded_qwen4b_sft_smoke_retry3.log` | `096e622a94beae16c114afcf6d6cdd923b01f77d4f5a76200b22eed5fcf0767e` |
| `manifests/smoke_checkpoints_retry3_inventory.tsv` | `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78` |
| `manifests/smoke_checkpoints_retry3_checksums.sha256` | `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4` |
| `manifests/smoke_checkpoints_retry3_latest_iteration.txt` | `d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35` |

Pre-optimizer manifest evidence:

- `pre_optimizer_fail_closed.status`: `PASS`
- train/valid/test rows: `279` / `1` / `0`
- train input/supervised tokens: `1024646` / `228927`
- Qwen packed chat contract: `PASS`
- Qwen training pipeline contract: `PASS`
- bounds: `CUDA_VISIBLE_DEVICES=0,1`, `train_iters=2`,
  `global_batch_size=2`, `micro_batch_size=1`, `lr=5e-7`, `min_lr=1e-7`

Task285 smoke log evidence:

- Iteration 1: LR `3.000000E-07`, lm loss `1.506399E+00`, skipped `0`,
  nan `0`.
- Iteration 2: LR `1.000000E-07`, lm loss `8.874496E-01`, skipped `0`,
  nan `0`.
- Latest checkpoint iteration: `2`.
- Checkpoint size report: `105G`.
- `SMOKE_RETRY3_COMMAND_RC=1` occurred after iteration-2 checkpoint save when
  the framework entered built-in validation/SIGTERM. This remains a residual,
  not an accepted eval pass.

## Task293 Equivalence

Task293 source head:
`87de0a97e6c0406a4b67520faab6b11d91d9131e`.

Comparison to current main over `src`, `tests`, task291/task292/task293 docs,
`run_no_export_aime_eval.py`, and `run_no_export_canary_probe.py` showed:

- `git diff --name-only ... -- src tests | wc -l` returned `0`.
- Explicit diff for `run_no_export_aime_eval.py` returned no output.
- Diff output was limited to task293 README/report/history/knowledge files.

Task293 local artifact root checked:
`/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`.

Key recomputed hashes matched task296/task293 carried evidence:

| File | sha256 |
|---|---|
| `artifacts/aime_eval/summary.json` | `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7` |
| `artifacts/aime_eval/results.jsonl` | `4cbc2a9543a658df6a3e18e3128c5a5c9a173f9a575372095cfcbe5d6232aca5` |
| `artifacts/aime_eval/full_completions.jsonl` | `5cb1e11ab8d331127c7c12f2cd8c04d83d2e6bd93445a5ebffc62363e2a818b4` |
| `artifacts/manifests/aime_prompt_manifest.json` | `93146086fcc2214fc3c866354e23358d320377caddb6d2b5a2bd58954e85b919` |
| `artifacts/manifests/checkpoint_load_manifest.json` | `243044f2e548e0c8b1b539e9c11fee17a39b4d45898e1a6601382716e4d90c74` |
| `artifacts/manifests/command_env_manifest.json` | `5b128b5cc84159b8603b07fc92475ebc768152b7c0ea0fae0897c6635a502ccf` |
| `artifacts/manifests/checksum_manifest.json` | `6a47e802433648248658010125db51474d0b4af565dc10c637d004900948e7d4` |
| `logs/remote_no_export_aime_eval.log` | `c0dbfcd93cbb7c615c7f784b201a862e338c4eea23c0faf6d9dd9aa5bdcae4ab` |
| `logs/remote_no_export_aime_eval_command.txt` | `39bfe804e49eb34ada919ef0ec557313a7cea7eed26c86ab18f746cf2fdd487b` |

Task293 summary evidence:

- disposition: `PASS`
- total requests: `30`
- FT score: `12/30 = 0.4`
- accepted base score: `11/30 = 0.36666666666666664`
- delta: `+1` correct, `+0.03333333333333338` accuracy
- request status: `30/30 ok`
- parsed rows: `21/30`
- finish reasons: `stop=21`, `length=9`
- prompt token mismatch count versus accepted task247 base: `0`
- same AIME score cache sha:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`
- same row count/denominator, prompt variant, max tokens, and parser/normalizer
  proof are present.
- checkpoint load manifest has `load_megatron_model=PASS` and
  `model_eval=true`.
- route: `direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy_corrected_aime25`

Task293 boundary confirmations recorded no export, no endpoint, no promotion,
no task255 reuse, no AIME2025 train prompts or labels, one GPU, no 30B, and no
8-GPU.

## Residual Risks

- task285 smoke command has `SMOKE_RETRY3_COMMAND_RC=1` after iteration-2
  checkpoint save because built-in validation started and was interrupted by
  SIGTERM. The checkpoint/optimizer evidence is usable for the bounded smoke
  artifact, but this is not an eval pass.
- task276 packed data remains sparse for validation/test: valid has one row and
  test has zero rows.
- task292/task291 retained canary route carried the synthetic-row detokenized
  fallback residual.
- task293 has `sampling_exact_parameter_match=false`: accepted base used SGLang
  endpoint settings while FT used the approved no-export/no-endpoint local MCore
  top-k-1 greedy route. I accept this only as semantic greedy equivalence, not
  byte-identical transport/sampling equivalence.
- The approval is limited to current-main no-rerun equivalence. It does not
  authorize release, promotion, export, endpoint, task243/live AIME eval, fresh
  training/eval, task255 reuse, 30B, or 8-GPU work.

## Boundary Confirmation

This task297 refresh was review-only apart from updating task297/status docs on
the worker_4 review branch. I did not train, run canary, run AIME/task243 eval,
export, launch an endpoint, promote, reuse task255, use AIME2025 prompt/label
train data, delete shared files, push main, merge, use 30B, or use 8-GPU.
