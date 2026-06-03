# task316_qwen_all_sft_repair_candidate_plan_s1 - Qwen all-SFT repair candidate plan

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=78 -->

## Background

Task310 produced a salvage checkpoint candidate, not a clean `PASS_TRAINING`:
the train loop reached 35/35 with finite loss, but validation hung and the run
was terminated with `train_rc=1`. Task311 then showed mixed benchmark evidence:
AIME2025 and HMMT improved, but MMLU-Pro regressed by 2 rows.

The pipeline needs a concrete next candidate plan before any additional
training or eval can be authorized.

## Goal

Analyze task308-task311 evidence and propose a fail-closed next repair plan for
the all-SFT Qwen3-30B pipeline, including whether the next action should be
checkpoint/validation repair, data blend repair, training schedule change,
evaluator/protocol repair, or docs-only fail closeout.

## Scope

- Review task310 training logs, checkpoint salvage evidence, validation hang
  residuals, LR/loss/step configuration, and checkpoint handoff.
- Review task309 packed-data contract and task308 inventory constraints.
- Incorporate task311 benchmark metrics:
  - AIME2025 FT 16/30 vs base 15/30;
  - HMMT FT 11/30 vs base 9/30;
  - MMLU-Pro FT 6756/12032 vs base 6758/12032.
- Coordinate with task314 findings if available; otherwise clearly mark
  assumptions.
- Produce a concrete next-task recommendation with exact gates, artifacts,
  commands/env requirements, risk controls, and stop conditions.

## Boundaries

- Planning/review only; no training, new eval, packing, export, endpoint,
  promotion, merge, main push, task255 reuse, AIME2025 train data, or shared
  deletion.
- Do not rewrite task310 or task311 branches.
- Any proposed training/eval must be expressed as a later lead-gated task, not
  launched here.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task316_qwen_all_sft_repair_candidate_plan_s1`.
- Report:
  `workspace/tasks/task316_qwen_all_sft_repair_candidate_plan_s1/all_sft_repair_candidate_plan.md`.
- Mailbox report with branch/head/PR or blocker, evidence reviewed, proposed
  next plan, exact go/no-go gates, and residual risks.

## Acceptance Criteria

- `APPROVE_PLAN`: recommendation is concrete, bounded, and consistent with
  task308-task311 evidence and no-promotion boundaries.
- `REQUEST_CHANGES`: plan misses key artifacts, gates, risk controls, or
  dependencies.
- `BLOCK`: evidence is insufficient to recommend any safe next action.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Review targets: task308, task309, task310, task311/#371
- Gate state: no further training/eval authorized.
