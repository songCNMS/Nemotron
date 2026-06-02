# task296 current-main equivalence audit report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=76 -->

## Decision

Decision: `A_PROVED_NO_RERUN`.

Current `origin/main` at `2d84ec75960fb51ba9091427638b00083625e137`
is product-code-equivalent to the accepted task285/task293 evidence for the
scoped Qwen3-4B V11 bounded smoke plus corrected AIME gate. The only post-#351
main delta from PR #312 is coordinator workspace status/history/knowledge/handoff
documentation. I found no changes under product, data-prep, training, eval,
harness, source, tests, model, recipe, or task285/task293 runner/script paths
that would require rerunning task285 or task293.

This decision is limited to current-main equivalence for existing artifacts. It
does not authorize promotion, export, endpoint launch, task243/live AIME eval,
fresh training, task255 reuse, 30B, or 8-GPU work.

## Commands And Environment

Workspace:
`/work-agents/intern_nemotron_worker_1/Nemotron`

Branch:
`intern_nemotron_worker_1/task296_qwen_aime_v11_current_main_equivalence_audit_s1`

Read-only commands used:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main
git rev-parse origin/intern_nemotron_lead/session1-recovery-task-docs
gh pr view 312 --json number,state,baseRefName,headRefName,headRefOid,mergeCommit,mergedAt,mergedBy,url,files
git diff --name-status 5d8b8d850d26e785332f8b707c772d99881a1b5d..2d84ec75960fb51ba9091427638b00083625e137
git diff --stat 5d8b8d850d26e785332f8b707c772d99881a1b5d..2d84ec75960fb51ba9091427638b00083625e137
git diff --name-status c53095a639f0ccf8ce34afcec1bdf302cf45add6..2d84ec75960fb51ba9091427638b00083625e137 -- src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml src tests workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1 workspace/tasks/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1 workspace/tasks/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1
git diff --name-status 87de0a97e6c0406a4b67520faab6b11d91d9131e..2d84ec75960fb51ba9091427638b00083625e137 -- workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_no_export_canary_probe.py src tests workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1 workspace/tasks/task292_qwen_aime_v11_task291_canary_route_review_s1 workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1
git diff --name-only c53095a639f0ccf8ce34afcec1bdf302cf45add6..2d84ec75960fb51ba9091427638b00083625e137 -- src tests | wc -l
git diff --name-only 87de0a97e6c0406a4b67520faab6b11d91d9131e..2d84ec75960fb51ba9091427638b00083625e137 -- src tests | wc -l
git diff --name-status 87de0a97e6c0406a4b67520faab6b11d91d9131e..2d84ec75960fb51ba9091427638b00083625e137 -- workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py
gh pr view 350 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
gh pr view 351 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
gh pr view 356 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
gh pr view 357 --json number,state,baseRefName,headRefOid,mergeCommit,mergedAt,url
find /work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z -maxdepth 3 -type f
find /work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z -maxdepth 4 -type f
sha256sum <task285 report-listed files>
sha256sum <task293 report-listed files>
jq '.' /work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/artifacts/aime_eval/summary.json
jq '{load_megatron_model, model_eval, checkpoint_iter_dir, base_model_path, schema_version}' /work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/artifacts/manifests/checkpoint_load_manifest.json
jq '.' /work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/manifests/fail_closed_pre_optimizer_preflight_manifest.json
```

No training, canary, AIME/task243 eval, export, endpoint, promotion, artifact
mutation, shared deletion, main push, 30B, or 8-GPU command was run.

## Current Main And PR #312

`origin/main` verified as:
`2d84ec75960fb51ba9091427638b00083625e137`.

Lead docs branch verified as:
`c01fb6147c4d711c2a4e5f55dcbe2366ee764709`.

PR #312 metadata:

- State: `MERGED`
- Base: `main`
- Head branch: `intern_nemotron_coordinator/session1-resume-interrupted-work`
- Head SHA: `c7ada6134f63c88d1efcbf993452186d14ae24f3`
- Merge commit: `2d84ec75960fb51ba9091427638b00083625e137`
- MergedAt: `2026-06-02T12:13:44Z`
- URL: `https://github.com/songCNMS/Nemotron/pull/312`

`5d8b8d850d26e785332f8b707c772d99881a1b5d..2d84ec75960fb51ba9091427638b00083625e137`
changed 4 files, 806 insertions, and 4 deletions:

