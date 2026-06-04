# task335 task333 30B launch preflight report

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=BLOCK_LAUNCH_PREFLIGHT,SESSION=2 -->

Generated: 2026-06-04T09:06:44Z

## Disposition

`BLOCK_LAUNCH_PREFLIGHT`.

The no-training Qwen3-30B all-SFT preflight produced a concrete later launch
contract and verified the task333 packed data route, model path, GPU resource
shape, task-owned `/root` sync, and validation fail-closed behavior. The launch
remains blocked because the NemTron runtime cannot import the Qwen3 MoE Bridge
recipe:

`megatron.bridge.recipes.qwen.qwen3_moe` -> `ModuleNotFoundError("No module named 'megatron.energon'")`.

Recommendation: do not assign or launch training until the NemTron runtime
route includes `megatron.energon` and can import the Qwen3 MoE Bridge recipe in
the same task-owned `/root` synced environment. The task-owned train-only data
route and later launch contract can be reused after that runtime blocker is
cleared and lead explicitly releases a training task.

No optimizer step, training loop, eval, export, endpoint, promotion, task310
release, task255 reuse, AIME2025 train row use, shared deletion/mutation, main
push, merge, or self-merge was performed.

## Artifact Roots

| Artifact | Path |
|---|---|
| Local run root | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z` |
| Remote run root | `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z` |
| Remote synced repo | `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/Nemotron` |
| Remote synced head | `76b9ebf98e623cb85075378ca9980ba6ee11c8ed` |
| Local train-only packed root | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/packed_qwen_task333_train_only_contract` |
| Remote train-only packed root | `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/input/packed_qwen_task333_train_only_contract` |
| Final summary | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/manifests/final_summary.json` |
| Remote preflight manifest | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/manifests/remote_no_training_preflight_probe.json` |
| Later launch contract | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/manifests/later_launch_contract.json` |
| Later launch template | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/config/run_later_training_TEMPLATE_DO_NOT_RUN.sh` |

Important checksums:

| File | sha256 |
|---|---|
| `manifests/final_summary.json` | `80a4ddce65f43af87ff269b760db73e5520644b9c528530f2e0df267b9968b6d` |
| `manifests/artifact_checksums.sha256` | `fedeea0f279cd716ed24d7c352a464b010e7577876d75bb5d156ade292665297` |
| `manifests/remote_no_training_preflight_probe.json` | `cf0cacc2a42c3e13a8677edcdfd804f27f97e5b7b1cc2b57a5369304409560d8` |
| `manifests/later_launch_contract.json` | `476b28337526d2057278f82de8e0917b9b33e418d75ac15adda8a8a81c860d6b` |
| `logs/remote_no_training_preflight_probe.log` | `8fa6724d984d38402324f6a3e91e2ba53a95fd11fcb3eb46b9a3dd925616a210` |
| `manifests/train_only_shard_checksums.sha256` | `e5abfbdfebe341b8f346c17f33f4b95ff8fe5750411a40efac1b079fa66bb937` |

Validation commands from the local run root:

```bash
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/train_only_shard_checksums.sha256
```

Both returned `rc=0`.

## Inputs Verified

Model:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

- Exists.
- `model_type=qwen3_moe`.
- Architecture: `Qwen3MoeForCausalLM`.
- Qwen tokenizer chat template present.
- `trust_remote_code=false` for tokenizer/model path probing.

Task333 packed root:
`/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`.

- Full task333 root exposes `84` train shards, `6` valid shards, and `6` test
  shards.
- task333 artifact checksum validation passed with `rc=0`.
- task333 packed shard checksum validation passed with `rc=0`.
- task333 Qwen3-30B packed-data contract was accepted upstream and is recorded
  as pass in the local probe.

## Train-Only Launch View

The later launch should not use the full task333 root directly because the full
root exposes valid/test shards. To preserve the task323/task318
validation-skip route and avoid repeating the task310 validation hang, this
preflight materialized a task-owned train-only packed view with no valid/test
parquet exposure.

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

The task-owned local view was mirrored to `/root` before the remote preflight.
Remote split exposure check passed: `84` train parquet files, `0` valid, `0`
test.

## Remote Runtime Preflight

Remote host: `lg-cmc-b7r201-f08u26-h200-000126`.

Remote code sync rule was followed before NemTron debug:

- Current main synced to
  `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/Nemotron`.
- Synced head recorded as
  `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`.

Remote environment:

```bash
PYTHONPATH=/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/Nemotron/src
SUPER3_M1_AGENTIC_PACKED_DIR=/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/input/packed_qwen_task333_train_only_contract/splits
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
SUPER3_M1_TRAINING_PROFILE=qwen
TOKENIZERS_PARALLELISM=false
WANDB_DISABLED=true
WANDB_MODE=offline
```

Remote no-training preflight command returned `rc=2` and wrote
`TASK335_REMOTE_PREFLIGHT=BLOCK`.

