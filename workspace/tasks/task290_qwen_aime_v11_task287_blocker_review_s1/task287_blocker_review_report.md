# task290 Task287 Blocker Evidence Review

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_1,SESSION=2 -->

Generated: 2026-06-02T08:05:00Z

Decision: `APPROVE_BLOCKER_CLOSEOUT`.

This is an independent read-only review of task287 blocker evidence. It does
not authorize canary execution, training, AIME/task243 eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, merge, main
push, 30B, or 8-GPU.

## Reviewed Target

- Authoritative task287 PR: #352
  https://github.com/songCNMS/Nemotron/pull/352
- PR state at review time: `OPEN`, base `main`, `CLEAN`, non-draft.
- Reviewed exact PR head:
  `52834d74c79ab98b5e125434160843752c34d47a`.
- Task287 report at that head:
  `workspace/tasks/task287_qwen_aime_v11_non_aime_canary_retention_s1/non_aime_canary_retention_report.md`.
- Original task docs named local task287 acceptance head
  `aa5ff74046221926c53eddfe1afbd7df38baaa89`; lead update superseded the
  review target with official PR #352 exact head above.
- Drift from task287 head `e01ced3303ce136ba36e299845b19a03278a3181` to
  `52834d74c79ab98b5e125434160843752c34d47a` is status/history metadata only;
  the task287 report content is unchanged in that drift.

## Artifact Root

Task287 local output root reviewed:

`/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`

Canary attempt root emphasized by lead:

`/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z/canary/qwen4b_task285_iter2_non_aime_canary_20260602T071900Z`

Remote run root recorded by artifacts:

`/root/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`

`source_head.txt` records:

`aa5ff74046221926c53eddfe1afbd7df38baaa89`

`remote/sync_check.log` records `SYNCED_CODE_PRESENT`. `remote/synced_head.txt`
is empty, so the remote copy's git head is not independently recorded in that
file; this is a residual documentation gap but not a blocker for accepting the
published #352 blocker report because the local output root, PR report, and
command/hash artifacts are otherwise internally consistent.

## Checksum Validation

Required lead hashes matched direct `sha256sum`:

| Artifact | sha256 |
|---|---|
| `canary/qwen4b_task285_iter2_non_aime_canary_20260602T071900Z/canary_blocker.json` | `551e76adcb3a29ad421bed4ad48d60b31225b664896d10ae715df5bb87b4a9e9` |
| `canary/qwen4b_task285_iter2_non_aime_canary_20260602T071900Z/checkpoint_load_manifest.json` | `e48c8128d4360e93f7858b682474c293ad715bd441fbaa791f33c131b7f83b13` |
| `logs/remote_direct_canary_run.log` | `d2aaa3762e2fa368c66fb1aa26ed97b5d459368e756ae87bf1767d1ae6d89ecc` |
| `logs/remote_single_gpu_checkpoint_load_probe.log` | `e63eb5634677e2640984bd8666b5b7134f6f6ce71ff9982ba68322c2672d61c1` |

Additional reviewed hashes:

| Artifact | sha256 |
|---|---|
| `manifests/canary_prompt_manifest.json` | `69d6634c47eea160548fe2779b6dd6038dc7605e8c9a894660a385efc9ae7cc2` |
| `manifests/repo_gate_file_hashes.sha256` | `77574ff744a024dc11765989ed69b94be9a9ca26377f2349fbf6008b0e3e3dc5` |
| `logs/remote_symbol_probe.log` | `097b500443c750bfb1d6495ad282dff7c77fd47d6fd3c4a0039ccd147ad9de82` |
| `logs/remote_checkpoint_metadata_probe.log` | `9f9f212ad3024e931ac82f3027a3ef6a43dd50f08a6507e2a7617c030e0218e8` |
| `logs/remote_bridge_config_tokenizer_probe.log` | `4b63671b105448688f04152e93565f586937f84809a7fffc052e4b6491cd9d4f` |
| `logs/remote_bridge_load_source_probe.log` | `ab201801527cec41319da0d4e2d4da8857ab11d592d242ced7ab0895d96f41fe` |

Retry blocker hashes checked for consistency:

| Artifact | sha256 |
|---|---|
| `canary/qwen4b_task285_iter2_non_aime_canary_20260602T072300Z/canary_blocker.json` | `77a6c76e8ddb993d4c4cdf4e460980b8654849f4c86333a9a82dcd62b842720d` |
| `canary/qwen4b_task285_iter2_non_aime_canary_20260602T072800Z/canary_blocker.json` | `aa451bfb364e1c44b67f6a0beb2612a2f331582555909445099c228c480aab2e` |
| `logs/remote_direct_canary_run_retry1.log` | `c1a8c122e74086fb687bca5403e723879056b835c3dab761b174ba69e8ba27f9` |
| `logs/remote_direct_canary_run_retry2.log` | `f32df07a0ab624057a93b3615f28416dc212c3d511bd617fa1c2508825e65473` |

## Blocker Findings

The authoritative #352 report and local artifacts agree:

