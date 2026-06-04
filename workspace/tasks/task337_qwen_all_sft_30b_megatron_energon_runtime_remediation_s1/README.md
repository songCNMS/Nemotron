# task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1 - Runtime remediation for Qwen3 MoE Bridge import

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=88 -->

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

## Acceptance

- Worker_2 acceptance mailbox:
  `task337-acceptance-4db10e07-20260604T1001Z`.
- Worker branch:
  `origin/intern_nemotron_worker_2/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1`.
- Acceptance head: `4db10e0783823c8f6087748718d40e729879554d`.
- Base: `origin/main` `373d162d63a66f2dac6b94c43917be9c249cd83f`.
- Lead docs imported from:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `4fc5e1d3`.
- PR: none yet; acceptance branch/mailbox only.
- Worker_2 confirmed no runtime mutation was performed in the acceptance step.

## Closeout Under Review

- Worker_2 closeout mailbox:
  `task337-closeout-fb6ba0e7-20260604T1015Z`.
- PR: #400 `https://github.com/songCNMS/Nemotron/pull/400`.
- PR head: `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`, `OPEN`,
  non-draft, base `main`, `CLEAN`/`MERGEABLE`.
- Disposition reported: `PASS_RUNTIME_REMEDIATED`.
- Report:
  `workspace/tasks/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/qwen3_moe_runtime_remediation_report.md`.
- Report sha256:
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.
- Artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z`.
- Gate state: #400/task337 remains HOLD pending task338 independent review.
  task310/all-SFT 30B launch/training/eval/export/endpoint/promotion remain
  HOLD.

## Lead Gate

- Independent review: task338/#401 merged at `2026-06-04T11:05:56Z` with merge
  commit `d87320cfd0f2cedb786b0588f9ee7b564c467ee1` from reviewed head
  `422ca360447e083f0e08c53b446653ad44d51707`.
- Post-#401 recheck: #400 exact head
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`, `OPEN`, non-draft, base
  `main`, `CLEAN`/`MERGEABLE`.
- Post-#401 diff scope remains worker_2 status plus task337 README/history/
  task_knowledge/report only; `git diff --check origin/main...origin/pr/400`
  passed.
- Report sha256 remains
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.
- Lead already spot-checked assigned artifact root checksums and markers:
  baseline `TASK337_IMPORT_PROBE=BLOCK_MISSING_MEGATRON_ENERGON`; final
  `TASK337_IMPORT_PROBE=PASS_QWEN3_MOE_IMPORT` and
  `TASK337_SYMBOL_PROBE=PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- Decision: `APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE`.
- Meaning: accept #400/task337 as no-training runtime import remediation
  evidence only.
- #400 may self-merge only if exact head `fb6ba0e7` remains `OPEN`/`CLEAN`.
- Still blocked: task310/all-SFT 30B launch/training/eval/export/endpoint/
  promotion. Next allowed lead action after #400 lands is a bounded
  task335-equivalent no-training launch preflight rerun using the approved
  task337 runtime route or equivalent checksummed recreation.

## Merge Closeout

- Worker_2 merge closeout mailbox:
  `intern_nemotron_worker_2_task337_pr400_merge_closeout_20260604T111108Z`.
- #400 merged at `2026-06-04T11:11:08Z`.
- Merge commit: `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Merged evidence head: `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.
- Worker_2 branch-only closeout head:
  `7cae0b9bfc351544a41158384aad59f29adbb8a8`.
- Merge scope from parent `d87320cfd0f2cedb786b0588f9ee7b564c467ee1` is
  worker_2 status plus task337 README/history/task_knowledge/report only;
  `git diff --check` passed.
- task337 is complete as no-training runtime import remediation evidence only.
- task310/all-SFT 30B launch/training/eval/export/endpoint/promotion remain
  HOLD pending task339 no-training launch preflight rerun and later lead gate.
