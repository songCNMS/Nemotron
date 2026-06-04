# task339 task337-runtime 30B launch preflight rerun report

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME,SESSION=3 -->

Generated: 2026-06-04T11:32:00Z

## Disposition

`PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME`.

The task335-equivalent no-training Qwen3-30B all-SFT launch/config/import/
resource preflight was rerun from current main
`f083c9566a9f0775c27ae49f16b8b898edfc8d11` with the approved task337 runtime
target prepended on `PYTHONPATH`.

This proves a no-training handoff route only. It does not release task310, 30B
training, optimizer steps, eval, export, endpoint, promotion, task255 reuse,
AIME2025 train rows, shared deletion/mutation, main push, merge, or self-merge.

## Artifact Roots

| Artifact | Path |
|---|---|
| Local run root | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z` |
| Remote run root | `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z` |
| Remote synced repo | `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/Nemotron` |
| Remote synced head | `f083c9566a9f0775c27ae49f16b8b898edfc8d11` |
| task337 runtime target | `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site` |
| task333 packed root | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract` |
| Local train-only root | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/packed_qwen_task333_train_only_contract` |
| Remote train-only root | `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/input/packed_qwen_task333_train_only_contract` |
| Final summary | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/manifests/final_summary.json` |
| Remote preflight manifest | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/manifests/remote_no_training_preflight_probe.json` |
| Later launch contract | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/manifests/later_launch_contract.json` |
| Template, not run | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/config/run_later_training_TEMPLATE_DO_NOT_RUN.sh` |

Important checksums:

| File | sha256 |
|---|---|
| `manifests/final_summary.json` | `af9220da4de0668b8f2baefe146ea3ec431a1ca66278d7235a6b3c476ae1bcdb` |
| `manifests/artifact_checksums.sha256` | `d2be924429e8dc51b9ebc6f9cba124f6673fbfa7e6290db7f650f8eaa53a4500` |
| `manifests/remote_no_training_preflight_probe.json` | `c4d569de1d49aefbdcf0e9c5cb44f476993d84e8498aa15fe52e991f2fbf2b17` |
| `manifests/command_env_manifest.json` | `fb2020f440c5f7ede9bdd555f77775b6a3e3a36979f49e96901de38d7b3a5a32` |
| `manifests/later_launch_contract.json` | `7352db7e6b1cd14de0da58a3b70e0375ae69c33c048a77782f17e87b8bc2f39a` |
| `manifests/local_model_and_data_probe.json` | `7088ab0f51b99db820f36dda3fd58348b179f99d868d8ae56b54926cc495c2d7` |
| `logs/remote_no_training_preflight_probe.log` | `bc94f2d06228d9d98a8742c08db1eb6a9a97b0e37a09a5bcdfc16dda5c6feb51` |
| `config/remote_no_training_preflight_probe.py` | `87f99c7f49f89636dfc297a871efe14a8f4271a3b57ffddbb0febbbced0a702d` |
| `config/run_later_training_TEMPLATE_DO_NOT_RUN.sh` | `f4ef5b83abfd56428228a91444299c93be78022581cad3d4bf901568afaa9210` |

Validation commands from the local run root:

```bash
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/train_only_shard_checksums.sha256
```

Both returned `rc=0`.

## Commands And Environment

Primary command:

```bash
PYTHONPATH=src python3 \
  workspace/tasks/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/build_task339_30b_launch_preflight_rerun.py
```

Recorded phases:

| Phase | rc | Log |
|---|---:|---|
| `task337_artifact_checksum_check` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/logs/task337_artifact_checksums_check.log` |
| `sync_current_main_to_root` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/logs/remote_repo_sync.log` |
| `sync_train_only_data_to_root` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/logs/remote_train_only_data_sync.log` |
| `sync_remote_probe_artifacts` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/logs/remote_probe_artifact_sync.log` |
| `remote_no_training_preflight_probe` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/logs/remote_no_training_preflight_probe.log` |
| `fetch_remote_preflight_manifest` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/logs/fetch_remote_preflight_manifest.log` |

Remote environment:

```bash
PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/Nemotron/src
SUPER3_M1_AGENTIC_PACKED_DIR=/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/input/packed_qwen_task333_train_only_contract/splits
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
SUPER3_M1_TRAINING_PROFILE=qwen
WANDB_MODE=offline
WANDB_DISABLED=true
TOKENIZERS_PARALLELISM=false
```

Remote host: `NemTron` (`lg-cmc-b7r201-f08u26-h200-000126` in probe output).

## task337 Runtime Handoff

The task337 artifact checksum manifest passed with `rc=0`.

Accepted markers:

- task337 report sha256:
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.
- task337 final disposition: `PASS_RUNTIME_REMEDIATED`.
- task337 import marker: `PASS_QWEN3_MOE_IMPORT`.
- task337 symbol marker: `PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- Runtime target exists on NemTron and was first in `PYTHONPATH`.