| File | Status | Classification |
|---|---:|---|
| `workspace/interns/intern_nemotron_coordinator/status.md` | M | Coordinator status doc only |
| `workspace/tasks/task_coordinator_nemotron_coordinator_06b9acba/history_log.md` | M | Coordinator task history doc only |
| `workspace/tasks/task_coordinator_nemotron_coordinator_06b9acba/session16_aime2025_qwen_handoff.md` | A | Coordinator handoff/provenance doc only |
| `workspace/tasks/task_coordinator_nemotron_coordinator_06b9acba/task_knowledge.md` | M | Coordinator task knowledge doc only |

No #312 changed file is under `src/`, `tests/`, product code, data prep,
training, eval, harness, model, recipe, task285 artifacts/scripts, or task293
artifacts/scripts.

## Task285 Source-To-Current Comparison

Task285 bounded Qwen3-4B SFT smoke source head:
`c53095a639f0ccf8ce34afcec1bdf302cf45add6`.

Relevant comparison to current main included:

- `src/`
- `tests/`
- `src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py`
- `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`
- `workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/`
- `workspace/tasks/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/`
- `workspace/tasks/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/`

Result:

- `git diff --name-only ... -- src tests | wc -l` returned `0`.
- The task276 packed-data directory had no diff in this comparison.
- `qwen_local_train.py` and `m1_agentic_train.yaml` had no diff.
- The only relevant diff output was task283/task285 docs/status/report
  closeout files:
  - task283 `README.md`, `bridge_runtime_remediation_preflight_report.md`,
    `history_log.md`, `task_knowledge.md`
  - task285 `README.md`, `bounded_qwen4b_sft_smoke_report.md`,
    `history_log.md`, `task_knowledge.md`

These are evidence/report surfaces, not product training/data code changes.

## Task293 Source-To-Current Comparison

Task293 corrected AIME eval run source head:
`87de0a97e6c0406a4b67520faab6b11d91d9131e`.

Relevant comparison to current main included:

- `src/`
- `tests/`
- `workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py`
- `workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_no_export_canary_probe.py`
- task291/task292/task293 task docs directories.

Result:

- `git diff --name-only ... -- src tests | wc -l` returned `0`.
- Explicit diff for
  `workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py`
  returned no changes.
- `run_no_export_canary_probe.py` had no diff in the broader relevant command.
- The only relevant diff output was task293 docs/report closeout files:
  - task293 `README.md`, `history_log.md`,
    `task285_iter2_same_harness_aime_eval_report.md`, `task_knowledge.md`

These are evidence/report surfaces, not eval runner or harness code changes.

## Evidence PR Metadata

- task285/#350: `MERGED`, head
  `fc379240c8517de10e37a5438f87b6b0994399f0`, merge commit
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`, mergedAt
  `2026-06-02T06:53:14Z`.
- task295/#351: `MERGED`, head
  `c2c217231c9d377430171166c85d1165ac75db69`, merge commit
  `5d8b8d850d26e785332f8b707c772d99881a1b5d`, mergedAt
  `2026-06-02T11:35:48Z`.
- task293/#356: `MERGED`, head
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`, merge commit
  `31a3e962544202954f0afba211888f7414b38d7c`, mergedAt
  `2026-06-02T11:22:34Z`.
- task294/#357: `MERGED`, head
  `f1c00a0cc8e2a9cda5e2caef9bc5137cda7835a1`, merge commit
  `24268157bd7088fea0f37d149cfc6ec042aa0e5a`, mergedAt
  `2026-06-02T11:16:53Z`.

## Task285 Artifact Checks

Task285 local output root:
`/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`

Task285 remote run root:
`/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`

Source head recorded in report:
`c53095a639f0ccf8ce34afcec1bdf302cf45add6`.

Key recomputed hashes matched the merged task285 report:

