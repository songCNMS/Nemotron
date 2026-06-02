# task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1 - Bridge runtime remediation preflight

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=74 -->

## Background

Session 74 task278 attempted the first no-training Qwen AIME V11
config/import preflight from the accepted task276 packed root. task279
independently approved #347 only as blocker evidence:

`CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE`

The packed-data, Qwen chat contract, training-pipeline contract,
fail-closed guard, HF config/tokenizer import, and no-AIME train-leakage
checks passed. The blocker is the missing usable NeMo/Megatron-Bridge runtime
route for the training-stack import path.

The accepted packed root remains:

`/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`

The Qwen3-4B path remains:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

The accepted corrected AIME2025 base comparator remains `11/30 =
0.36666666666666664`.

## Goal

Find or create a documented, task-owned no-training NemTron/NeMo/
Megatron-Bridge runtime route that can rerun the task278 style config/import
preflight against task276 packed data and Qwen3-4B without starting
optimization.

## Scope

- Start from current `origin/main` after #347 if it has merged; otherwise use
  #347 exact head
  `b7e544100ac13eaa908a9d1af6fafaf599bc3310` as blocker evidence only.
- Reconcile the contradiction between coordinator Session 40 positive import
  evidence and task278 current missing-runtime evidence.
- Sync code to a task-owned `/root` run directory on `NemTron` before any
  remote debug command.
- Probe only no-training symbols/imports/config resolution/data readability.
- If environment remediation is attempted, keep it user-site or task-owned,
  reversible, documented, and non-destructive. Do not change system site
  packages.
- Re-run or extend the task278 preflight only if the route cannot start a
  training loop or optimizer step.
- Carry task276 sparse split risk explicitly: valid has one packed row and test
  has zero rows.

## Required Evidence

Report by mailbox and branch/PR if docs/status/report files change:

- branch/head/PR or exact blocker;
- exact host, shell, Python path, environment variables, code revision, and
  `/root` sync path;
- commands and logs for runtime symbol probes, config/import preflight, data
  readability, and fail-closed no-training guards;
- task276 packed root, split manifest, metadata, evidence manifest, and shard
  checksum references;
- Qwen3-4B path and checkpoint import/load proof if the route passes;
- comparison to Session 40 evidence root
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`;
- exact package/module blocker if the route still fails;
- proof that no training loop, optimizer step, training checkpoint save,
  export, endpoint, live canary, or AIME/task243 eval ran.

## Boundaries

- Do not train, run nonzero-LR smoke, run live canary, run AIME/task243 eval,
  export, launch endpoint, promote, reuse task255, put AIME2025 prompt/label
  rows into training, delete shared files, push main, merge, or use 30B/8-GPU.
- Do not delete or overwrite anything under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not modify system site packages. If the only route requires system-level
  install, privileged service changes, scheduler credentials, or GPU training
  launch, stop and report the exact blocker.

## Acceptance Criteria

- PASS: no-training Bridge/config/import preflight succeeds with complete
  commands, logs, task-owned artifact paths, Qwen3-4B import/load proof, and
  fail-closed confirmation.
- REQUEST-CHANGES: evidence is incomplete, stale, or ambiguous.
- BLOCK: no usable NeMo/Megatron-Bridge runtime route exists without forbidden
  system changes or training/eval execution.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task247, task262, task270, task276, task278, task279
- Related PR: #347
- Current gate: no-training runtime remediation/config-import preflight only.