Import checks:

| Module | Status |
|---|---|
| `omegaconf` | PASS |
| `torch` | PASS |
| `megatron` | PASS |
| `megatron.bridge` | PASS |
| `megatron.bridge.training.config` | PASS |
| `nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train` | PASS |
| `nemotron.recipes.super3.stage1_sft.qwen_chat_contract` | PASS |
| `megatron.bridge.recipes.qwen.qwen3_moe` | FAIL: `ModuleNotFoundError("No module named 'megatron.energon'")` |

This is the exact blocker. No package workaround or system mutation was
performed in task335.

## Resource Preflight

NemTron GPU probe passed with 8 idle H200 GPUs:

| GPU count | GPU type | Memory per GPU | Observed utilization |
|---:|---|---:|---:|
| 8 | NVIDIA H200 | 143,771 MiB | 0% |

Each observed GPU reported approximately `4 MiB` used during the probe.

The synthesized resource contract uses 8 GPUs with:

- tensor parallel size `4`;
- pipeline parallel size `2`;
- context parallel size `1`;
- data parallel size `1`;
- expert model parallel size `4`;
- expert tensor parallel size `1`;
- sequence parallel enabled.

This resource shape is a preflight contract only. It does not release 30B
training.

## Validation Fail-Closed Proof

Validation route preflight passed.

- The task-owned remote train-only root has `0` valid parquet files.
- Remote source inspected:
  `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/Nemotron/src/nemotron/recipes/super3/stage1_sft/train.py`.
- Source contains `has_validation_data = False`.
- Source returns `do_validation=has_validation_data`.
- Expected result: `do_validation=false`.

Later launch policy from the contract:

- Any validation phase entry is a fail-closed condition.
- Any nonzero return code, missing checkpoint, non-finite loss, or shared
  mutation is a fail-closed condition.
- No salvage claim is allowed without explicit lead clearance.
- No same-harness eval is part of this task; any future checkpoint requires
  later independent review and explicit eval assignment.

## Later Launch Contract

Contract file:
`/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/manifests/later_launch_contract.json`.

Template script:
`/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/config/run_later_training_TEMPLATE_DO_NOT_RUN.sh`.

The template was not run.

Key fields:

- Entrypoint:
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`.
- Base config:
  `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`.
- Launcher:
  `torchrun --standalone --nnodes=1 --nproc_per_node=8`.
- Packed train root:
  `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/input/packed_qwen_task333_train_only_contract`.
- Sequence length: `4096`.
- Global batch size: `8`.
- Micro batch size: `1`.
- Precision: recipe/container default bf16 mixed precision.
- Validation disposition:
  `disabled_by_train_only_view_no_valid_parquet_do_validation_false`.

Lead-required placeholders remain unset in task335:

- `TASK335_TRAIN_ITERS`.
- `TASK335_LR`.
- `TASK335_MIN_LR`.
- `TASK335_LR_WARMUP_ITERS`.
- `TASK335_SAVE_INTERVAL`.
- a later lead-approved imported Bridge checkpoint path.

## Commands

Helper:
`workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/build_task335_30b_launch_preflight.py`.

Primary command:

```bash
PYTHONPATH=src python3 \
  workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/build_task335_30b_launch_preflight.py \
  --run-root /work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z
```

Recorded command phases:

| Phase | rc | Log |
|---|---:|---|
| `sync_current_main_to_root` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/logs/remote_repo_sync.log` |
| `sync_train_only_data_to_root` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/logs/remote_train_only_data_sync.log` |
| `sync_remote_probe_artifacts` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/logs/remote_probe_artifact_sync.log` |
| `remote_no_training_preflight_probe` | 2 | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/logs/remote_no_training_preflight_probe.log` |
| `fetch_remote_preflight_manifest` | 0 | `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/logs/fetch_remote_preflight_manifest.log` |

Local host:
`lg-cmc-b7r201-n09u29-cpu-000191`.

Remote host:
`NemTron`, resolved during probe to
`lg-cmc-b7r201-f08u26-h200-000126`.

## Boundary Confirmation

Confirmed:

- no optimizer steps;
- no training loop;
- no benchmark eval;
- no AIME/task243 eval;
- no export;
- no endpoint;
- no promotion or go/no-go release claim;
- no task310 release claim;
- no task255 reuse;
- no AIME2025 train rows;
- no shared deletion or mutation, including under
  `/mnt/cephfs/data/processing/lei.song`;
- no main push, merge, or self-merge.

## Next Action

Keep task310/all-SFT 30B training HOLD. The smallest next remediation is a
lead-approved runtime route update that makes
`megatron.bridge.recipes.qwen.qwen3_moe` import successfully in a task-owned
NemTron `/root` sync environment, specifically resolving missing
`megatron.energon`. After that, rerun this no-training preflight or assign a
bounded launch task using the recorded train-only contract and fail-closed
validation policy.
