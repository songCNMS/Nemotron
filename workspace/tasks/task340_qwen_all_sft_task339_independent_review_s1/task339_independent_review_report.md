# task340 independent review of task339/#402

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=APPROVE_TASK339_NO_TRAINING_PREFLIGHT,SESSION=89 -->

Generated: 2026-06-04T11:49:47Z

## Decision

`APPROVE_TASK339_NO_TRAINING_PREFLIGHT` for #402 exact head
`0a064f3517e6c10acfaec2c0915e24bc1434ceb1`.

The reviewed evidence supports accepting #402/task339 as a task-owned,
no-training 30B launch/config/import/resource preflight PASS using the
previously approved task337 runtime target and task333 train-only packed data
view.

This approval is preflight evidence only. It does not release task310, 30B
training, optimizer steps, eval, export, endpoint, promotion, task255 reuse,
AIME2025 train rows, shared deletion, main push, merge, or self-merge.

## Target Reviewed

- PR: #402 `https://github.com/songCNMS/Nemotron/pull/402`
- Exact head reviewed: `0a064f3517e6c10acfaec2c0915e24bc1434ceb1`
- PR state observed: `OPEN`, non-draft, base `main`, `CLEAN`/`MERGEABLE`
- Base observed: `origin/main`
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`
- Report reviewed:
  `workspace/tasks/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/task337_runtime_route_30b_launch_preflight_report.md`
- Report sha256 verified:
  `b7115e42444defdc9e0f44ad15f1e622ad476679148e285da8836a6c8b74969e`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`
- Remote artifact root:
  `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`