- The task285 iter2 checkpoint is present at
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`.
- `checkpoint_load_manifest.json` records `latest_iteration: 2`.
- `remote_single_gpu_checkpoint_load_probe.log` records:
  - `LOAD_MEGATRON_MODEL=PASS`;
  - model type `megatron.core.transformer.module.Float16Module`;
  - device `cuda:0`;
  - dtype `torch.bfloat16`;
  - `MODEL_EVAL_SET=PASS`.
- The allowed route was
  `direct_in_process_mcore_static_engine_no_endpoint_no_export`.
- The lead-named `071900Z` attempt blocks with:
  - status `BLOCK`;
  - error type `ImportError`;
  - error `cannot import name 'get_model_config' from 'megatron.core.transformer.module'`.
- Later local attempts remain consistent with route/runtime blocking:
  - `072300Z`: `ValueError: Unknown attention backend None`;
  - `072800Z`: `AcceleratorError: CUDA error: device-side assert triggered`.
- No retained completion artifacts were found. Filename search found no
  `completion`, `response`, `result`, `prediction`, `sample`, `output`, or
  `jsonl` completion artifacts under the canary attempt tree. Task287 PR #352
  also states expected `canary_summary.json`, `canary_results.jsonl`, and
  `canary_full_completions.jsonl` are absent because generation did not
  complete.

This is a route/runtime blocker, not model-quality evidence. The checkpoint
loads, but the currently attempted no-export/no-endpoint in-process generation
route cannot produce retained non-AIME canary completions.

## Prompt And Data Boundary Review

The prompt manifest contains five synthetic non-AIME prompts and records:

- `synthetic_prompts_only: true`;
- `review_only_not_trainable: true`;
- `excludes_aime2025: true`;
- `excludes_training_rows: true`;
- `no_aime2025_prompt_or_label_text: true`.

Each prompt has `contains_aime_case_insensitive: false`.

The reviewed blocker manifests record all required boundaries as true:

- `no_export`;
- `no_endpoint`;
- `no_aime_task243_eval`;
- `no_training_or_optimizer_steps`;
- `no_task255_reuse`;
- `no_aime2025_train_data`;
- `no_30b`;
- `no_8gpu`.

`canary_command.json` records one H200 via `CUDA_VISIBLE_DEVICES=0`, not 8-GPU.

## Publication Status

The initial task290 assignment noted no official task287 report/PR. That is no
longer true:

- Task287 PR #352 is now visible.
- PR #352 is `OPEN`, base `main`, `CLEAN`, non-draft at exact head
  `52834d74c79ab98b5e125434160843752c34d47a`.
- The official task287 report in #352 records the same artifact root, hashes,
  checkpoint load proof, absent completions, and boundary confirmations.

Therefore task287 does not need to remain HOLD waiting for worker_3 publication.
It can be reviewed/closed as `BLOCK` using PR #352 plus the artifact evidence.

## Decision

`APPROVE_BLOCKER_CLOSEOUT`.

The artifacts are sufficient official gate input to classify task287 as BLOCK:

- exact PR head and official report are visible;
- required hashes match;
- checkpoint load proof passes;
- the allowed no-export/no-endpoint route blocks before completion retention;
- no retained completion artifacts exist;
- boundary confirmations are present and consistent.

## Recommended Bounded Unblock Task

Create a new bounded no-training/no-AIME implementation or runtime-probe task
to repair the Qwen3-4B task285 iter2 checkpoint local generation path without
export or endpoint. The task should:

- use one GPU and Qwen3-4B only;
- avoid task255 and AIME2025 train data;
- keep no export and no endpoint unless lead explicitly changes the route;
- verify a compatible MCore or Bridge generation wrapper for the task285 iter2
  torch-dist checkpoint;
- address the observed route failures:
  - missing `get_model_config` import path;
  - `Unknown attention backend None`;
  - CUDA device-side assert during sampling;
- produce retained non-AIME completion artifacts with prompt hashes, response
  hashes, extracted final answers, finish reasons, and degeneration flags;
- stop before AIME/task243 eval, promotion, 30B, or 8-GPU.

## Commands Run

Read-only commands only:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1
git show --no-patch --format='%H%n%P%n%s' <task287_heads>
gh pr view 352 --repo songCNMS/Nemotron --json number,url,state,baseRefName,headRefOid,mergeStateStatus,isDraft,title
sha256sum <task287 blocker/log/manifest artifacts>
python3 - <<'PY'
# Read-only JSON field inspection for canary_blocker.json,
# checkpoint_load_manifest.json, canary_command.json, and prompt manifest.
PY
rg -n <status/error/boundary markers> <task287 logs and JSON artifacts>
find <task287 canary root> -type f
git diff --name-status <task287_heads> -- workspace/tasks/task287... workspace/interns/intern_nemotron_worker_3/status.md
git diff --check
```

No code edits, canary run, training, AIME/task243 eval, export, endpoint,
promotion, task255 reuse, AIME2025 train-data use, shared deletion, merge, main
push, 30B, or 8-GPU action was performed.
