# task243_qwen_aime2025_base_vs_ft_eval_gate_s1 - Corrected AIME2025 base-vs-FT gate

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_3,SESSION=0 -->

## Background

The new supervisor acceptance rule is absolute: any promoted fine-tuned Qwen model must not score lower than the same base model under the same corrected AIME 2025 evaluator/protocol. Existing eval history includes `qwen_eval_repro_gate.py`, `qwen_eval_repro_gate.yaml`, benchmark alignment tests, and corrected AIME/HMMT evidence from task071/task075/task076.

## Goal

Define and implement the corrected AIME2025 base-vs-FT evaluation gate and score normalization needed to judge Qwen3-4B pilot checkpoints and any future 30B candidates.

## Scope

- Own eval-gate changes around `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_eval_repro_gate.py`, `qwen_eval_repro_gate.yaml`, benchmark alignment ledgers, or a new narrowly scoped gate module if cleaner.
- Preserve Qwen eval route `/v1/chat/completions`, Qwen tokenizer chat template, `enable_thinking=false`, and `truncate_history_thinking=false`.
- Define a pilot AIME25 smoke protocol and the final full corrected AIME25 protocol.
- Require a same-harness base score before judging any FT checkpoint. The base and FT runs must use the same model family, prompt set, repeats, max tokens, parser, endpoint route, temperature/top_p policy, and scorer normalization.
- Record score normalization: numerator, denominator, parsed count, finish reasons, per-problem rows, and exact-normalized accuracy.

## Boundaries

- Do not push `main` or self-merge.
- Do not train models.
- Do not use AIME25 labels/prompts as training data.
- Do not promote a checkpoint on parsed rate alone.
- If live eval is blocked by endpoint/container/resource issues, report the blocker and provide the exact command/config needed for worker_5 to verify.

## Expected Output

- Worker branch: `intern_nemotron_worker_3/task243_qwen_aime2025_base_vs_ft_eval_gate_s1`.
- PR to `main` after local validation.
- A baseline protocol report in this task directory with:
  - Qwen3-4B base checkpoint path.
  - Pilot smoke protocol.
  - Final corrected AIME25 protocol.
  - Score normalization schema.
  - Required artifact paths for base and FT.
- Mailbox report with branch, head SHA, PR URL, tests/checks run, and any live baseline score if executed.

## Acceptance Criteria

- The gate refuses to judge FT without a same-harness base result.
- The gate fails promotion when FT exact-normalized AIME25 score is lower than base under the same protocol.
- The gate reports both accuracy and parsed/finish diagnostics so shorter wrong traces do not look like improvement.
- First measurable go/no-go gate: Qwen3-4B V10 pilot can proceed to broader evaluation only if its corrected AIME25 smoke score is at least the Qwen3-4B base smoke score under identical settings.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Depends on: current qwen eval repro gate, task071/task075/task076 corrected math evidence
