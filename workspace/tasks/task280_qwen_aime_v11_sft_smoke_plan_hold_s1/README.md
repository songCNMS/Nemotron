# task280_qwen_aime_v11_sft_smoke_plan_hold_s1 - bounded SFT smoke plan hold

<!-- METADATA:STATUS=PlanningHold,ASSIGNEE=intern_nemotron_worker_1,SESSION=1 -->

## Background

Coordinator Session 43 authorizes attempting the full pipeline, but nonzero-LR
Qwen3-4B SFT smoke/training may be assigned only after task278 no-training
preflight passes and task279 review is processed. This task prepares the exact
smoke plan without running it.

## Goal

Prepare a no-run, fail-closed bounded Qwen3-4B SFT smoke plan that lead can
release later if task278/task279 pass.

## Scope

- Do not run training or launch scripts.
- Draft the exact candidate command/config plan for a minimal Qwen3-4B
  nonzero-LR SFT smoke using task276 packed root.
- Include intended LR, max train steps, global/micro batch, sequence length,
  packed root, output root, checkpoint naming, log paths, and stop criteria.
- Include fail-closed checks proving AIME2025 prompt/label rows are not
  trainable data and task255 is not used.
- Include how to avoid deleting or overwriting shared paths.

## Boundaries

- This is not the training execution task.
- Do not train, run nonzero-LR smoke, live canary, AIME/task243 eval, export,
  endpoint, promote, reuse task255, use AIME2025 train data, delete shared
  files, merge, push main, or use 30B/8-GPU.

## Expected Output

- Mailbox report and optional docs branch with exact no-run plan, commands/env,
  artifacts to expect if released, and blockers.

## Acceptance Criteria

- PASS: plan is exact enough to run after lead release and includes all
  safeguards.
- REQUEST-CHANGES: plan is incomplete or ambiguous.
- BLOCK: no safe bounded Qwen3-4B smoke route exists from current evidence.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Gate: planning only; execution HOLD until explicit lead release after
  task278/task279 pass.

## Current Worker State

- Branch:
  `intern_nemotron_worker_1/task280_qwen_aime_v11_sft_smoke_plan_hold_s1`.
- Base:
  `origin/main` at `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`.
- Task docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `be45766c6fc127b0ba00e784d84810a378b3e8e4`.
- Status: accepted; preparing no-run bounded SFT smoke plan.
- Report:
  `workspace/tasks/task280_qwen_aime_v11_sft_smoke_plan_hold_s1/qwen3_4b_v11_sft_smoke_plan_hold_report.md`.
- Disposition: `PLAN_READY_HOLD_TASK278_TASK279_RELEASE`.
- Execution remains HOLD until task278 no-training preflight is approved,
  task279 independent review is processed, and lead explicitly releases a
  nonzero-LR Qwen3-4B smoke execution task.