- task337 runtime target:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`

## Commands And Checks

Commands were run from
`/work-agents/intern_nemotron_worker_4/Nemotron_task340` unless noted.

```bash
git fetch origin main pull/402/head:refs/remotes/origin/pr/402
gh pr view 402 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url
git diff --name-status origin/main...origin/pr/402
git diff --check origin/main...origin/pr/402
git show origin/pr/402:workspace/tasks/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/task337_runtime_route_30b_launch_preflight_report.md | sha256sum
python3 <read-only py_compile wrapper for origin/pr/402 task339 helper>
```

Artifact-root commands:

```bash
cd /work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/train_only_shard_checksums.sha256
python3 -m json.tool manifests/final_summary.json
python3 -m json.tool manifests/remote_no_training_preflight_probe.json
python3 -m json.tool manifests/local_model_and_data_probe.json
python3 -m json.tool manifests/train_only_view_manifest.json
python3 -m json.tool manifests/command_env_manifest.json
python3 -m json.tool manifests/later_launch_contract.json
rg -n "TASK339_REMOTE_PREFLIGHT=PASS|nvidia_resiliency_ext|multi_storage_client|multistorageclient|training_loop_called|optimizer_step_called|weights_loaded" logs manifests config
```

Additional upstream data checks:

```bash
cd /work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/packed_shard_checksums.sha256
python3 -m json.tool manifests/decontam_no_aime2025_train_proof.json
```

Results:

- #402 exact head is
  `0a064f3517e6c10acfaec2c0915e24bc1434ceb1`.
- #402 observed state is `OPEN`, non-draft, base `main`,
  `CLEAN`/`MERGEABLE`.
- PR diff scope is worker_2 status plus task339 README/history/
  task_knowledge, task-local helper, and task339 report only.
- `git diff --check origin/main...origin/pr/402`: clean.
- Report sha256 matches
  `b7115e42444defdc9e0f44ad15f1e622ad476679148e285da8836a6c8b74969e`.
- Helper compile from PR head: `PASS`. One initial reviewer wrapper using
  `/dev/null` as the pyc target failed because `py_compile` rejects non-regular
  output files; the rerun with a temp pyc path passed and did not modify repo
  files or task339 artifacts.
- `sha256sum -c manifests/artifact_checksums.sha256`: `PASS`, 18 entries.
- `sha256sum -c manifests/train_only_shard_checksums.sha256`: `PASS`, 84
  train-only shard entries.
- Upstream task333 `artifact_checksums.sha256` and
  `packed_shard_checksums.sha256`: `PASS`.

## Artifact And Checksum Verdict

The task339 artifact root is present and checksum-backed.

- `manifests/final_summary.json` disposition:
  `PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME`.
- `manifests/remote_no_training_preflight_probe.json` disposition:
  `PASS_NO_TRAINING_PREFLIGHT_WITH_TASK337_RUNTIME`.
- `logs/remote_no_training_preflight_probe.log` contains
  `TASK339_REMOTE_PREFLIGHT=PASS`.
- `manifests/final_summary.json` records current main synced as
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Task339 `artifact_checksums_sha256` is
  `d2be924429e8dc51b9ebc6f9cba124f6673fbfa7e6290db7f650f8eaa53a4500`.

I did not modify task339 artifacts or the worker_2 branch.

## Runtime And Model Verdict

The task337 runtime handoff is consistent:

- task337 report sha256 matches
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.
- task337 artifact checksum check log passed.
- task337 runtime target exists at the expected `/root/.../runtime_site` path.
- Remote runtime imports pass for `megatron`, `megatron.bridge`,
  `megatron.bridge.training.config`, `megatron.energon`,
  `megatron.bridge.recipes.qwen.qwen3_moe`, the task-local Qwen train recipe,
  the Qwen chat contract, `torch`, and `omegaconf`.

The 30B model/tokenizer surface is also consistent:

- Model path exists:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- `model_type`: `qwen3_moe`.
- Architecture: `Qwen3MoeForCausalLM`.
- Tokenizer chat template is present.
- Tokenizer/model probing used `trust_remote_code=false`.

The Qwen3-30B Bridge config surface passed without model construction, weight
load, training loop, or optimizer step:

- Config class: `ConfigContainer`.
- Model class: `Qwen3MoEModelProvider`.
- TP/PP/EP: `4/2/4`.
- Expert tensor parallel size: `1`.
- Sequence parallel: `true`.
- Sequence length: `4096`.
- Checkpoint placeholder:
  `LEAD_APPROVED_CHECKPOINT_REQUIRED_NOT_SET`.
- `training_loop_called=false`, `optimizer_step_called=false`,
  `weights_loaded=false`.

## Data And Decontam Verdict

The task333 packed source root is present and accepted by checksum validation.
Task339 correctly uses a train-only task-owned view:

- Full task333 split exposure: 84 train shards, 6 valid shards, 6 test shards.
- Task339 train-only exposure: 84 train shards, 0 valid shards, 0 test shards.
- Train-only rows: 78,168.
- Train-only input tokens: 300,046,415.
- Train-only supervised tokens: 33,477,337.
- Train-only bytes: 154,008,682.
- Train-only source shard layout: 14 shards each for
  `agentic-interactive`, `instruction-following-structured`,
  `m1-agentic-sft-v11-from-m0`, `m1-agentic-sft-v11-math-final-answer`,
  `m1-agentic-sft-v11-math-hard-verified-full-solution`, and `swe`.

Source counts carried in `final_summary.json`:

- `agentic-interactive`: 30,909 rows; 107,206,681 input tokens;
  6,618,618 supervised tokens.
- `instruction-following-structured`: 2,361 rows; 9,048,510 input tokens;
  1,680,403 supervised tokens.
- `m1-agentic-sft-v11-from-m0`: 214 rows; 826,782 input tokens;
  149,088 supervised tokens.
- `m1-agentic-sft-v11-math-final-answer`: 25 rows; 65,176 input tokens;
  47,283 supervised tokens.
- `m1-agentic-sft-v11-math-hard-verified-full-solution`: 8 rows;
  8,770 input tokens; 7,979 supervised tokens.
- `swe`: 44,651 rows; 182,890,496 input tokens;
  24,973,966 supervised tokens.

The accepted task333 decontam proof records:

- `aime2025_prompt_or_label_train_rows=0`.
- `task255_reuse=not used`.
- All nine task327 decontam-hit sources are excluded:
  `instruction-following-chat`, `competitive-cpp-00`,
  `competitive-cpp-01`, `competitive-python-00`,
  `competitive-python-01`, `math-proofs-lean`, `agentic-tool-calling`,
  `infinibyte-00`, and `infinibyte-01`.

Residual data nuance: task333 did not run a fresh combined decontam scan; it
carries accepted upstream decontam proofs, and the task299 seed still lacks a
normalized-prompt hit field. This does not block the reviewed task339
no-training preflight, but it remains provenance context for any later training
release decision.

## Validation And Resource Verdict

Validation is fail-closed for this train-only route:

- Remote train-only view has 0 valid parquet files.
- `do_validation_expected=false`.
- Remote source contains `has_validation_data = False` and returns
  `do_validation=has_validation_data`.
- Any later validation phase entry, nonzero rc, missing checkpoint,
  non-finite loss, or shared mutation is classified as a blocker by the launch
  contract.

Resource probe evidence:

- 8 NVIDIA H200 GPUs are visible.
- Each GPU reports 143,771 MiB memory.
- Utilization observed in the probe was 0%.

The later launch template is intentionally not runnable without lead-supplied
placeholders:

- `TASK339_TRAIN_ITERS`
- `TASK339_LR`
- `TASK339_MIN_LR`
- `TASK339_LR_WARMUP_ITERS`
- `TASK339_SAVE_INTERVAL`
- `SUPER3_M1_PRETRAINED_CHECKPOINT`

## Residual Risks

- This is no-training preflight evidence only. No checkpoint was loaded, no
  weights were loaded, no training loop ran, and no optimizer step happened.
- `nvidia_resiliency_ext` remains a `RESIDUAL_FAIL`. It did not block the
  no-training config/import probe, but it is a later training-runtime residual
  that must be resolved or explicitly waived before any optimizer step.
- Diagnostic import name `multi_storage_client` remains a `RESIDUAL_FAIL`,
  while the task337 runtime target provides `multistorageclient` version
  `0.49.0`. This does not block this preflight, but any future code requiring
  the underscore module name must be checked.
- The train-only view intentionally disables validation by exposing no valid
  shards. Future training must keep this fail-closed behavior or run a new
  lead-approved preflight for any changed validation/data route.
- Required training parameters and the lead-approved Bridge checkpoint path are
  still placeholders. Task339 does not authorize filling them or running the
  template.

## Boundary Confirmation

Confirmed from the report/manifests and my own actions:

- No task339 artifact or worker_2 branch mutation.
- No optimizer steps or training loop.
- No benchmark eval, AIME eval, or task243 eval.
- No export, endpoint, promotion, task310 release, or 30B training release.
- No task255 reuse and no AIME2025 train rows.
- No shared deletion/mutation.
- No main push, merge, or self-merge.
