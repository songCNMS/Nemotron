# task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1 - NemTron Bridge runtime probe

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Background

#337/task263 merged blocker evidence showing the CPU worker runtime lacks
`megatron`, `megatron.bridge`, and `nemo`; Bridge import rc was `1` and the
fail-closed preflight rc was `2`. That evidence is valid blocker evidence only.
It does not prove Qwen3-4B base-load/import, authorize training, or change the
global Qwen AIME `NO-GO/HOLD` gate.

Project rules still require code/debug runs on remote node `NemTron`, code
synced to `/root` before debug, Qwen3-4B pilot path
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, and no deletion
of existing files under `/mnt/cephfs/data/processing/lei.song`.

## Goal

Run the task263 Bridge import and fail-closed preflight probes in a task-owned
NemTron/NeMo/Megatron-Bridge environment, or report the exact resource/runtime
blocker that prevents doing so.

## Scope

- Start from current `origin/main` after #337 merge commit
  `8fb1a1cb042fca0a0ca3491363fb0e5616909010`.
- Use Qwen3-4B only:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Sync the repo to a task-owned `/root/task268_*/Nemotron` path before any
  remote probe.
- Reuse the #337/task263 generated Bridge import/preflight scripts or a
  task268 wrapper that preserves their fail-closed semantics.
- Run only import/checkpoint-load/preflight proof steps in an environment with
  `megatron.bridge` and `nemo` available, such as
  `nvcr.io/nvidia/nemo:26.02.nemotron_3_super` or an equivalent approved
  NemTron/NeMo runtime.
- Produce a manifest with commands, environment, image/module versions, paths,
  return codes, logs, base file hashes, and any converted/imported checkpoint
  artifact path if one is created.

## Boundaries

- Do not launch SFT training, nonzero-LR smoke, task243/AIME eval, export,
  endpoint, promotion, task255 reuse, 30B/8-GPU, or any full-scale job.
- Do not train on or include AIME2025 prompts or labels.
- Do not delete or overwrite existing shared files under
  `/mnt/cephfs/data/processing/lei.song`; write only task-owned outputs.
- Do not claim go/no-go pass. A future Qwen3-4B pilot still needs lead clearance,
  candidate artifacts, and same-harness FT-vs-base comparison against the
  accepted base score `11/30`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1`.
- PR to `main` if repo scripts/docs/status change; artifact-only blocker report
  by mailbox is acceptable if no repo changes are needed.
- Task-owned local output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/`.
- Task-owned remote output/root paths under `/root` and, only if needed,
  `/mnt/cephfs/data/processing/lei.song/task268_*`.
- Mailbox report with:
  - branch/head/PR or artifact-only status;
  - exact NemTron host/container/image/env used;
  - exact commands run and exit codes;
  - Bridge import/checkpoint-load proof or exact blocker;
  - log, manifest, inventory, and checksum paths;
  - base Qwen3-4B hashes and checkpoint/import artifact paths;
  - explicit boundary confirmation.

## Acceptance Criteria

- PASS: Bridge import or equivalent checkpoint-load preflight succeeds in a
  NemTron/NeMo/Megatron-Bridge environment and produces positive load proof that
  can gate a later bounded Qwen3-4B smoke.
- BLOCK: an exact resource/runtime blocker is reported with logs and the next
  smallest remediation path.
- FAIL: any training/eval/promotion/AIME2025-train-data/30B action occurs or the
  preflight can silently proceed without positive base-load/import proof.

## Current Evidence

- Disposition: `NEMTRON_BRIDGE_RUNTIME_BLOCKED`.
- Repo-visible summary:
  `workspace/tasks/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/runtime_probe_report.md`.
- Full local artifact report:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/reports/task268_bridge_runtime_report_20260602T002457Z.md`.
- Manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/task268_bridge_runtime_manifest_20260602T002457Z.json`.
- Artifact inventory:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/artifact_inventory_20260602T002457Z.sha256`.
- Exact blocker: Docker client exists but cannot connect to
  `/var/run/docker.sock`; local Python runtime still lacks
  `megatron`/`megatron.bridge`/`nemo`, so the Bridge import fails closed and no
  positive base-load/import proof exists.
- Checksum note: the earlier `20260602T002335Z` artifact set had a
  self-referential manifest/report checksum mismatch because those files were
  hashed before their final rewrite. The helper was fixed to keep manifest and
  report hashes in the inventory only, and the `20260602T002457Z` inventory
  validates with `sha256sum -c`.