| File | sha256 |
|---|---|
| `manifests/fail_closed_pre_optimizer_preflight_manifest.json` | `3b0a3bf3233eacfe8f727ad74e73c9062a86717be7a8c127e452b9fb6283c83c` |
| `logs/bridge_import_base_proof.log` | `cb1523fffcd97d2b9e5e3b76141624d0d67ad9d2fb1d061e150f15fc7fbf66e6` |
| `manifests/bridge_import_base_proof_checksums.sha256` | `8ed6f1d3ce637e4ea2c6742a7fe7d7baea6757f85a19870119e5c659c14f347f` |
| `scripts/run_bounded_qwen4b_sft_smoke_retry3.sh` | `14ec9206372a292486ea2a5fff68ec9d35536b4ff80de5901a6e27ade2f12321` |
| `logs/bounded_qwen4b_sft_smoke_retry3.log` | `096e622a94beae16c114afcf6d6cdd923b01f77d4f5a76200b22eed5fcf0767e` |
| `manifests/smoke_checkpoints_retry3_inventory.tsv` | `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78` |
| `manifests/smoke_checkpoints_retry3_checksums.sha256` | `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4` |
| `manifests/smoke_checkpoints_retry3_du.txt` | `164ec4a7d609a3dd7b39efeab70867244a1f48e45b7eb21365f3db8eef7274dd` |
| `manifests/smoke_checkpoints_retry3_latest_iteration.txt` | `d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35` |

Pre-optimizer manifest evidence:

- fail-closed status: `PASS`
- train rows: `279`
- valid rows: `1`
- test rows: `0`
- train input tokens: `1024646`
- train supervised tokens: `228927`
- Qwen packed chat contract: `PASS`
- Qwen training pipeline contract: `PASS`
- bounded smoke CUDA visibility: `0,1`
- bounded smoke limits: `train_iters=2`, `global_batch_size=2`,
  `micro_batch_size=1`, `lr=5e-7`, `min_lr=1e-7`

Task285 merged report optimizer evidence remains:

- Iteration 1: LR `3.000000E-07`, lm loss `1.506399E+00`, skipped `0`, nan `0`.
- Iteration 2: LR `1.000000E-07`, lm loss `8.874496E-01`, skipped `0`, nan `0`.
- Latest checkpointed iteration: `2`.
- Checkpoint inventory: `34` files, size `105G`.

## Task293 Artifact Checks

Task293 local output root:
`/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`

Task293 remote run root:
`/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`

Run source head:
`87de0a97e6c0406a4b67520faab6b11d91d9131e`.

Key recomputed hashes matched the merged task293 report:

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
- FT correct: `12/30`
- FT exact-normalized accuracy: `0.4`
- accepted task247 base: `11/30 = 0.36666666666666664`
- delta: `+1` correct, `+0.03333333333333338` accuracy
- parsed rows: `21/30`
- request status: `30/30 ok`
- finish reasons: `stop=21`, `length=9`
- prompt token mismatch count versus task247 base: `0`
- same AIME score cache sha256:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`
- same row count and all-request denominator: `30`
- same prompt variant: `original`
- same max-token cap: `8192`
- same parser/normalizer/scorer logic
- checkpoint load manifest: `load_megatron_model=PASS`, `model_eval=true`
- route: `direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy_corrected_aime25`

Accepted task247 base hashes carried from task293:

| File | sha256 |
|---|---|
| `summary.json` | `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639` |
| `results.jsonl` | `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961` |
| `command.txt` | `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40` |
| `endpoint_model_manifest.json` | `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354` |

## Residuals Carried Forward

- task285 smoke command returned `SMOKE_RETRY3_COMMAND_RC=1` after the
  iteration-2 checkpoint was saved because the framework entered built-in
  validation and the task-owned process received SIGTERM. The built-in eval is
  incomplete and is not accepted as an eval pass.
- task276 packed data remains sparse for validation/test: valid has one packed
  row and test has zero rows.
- task292/task291 canary route review carried the synthetic-row detokenized
  fallback residual.
- task293 has `sampling_exact_parameter_match=false`: task247 base used SGLang
  endpoint settings while task293 FT used the approved no-export/no-endpoint
  local MCore greedy route. The accepted residual is semantic greedy match, not
  byte-identical transport/sampling surface.
- This audit does not create release, promotion, endpoint, export, task243,
  fresh full eval, 30B, or 8-GPU clearance.

## Boundary Confirmation

For this task I did not run training, nonzero-LR smoke, live canary,
AIME/task243 eval, export, conversion, endpoint launch, promotion, task255
reuse, AIME2025 prompt/label train data, shared deletion, main push, merge, 30B,
or 8-GPU work. I did not mutate task285/task293 artifacts.
