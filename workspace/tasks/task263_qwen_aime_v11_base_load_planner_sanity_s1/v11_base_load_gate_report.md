# task263 V11 Base-Load Gate Report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Disposition

`NEMTRON_NEMO_RUNTIME_BLOCKED`.

The task-owned `/root` sync and live import probe are reproducible, but the
current runtime does not contain `megatron`, `megatron.bridge`, or `nemo`. The
Bridge import proof cannot be produced in this environment, and the generated
fail-closed preflight correctly blocks before any training.

## Branch And Base

- Worker branch:
  `intern_nemotron_worker_2/task263_qwen_aime_v11_base_load_planner_sanity_s1`.
- Refreshed base: `origin/main`
  `5e839d4a911c8a0c1c55e6adc606d325b9d17717`.
- Task-owned NemTron sync path:
  `/root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_20260601T234056Z/Nemotron`.
- Local output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/`.

## Commands

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rebase origin/main
rsync -a --exclude .git /work-agents/intern_nemotron_worker_2/Nemotron/ /root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_20260601T234056Z/Nemotron/
python3 -m py_compile workspace/tasks/task263_qwen_aime_v11_base_load_planner_sanity_s1/build_task263_v11_base_load_gate_bundle.py
git diff --check
python3 workspace/tasks/task263_qwen_aime_v11_base_load_planner_sanity_s1/build_task263_v11_base_load_gate_bundle.py --nemtron-run-root /root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_20260601T234056Z --synced-repo /root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_20260601T234056Z/Nemotron --run-bridge-probe --run-fail-closed-preflight
```

Generated scripts:

- `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/scripts/run_bridge_import_probe_20260601T234421Z.sh`
- `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/scripts/run_fail_closed_preflight_20260601T234421Z.sh`

## Artifact Paths

- Manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/manifests/v11_base_load_gate_manifest_20260601T234421Z.json`
- Report:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/reports/task263_v11_base_load_gate_report_20260601T234421Z.md`
- Artifact inventory:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/manifests/artifact_inventory_20260601T234421Z.sha256`
- Bridge import probe log:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/logs/bridge_import_probe_20260601T234421Z.log`
- Fail-closed preflight log:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/logs/fail_closed_preflight_20260601T234421Z.log`

## Checksums

```text
59d7d8c8ac7e057ec87aa9d8beec9c1ee1c17677832cf75ae49897bfd5737f61  /work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/manifests/v11_base_load_gate_manifest_20260601T234421Z.json
d298331298d9fea55c39d410fd400e4ecaea3c85fbdb3f87d2eee6d1d02041f7  /work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/reports/task263_v11_base_load_gate_report_20260601T234421Z.md
dc650f9b13524d25678546036e85c9c79b3b85f92eda27c5c3304246d1d9058a  /work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/scripts/run_bridge_import_probe_20260601T234421Z.sh
ce0777ce930c436540d8264d5f4b98e8e2e00b0c2fa2f681e73ba103cbee0739  /work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/scripts/run_fail_closed_preflight_20260601T234421Z.sh
c766c461085ec79bc61c26da68c188e719d1508e40c808816a830ab88a1bf408  /work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/logs/bridge_import_probe_20260601T234421Z.log
f1acd2ae4b669928b9448c3d0a31a07bd96de712a0f05e6becdc141ab89088ed  /work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/logs/fail_closed_preflight_20260601T234421Z.log
```

## Base Path Evidence

Base model:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.

Recorded base core hashes:

- `config.json`:
  `5beea1a4a34c62782bfb2f911c606741a3bab8f92d80a118fa053c28af12e8ba`
- `tokenizer_config.json`:
  `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3`
- `tokenizer.json`:
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`
- `model.safetensors.index.json`:
  `d6c42883a895dfef5b0080ed2116a1bcd764f558406b98923d675978a1abf29c`

The three safetensor shards are present by size with total size
`8044982000` bytes.

## Blocker Evidence

Bridge import probe:

```text
ModuleNotFoundError: No module named 'megatron'
BRIDGE_IMPORT_RC=1
```

Fail-closed preflight:

```text
TASK263_FAIL_CLOSED_PREFLIGHT=BLOCK
- megatron is missing
- megatron.bridge import probe errored: ModuleNotFoundError: No module named 'megatron'
- no Bridge-approved import proof or positive checkpoint-load line found
- Bridge import command did not complete with rc=0
```

Smallest remediation: rerun the generated Bridge import probe inside
`nvcr.io/nvidia/nemo:26.02.nemotron_3_super` or another task-owned
NemTron/NeMo environment where `megatron.bridge` is installed. Then rerun the
fail-closed preflight and proceed only if it passes and lead clears the bounded
smoke step.

## Nonzero-LR Plan

Plan-only schedule, blocked before training:

- Resource shape: 1 node / 2 GPUs, `CUDA_VISIBLE_DEVICES=0,1`.
- `train_iters=2`.
- `global_batch_size=2`.
- `micro_batch_size=1`.
- `seq_length=8192`.
- `optimizer.lr=5e-6`.
- `scheduler.min_lr=5e-7`.
- `scheduler.lr_warmup_iters=0`.
- `scheduler.lr_decay_iters=20`.
- First logged step expected LR: `5e-6`.

For any later launch, train iterations must be recomputed from actual V11
packed rows as `max(2, ceil(packed_train_rows / global_batch_size))`. The
preflight aborts on missing import/load proof, missing packed rows,
`train_iters < 2`, `lr_decay_iters <= train_iters`, zero first logged LR,
NaN/Inf, or random-init-scale first loss/PPL.

## Boundary Confirmation

No SFT training, export, endpoint serving, live AIME/task243 eval,
promotion/go-no-go claim, task255 checkpoint/export reuse, AIME2025 train
prompt/label use, 30B/8-GPU launch, or shared deletion was performed.
