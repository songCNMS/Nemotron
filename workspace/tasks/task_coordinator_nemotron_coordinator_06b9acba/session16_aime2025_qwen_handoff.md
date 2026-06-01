# Session 16 - AIME 2025 Qwen Pipeline Handoff

## Supervisor Priority

Focus the Nemotron team on improving Qwen fine-tuning performance on the math
benchmark AIME 2025. The promoted result must not score lower than the same base
Qwen model under the same corrected AIME 2025 evaluator and protocol.

## Resource Constraints

- Debug/training runs happen on the remote node `NemTron`.
- Code must be synced to `/root` before debug on `NemTron`.
- Use `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` for cheaper
  debug/pilot runs; other Qwen checkpoints are nearby under the same root.
- Downloads should happen locally on CPU first, then copy to `NemTron`.
- `/mnt/cephfs/data/processing/lei.song` is shared between local CPU and
  `NemTron`; use it if helpful, but never delete existing files.

## Existing Context To Reuse

- `task071_m1_agentic_qwen_scaleup_train_exec` contains the mature Qwen hard-math
  SFT pipeline history, including data prep, packing, training, export, and
  corrected eval artifacts.
- `task075_qwen_v8_export_eval` recorded V8 full corrected eval:
  MMLU-Pro `0.5606715425531915`, AIME25 `0.19666666666666666`, and HMMT
  `13.333333333333334`. V8 missed the AIME25 gate by one correct repeat and
  regressed `aime_06` from V7 `10/10` correct to V8 `0/10`.
- `task076_qwen_v9_aime_recurrence_tuning` recorded the V9 recurrence attempt.
  The checkpoint-root bug was fixed, but corrected V9 still failed targeted
  `aime_06`: parsed `10/10`, correct `0/10`, with wrong answer modes `640` and
  `830`.
- PR #178 and PR #183 are merged. The latest task076 conclusion is to move to a
  focused V10-style run-length DP/counting recurrence sidecar or weighting patch.

## Required Lead Plan

The lead should create standard task docs and assign current workers, not legacy
intern names:

1. Audit current `main` for Qwen AIME pipeline, data-prep, training planner,
   eval gate, and task071/task075/task076 artifacts.
2. Assign one worker to data processing and pipeline refactor for a
   decontaminated AIME-style hard-math sidecar.
3. Assign one worker to training/planner changes and smoke launch scripts.
4. Assign one worker to corrected AIME 2025 base-vs-fine-tuned evaluation,
   score normalization, and same-harness comparison.
5. Assign one worker to independent contamination and regression review.
6. Assign one worker to artifact, runbook, and reproducibility verification.

## Evaluation Gates

- Establish a same-harness base Qwen AIME 2025 score before judging any
  fine-tuned checkpoint.
- Do not train on AIME 2025 labels or prompts except as held-out eval and
  decontamination corpus.
- Use Qwen3-4B for the first cheap pilot/debug path.
- Do not spend full 30B/8-GPU scale until the 4B pilot and corrected AIME smoke
  justify it.
- Promotion requires non-regression on AIME 2025 versus the base model under the
  same evaluator/protocol; improvement is the target.

## Lead Report Expected

Report task ids, assignees, branch/PR plan, baseline protocol, candidate
training plan, first measurable go/no-go gate, artifact paths, and resource
blockers.