## Data And Model Checks

Model:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

- Exists.
- `model_type=qwen3_moe`.
- Architecture: `Qwen3MoeForCausalLM`.
- Qwen tokenizer chat template present.
- `trust_remote_code=false` for tokenizer/model probing.

task333 full root remained read-only and exposes `84` train, `6` valid, and
`6` test shards. For launch handoff, task339 materialized a task-owned
train-only root to preserve the validation skip/fail-closed route.

Train-only metrics:

| Split | Shards | Rows | Input tokens | Supervised tokens | Bytes |
|---|---:|---:|---:|---:|---:|
| train | 84 | 78,168 | 300,046,415 | 33,477,337 | 154,008,682 |
| valid | 0 | 0 | 0 | 0 | 0 |
| test | 0 | 0 | 0 | 0 | 0 |

By train source:

| Source | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `agentic-interactive` | 14 | 30,909 | 107,206,681 | 6,618,618 |
| `instruction-following-structured` | 14 | 2,361 | 9,048,510 | 1,680,403 |
| `m1-agentic-sft-v11-from-m0` | 14 | 214 | 826,782 | 149,088 |
| `m1-agentic-sft-v11-math-final-answer` | 14 | 25 | 65,176 | 47,283 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 8 | 8,770 | 7,979 |
| `swe` | 14 | 44,651 | 182,890,496 | 24,973,966 |

No AIME2025 prompt/label train rows were introduced; task339 reused accepted
task333 decontam/source-exclusion evidence and did not materialize new train
rows outside the train-only view.

## Remote No-Training Preflight

Required imports passed:

- `omegaconf`
- `torch`
- `megatron`
- `megatron.energon`
- `megatron.bridge`
- `megatron.bridge.training.config`
- `megatron.bridge.recipes.qwen.qwen3_moe`
- `nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train`
- `nemotron.recipes.super3.stage1_sft.qwen_chat_contract`

Qwen3-30B Bridge config surface passed without training:

- Config class: `ConfigContainer`.
- Model class: `Qwen3MoEModelProvider`.
- TP/PP/EP: `4`/`2`/`4`.
- Expert tensor parallel size: `1`.
- Sequence parallel: `true`.
- Sequence length: `4096`.
- Tokenizer: Qwen3-30B local model path.
- Placeholder checkpoint: `LEAD_APPROVED_CHECKPOINT_REQUIRED_NOT_SET`.
- `training_loop_called=false`, `optimizer_step_called=false`,
  `weights_loaded=false`.

Validation route/fail-closed behavior passed:

- Remote train-only view: `84` train shards, `0` valid shards, `0` test shards.
- Source contains `has_validation_data = False`.
- Source returns `do_validation=has_validation_data`.
- Expected validation disposition: disabled. Any validation phase entry in a
  later run is a fail-closed condition.

Resource probe passed:

- 8 GPUs visible.
- GPU type: NVIDIA H200.
- Each GPU reported `143771` MiB total memory and `0%` utilization during the
  probe.

## Residual Classification

Residual import checks are recorded in
`manifests/remote_no_training_preflight_probe.json`.

| Module | Status | Classification |
|---|---|---|
| `nvidia_resiliency_ext` | `RESIDUAL_FAIL` | Missing in this no-training route. It was not imported by the no-training config probe, but should be treated as a later training-runtime residual to resolve or explicitly disable before any training task. |
| `multi_storage_client` | `RESIDUAL_FAIL` | Diagnostic import name fails. |
| `multistorageclient` | `PASS`, version `0.49.0` | The installed `multi-storage-client` distribution exposes this package path in task337 runtime target. |

These residuals do not authorize training. The next lead-gated task should make
an explicit decision on `nvidia_resiliency_ext` before any optimizer step.

## Launch Handoff

The later launch contract is written to:
`/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/manifests/later_launch_contract.json`.

The template script is written to:
`/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/config/run_later_training_TEMPLATE_DO_NOT_RUN.sh`.

The template was not run.

Required future placeholders remain unset by design:

- `TASK339_TRAIN_ITERS`
- `TASK339_LR`
- `TASK339_MIN_LR`
- `TASK339_LR_WARMUP_ITERS`
- `TASK339_SAVE_INTERVAL`
- `SUPER3_M1_PRETRAINED_CHECKPOINT`

Recommendation: task339 evidence supports assigning a separate lead-gated
runtime/training-readiness task that first resolves or waives the
`nvidia_resiliency_ext` residual and supplies a lead-approved checkpoint path.
Do not release task310 or 30B training from this report alone.

## Boundary Confirmation

No training loop, optimizer step, benchmark eval, AIME/task243 eval, export,
endpoint, promotion, task255 reuse, AIME2025 train row use, shared deletion or
mutation, main push, merge, or self-merge was performed.
