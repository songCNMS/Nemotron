# task242_qwen_aime_v10_planner_smoke_s1 - Qwen AIME V10 planner and smoke scripts

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=0 -->

## Background

The team must use Qwen3-4B for cheap pilot/debug before spending 30B/8-GPU scale. Existing project rules say code/debug runs happen on remote node `NemTron`, code must be synced to `/root` before debug, and the small debug checkpoint is `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.

## Goal

Expose the V10 data strategy through planner/training scripts and produce safe smoke launch scripts for a Qwen3-4B pilot. The planner must enforce the same base-vs-FT eval gate before any 30B scaling is proposed.

## Scope

- Own planner changes in `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py` and related training-planner surfaces.
- Add or update generated-script support for the V10 strategy created by worker_1.
- Provide a Qwen3-4B pilot plan using `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Preserve Qwen3-30B-A3B train-entrypoint routing for any later scale-up, but do not launch or spend 30B/8-GPU scale in this task.
- Make smoke scripts record local CPU prep, sync-to-`/root` on NemTron, and safe shared-storage behavior.

## Boundaries

- Do not push `main` or self-merge.
- Do not launch full 30B/8-GPU training.
- Do not delete existing files in `/mnt/cephfs/data/processing/lei.song`.
- Do not judge pilot success without worker_3 same-harness base score.
- Coordinate with worker_1 if planner changes need data-strategy names that are still in review.

## Expected Output

- Worker branch: `intern_nemotron_worker_2/task242_qwen_aime_v10_planner_smoke_s1`.
- PR to `main` after local validation.
- A planner report in this task directory with generated command examples, pilot resource assumptions, expected artifact paths, and 30B scale-up hold conditions.
- Mailbox report with branch, head SHA, PR URL, files touched, tests/checks run, and resource blockers.

## Acceptance Criteria

- Planner can generate a Qwen3-4B V10 pilot bundle without requiring 30B weights.
- Planner manifest records base model path, candidate FT output path, corrected AIME evaluator config, and base-vs-FT non-regression rule.
- Scripts fail closed if decontamination corpus is missing for V10 hard-math data.
- First measurable go/no-go gate is encoded in the run plan: compare Qwen3-4B base and Qwen3-4B V10 FT under the same corrected AIME25 smoke protocol before any 30B proposal.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Depends on: worker_1 V10 sidecar interface, worker_3 baseline/eval protocol, worker_5 runbook verification
