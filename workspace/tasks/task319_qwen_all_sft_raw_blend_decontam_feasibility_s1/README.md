# task319_qwen_all_sft_raw_blend_decontam_feasibility_s1 - Qwen all-SFT raw blend/decontam feasibility

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Background

Task308 and task309 accepted only the constrained task299/V11 seed for task310.
Generic `stage1_sft/data_blend_raw` remained excluded because row counts,
materialized source checksums, supervised-token counts, and decontamination
proof were incomplete. Task311 then showed math benchmark gains but MMLU-Pro
regression, consistent with an overly narrow data seed.

## Goal

Determine whether the broader all-eligible SFT raw blend can be safely
materialized and decontaminated for a later Qwen packed-data repair task.

## Scope

- Review current `stage1_sft/data_blend_raw` registry/configs and task308/task309
  exclusions.
- For each candidate raw SFT source, report:
  - path or dataset id;
  - source revision if available;
  - split;
  - materialization status;
  - row count availability;
  - checksum availability;
  - supervised-token/count feasibility;
  - heldout/decontam risk;
  - eligibility or blocker.
- Define the exact decontam corpus and checks needed before any future packing:
  AIME2025/HMMT/MATH heldouts where relevant, no task255 reuse, no held-out eval
  train rows, and prompt/label exclusion proof.
- If safe, propose a later lead-gated task-owned materialization/decontam
  command plan. Do not perform final packing in this task.

## Boundaries

- No training, optimizer steps, final packing, benchmark eval, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, shared deletion, main push,
  merge, or self-merge.
- Read-only source/registry audit and task-owned lightweight probes only.
- Do not download or mutate large shared datasets without explicit lead release.
- Do not delete shared files under `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1`.
- Report:
  `workspace/tasks/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/raw_blend_decontam_feasibility_report.md`.
- Optional task-owned output root with source inventory tables, probe logs, and
  checksums.
- Mailbox report with branch/head/PR or blocker, source matrix, decontam plan,
  commands/env, exact blockers, and recommendation for a later packing task.

## Acceptance Criteria

- `PASS_FEASIBILITY_PLAN`: raw blend sources have a concrete, safe
  materialization/decontam route for later lead-gated packing.
- `REQUEST_CHANGES`: source inventory or decontam plan is incomplete.
- `BLOCK`: raw sources cannot be safely materialized/decontaminated without
  forbidden data use, missing credentials, shared mutation, or undefined counts.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task308, task309, task316
- Gate state: no final packing or training authorized.
