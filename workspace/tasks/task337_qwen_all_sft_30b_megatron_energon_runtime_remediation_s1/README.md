# task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1 - Runtime remediation for Qwen3 MoE Bridge import

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Background

task335/#398 merged as no-training fail-closed blocker documentation. The
accepted blocker is that the NemTron current route can import base Megatron,
Megatron Bridge, Torch, OmegaConf, and task-local Qwen code, but cannot import
the Qwen3 MoE Bridge recipe:

`megatron.bridge.recipes.qwen.qwen3_moe` ->
`ModuleNotFoundError("No module named 'megatron.energon'")`.

The user requested a full all-SFT Qwen pipeline, but task310/all-SFT 30B launch
cannot proceed until this runtime route is repaired or precisely classified and
then rechecked with no-training preflight.

## Goal

Produce a task-owned no-training runtime remediation report that either:

- `PASS_RUNTIME_REMEDIATED`: the same NemTron task-owned `/root` sync route can
  import `megatron.bridge.recipes.qwen.qwen3_moe` and required dependencies,
  with exact commands/env/package/source evidence; or
- `BLOCK_RUNTIME_REMEDIATION`: the route cannot be repaired within the allowed
  boundaries, with exact missing package/source/credential/container/runtime
  blocker and recommended next owner.

## Inputs

- Current `origin/main`: `373d162d63a66f2dac6b94c43917be9c249cd83f`.
- 30B model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- task335 artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z`.
- task335 remote route:
  `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z`.
- task335 accepted blocker:
  missing `megatron.energon` when importing
  `megatron.bridge.recipes.qwen.qwen3_moe`.

## Required Checks

- Sync current repo code to a new task-owned `/root` run directory on NemTron
  before remote debug, following project rules.
- Identify the active Python executable, `PYTHONPATH`, user-site path, package
  versions, and import resolution path for `megatron`, `megatron.bridge`,
  `megatron.energon`, `megatron.bridge.recipes.qwen.qwen3_moe`, `nemo`,
  `torch`, `transformers`, and `omegaconf`.
- If installing or copying a missing dependency is needed, do it only in a
  task-owned/user-site/runtime-local way; record exact command, source,
  version/revision, checksum where applicable, and whether it is reproducible.
- Do not mutate shared roots or delete existing files under
  `/mnt/cephfs/data/processing/lei.song`.
- Re-run only no-training symbol/import/config preflight sufficient to prove
  whether the Qwen3 MoE Bridge recipe import blocker is cleared.
- If the remediation succeeds, state whether task335 no-training preflight must
  be rerun from scratch before any training task, and provide the exact command
  handoff.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1`.
- Report:
  `workspace/tasks/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/qwen3_moe_runtime_remediation_report.md`.
- Task-owned local and/or remote output root with logs, manifests, package
  inventory, import probe output, checksums, and command/env transcript.
- Mailbox closeout with branch/head/PR or exact blocker, commands/env, artifact
  paths, pass/fail disposition, and next gate recommendation.

## Boundaries

- No training, optimizer steps, benchmark eval, AIME/task243 eval, export,
  endpoint, promotion, task310 release, task255 reuse, AIME2025 train rows,
  shared deletion/mutation, main push, merge, or self-merge.
- Do not silently downgrade to 4B or switch 30B checkpoint paths.
- Do not use AIME2025 prompts or labels as train data.
- Do not mutate task335 artifacts except by reading/copying into a task-owned
  route if needed for no-training preflight.
- If the only viable fix requires system package installation, container
  credentials, shared-root mutation, or product-code edits, stop and report
  `BLOCK_RUNTIME_REMEDIATION`.

## Acceptance Criteria

- A PASS must prove the exact prior failing import now succeeds in a recorded
  NemTron route and must preserve all no-training boundaries.
- A BLOCK must name the exact missing dependency/source/runtime access issue and
  the safest next remediation path.
- Neither PASS nor BLOCK releases training. A PASS only enables a later
  lead-assigned rerun/equivalent no-training launch preflight.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Base: current `origin/main` `373d162d63a66f2dac6b94c43917be9c249cd83f`
- Gate state: task310/all-SFT 30B training/eval/export/endpoint/promotion
  remains HOLD.
