# task270_qwen_aime_v11_nemtron_runtime_route_audit_s1 - NemTron runtime route audit

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=0 -->

## Background

#338/task268 merged blocker evidence for Qwen3-4B Bridge import/checkpoint-load
preflight. The corrected run `20260602T002457Z` reported
`NEMTRON_BRIDGE_RUNTIME_BLOCKED`: Docker daemon unavailable for
`nvcr.io/nvidia/nemo:26.02.nemotron_3_super`, local `megatron`/`nemo` missing,
Bridge import rc `1`, fail-closed preflight rc `2`, and no positive
Bridge/checkpoint-load proof.

The next gate is not training. It is finding a task-owned NemTron/NeMo/
Megatron-Bridge runtime route that can rerun the Bridge import and fail-closed
preflight, or confirming the exact resource blocker that requires external
coordination.

## Goal

Audit available project/runtime paths and produce a concrete, bounded route to
rerun task268 Bridge import/preflight in a valid NemTron/NeMo/Megatron-Bridge
environment, or a precise blocker report if no route is available.

## Scope

- Review project rules, task268 artifacts, runbooks, and known NemTron access
  paths.
- Identify whether any of the following is available:
  - Docker daemon access for `nvcr.io/nvidia/nemo:26.02.nemotron_3_super`;
  - a preloaded/launchable NeMo/Megatron-Bridge image or container;
  - an existing module/venv/container runtime on `NemTron` with
    `megatron.bridge` and `nemo`;
  - an LTP/OpenPAI job route that can run a no-training import/preflight probe.
- Produce exact commands, host/container/image assumptions, required sync paths,
  output paths, and permissions needed for a future task268 rerun.
- If blocked, state the smallest external action needed, such as enabling
  Docker daemon, supplying a specific image/runtime, or granting access to a
  known container route.

## Boundaries

- Do not run SFT training, nonzero-LR smoke, task243/live AIME eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, 30B/8-GPU, or any
  full-scale job.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.
- Read-only runtime probes are acceptable only if they do not launch training
  or mutate shared artifacts; record exact commands and outputs.
- Do not merge PRs or push main.

## Expected Output

- Branch:
  `intern_nemotron_worker_5/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1`.
- PR only if repo-visible runbook/docs/status change; otherwise mailbox-only
  report is acceptable.
- Report by mailbox with:
  - branch/head/PR or artifact-only status;
  - exact runtime route or exact blocker;
  - command plan for rerunning task268 Bridge import/preflight;
  - required image/module/container details;
  - permissions/resource blockers;
  - output and checksum plan;
  - explicit boundary confirmation.

## Acceptance Criteria

- PASS: a concrete no-training route exists to rerun task268 import/preflight in
  a valid NemTron/NeMo/Megatron-Bridge runtime.
- BLOCK: no route exists with current permissions/resources, and the report
  identifies the exact external action needed.
- FAIL: any training/eval/promotion/AIME2025 train-data/30B action occurs.
