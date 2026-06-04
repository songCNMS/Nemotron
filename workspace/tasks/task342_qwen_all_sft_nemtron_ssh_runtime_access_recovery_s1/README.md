# task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1 - NemTron access recovery

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_4,SESSION=91 -->

## Background

task341/#404 merged as `BLOCK_TRAINING_READINESS` evidence. The all-SFT 30B
pipeline is not training-ready because the required `NemTron` SSH route fails
with `channel 0: open failed: connect failed: Connection refused`.

This blocks the task-owned `/root` sync/probe, live task337 runtime validation,
task298 candidate checkpoint validation, and the `nvidia_resiliency_ext`
decision needed before any training task can be considered.

## Goal

Independently recover or precisely classify the `NemTron` SSH/runtime access
route without running training or eval.

Return exactly one disposition:

- `PASS_NEMTRON_ACCESS_RESTORED`: the `NemTron` route works from the worker
  environment, `/root` is reachable, the task337 runtime target, task298
  checkpoint candidate, and task339 train-only data roots are readable, and a
  no-training Python import probe can run.
- `REQUEST_CHANGES`: evidence is incomplete, inconsistent, or missing command/
  environment/log/checksum detail.
- `BLOCK_NEMTRON_ACCESS`: access remains unavailable or remediation requires
  coordinator/user credentials, LTP job repair, system/network change, shared
  mutation, or any other action outside worker boundaries.

## Required Checks

- Start from current `origin/main`
  `371aea491776cc258e1cbb59a081d28be0530438`.
- Inspect the current `NemTron` SSH configuration and proxy route without
  exposing private key material.
- Run and log a simple connectivity probe:
  `ssh -o ConnectTimeout=10 NemTron 'hostname; date -u +%Y-%m-%dT%H:%M:%SZ'`.
- If the route works, create a task-owned `/root` run directory and log:
  - `hostname`, UTC timestamp, and `nvidia-smi` GPU visibility;
  - existence/readability of task337 runtime target:
    `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`;
  - existence/readability of task298 checkpoint candidate:
    `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`;
  - existence/readability of task339 train-only data root:
    `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/input/packed_qwen_task333_train_only_contract`;
  - Python import probe for `megatron`, `megatron.bridge`,
    `megatron.energon`, `nvidia_resiliency_ext`, `multi_storage_client`, and
    `multistorageclient` using the intended task337 runtime path.
- If the route fails, classify whether the failure appears to be proxy/LTP,
  target host/port, auth, DNS/host alias, or unknown; include exact command,
  return code, stderr, and any non-secret SSH config fields needed for
  coordinator escalation.
- If any remediation appears possible only by mutating shared/system/network
  state, do not perform it; report the proposed action and required owner.

## Boundaries

- No optimizer steps, training loop, benchmark eval, AIME/task243 eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion or
  mutation, destructive SSH config changes, main push, merge, or self-merge.
- Do not delete or mutate files under `/mnt/cephfs/data/processing/lei.song` or
  any shared model/data/checkpoint roots.
- Do not change product/source code. Task-local helper scripts and task docs are
  allowed if needed for reproducible evidence.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1`.
- Report:
  `workspace/tasks/task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1/nemtron_access_recovery_report.md`.
- Task-owned local artifact root with commands, logs, SSH route summary with no
  secrets, manifests/checksums, and PASS/BLOCK disposition.
- Mailbox closeout with branch/head/PR or blocker, artifact paths, commands/env,
  exact residuals, and whether task341 can be rerun.

## Assignment

- Team: `nemotron`.
- Team lead: `intern_nemotron_lead`.
- Worker: `intern_nemotron_worker_4`.
- Base: `origin/main` `371aea491776cc258e1cbb59a081d28be0530438`.
- Gate state: task310/all-SFT 30B launch/training/eval/export/endpoint/
  promotion remain HOLD pending this task and a later rerun of task341 or
  equivalent no-training checkpoint handoff.
