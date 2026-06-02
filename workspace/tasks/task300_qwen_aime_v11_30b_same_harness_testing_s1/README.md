# task300_qwen_aime_v11_30b_same_harness_testing_s1 - 30B same-harness testing gate

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_3,SESSION=76 -->

## Background

The hard acceptance rule for Qwen AIME remains unchanged: any fine-tuned model
must not score lower than the same base model under the same corrected AIME2025
evaluator/protocol. For 30B, a same-harness base score is required before any
FT checkpoint can be judged.

## Goal

Establish the 30B corrected AIME2025 base score and run the later non-AIME
canary plus corrected AIME2025 FT-vs-base test after a task301 checkpoint is
available.

## Scope

- Depend on task298 for runtime/eval route and exact model path.
- Before judging any FT checkpoint, run or produce the same-harness base
  AIME2025 score for the exact 30B base/instruct checkpoint used by training.
- After task301 provides a checkpoint, run non-AIME canary/completion-retention
  first; only if canary passes, run corrected AIME2025 FT-vs-base testing.
- Include full completions, parser diagnostics, prompt/token cache proof,
  denominator, answer normalizer evidence, command/env, logs, checksums, and
  residuals.
- Use eval-only export/endpoint only if task298 proves it is required for the
  same-harness route; never claim promotion.

## Boundaries

- No training, optimizer steps, task255 reuse, AIME2025 train prompts/labels,
  shared deletion, promotion, production endpoint, main push, merge, or 30B
  scale decisions beyond testing. AIME2025 is held-out eval/decontam only.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1`
- Reports:
  `30b_base_aime2025_report.md`,
  `30b_non_aime_canary_report.md`, and
  `30b_ft_vs_base_aime2025_report.md` as applicable.
- Artifact roots under worker outputs for base score and, after task301,
  canary/FT evaluation with full completions and checksum manifests.
- Mailbox reports at each gate: base score, canary result, corrected AIME
  FT-vs-base result, blockers, and boundary confirmations.

## Acceptance Criteria

- BASE_PASS: exact 30B same-harness base score exists with full artifacts before
  any FT judgment.
- FT_PASS: non-AIME canary passes and corrected AIME2025 FT score is greater
  than or equal to the same-harness 30B base score.
- REQUEST-CHANGES: missing protocol, completions, parser diagnostics, checksums,
  or command/env details.
- BLOCK: base cannot be scored, canary fails, FT score is below base, or
  same-harness equivalence cannot be proven.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Current main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Related tasks: task247, task291, task293, task298, task301
