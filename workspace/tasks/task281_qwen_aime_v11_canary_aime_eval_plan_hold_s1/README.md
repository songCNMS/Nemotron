# task281_qwen_aime_v11_canary_aime_eval_plan_hold_s1 - canary and AIME eval plan hold

<!-- METADATA:STATUS=PlanningHold,ASSIGNEE=intern_nemotron_worker_3,SESSION=74 -->

## Background

The pipeline sequence requires a non-AIME canary/completion-retention check
before corrected AIME2025 FT-vs-base comparison. No candidate FT artifact exists
yet in Session 74, so this task prepares the evaluation plan and readiness
criteria without running canary or AIME evaluation.

## Goal

Prepare the exact non-AIME canary and corrected AIME2025 same-harness comparison
plan for a future Qwen3-4B V11 FT artifact.

## Scope

- Reuse task264/task273 accepted eval-gate continuity.
- Preserve accepted base comparator: Qwen3-4B base `11/30 =
  0.36666666666666664` under the corrected AIME2025 harness.
- Define canary prompt source, non-AIME/non-train proof, metrics, retained
  completion artifacts, and pass/fail rules.
- Define AIME comparison command/protocol requiring same harness, same base
  model path, same scoring normalization, and FT score >= base before any
  promotion discussion.

## Boundaries

- Do not run live canary, AIME/task243 eval, training, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, shared deletion, merge, push
  main, or 30B/8-GPU.

## Expected Output

- Mailbox report and optional docs branch with exact no-run canary/AIME plan,
  artifact retention schema, metrics, and blockers.

## Acceptance Criteria

- PASS: future evaluation can be launched only after lead release and has clear
  same-harness/base-vs-FT non-regression criteria.
- REQUEST-CHANGES: plan omits base comparator, canary retention, or AIME data
  boundaries.
- BLOCK: current harness cannot support required same-harness comparison.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Gate: planning only; no live canary or AIME eval until candidate FT artifact
  and lead release exist.
