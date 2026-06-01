# task257_qwen_aime_v10_task255_same_harness_eval_s1 - task255 AIME gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Background

task243 defined the corrected AIME2025 base-vs-FT gate. task247 accepted the
same-harness Qwen3-4B base score:

- Base model: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Corrected AIME2025 exact-normalized score: `11/30 =
  0.36666666666666664`

task255 now has a bounded Qwen3-4B candidate HF export pending independent
artifact review:

`/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`

## Goal

Run or prepare the corrected AIME2025 same-harness FT-vs-base comparison for
the task255 Qwen3-4B candidate artifact, preserving the hard non-regression
rule: FT exact-normalized score must be greater than or equal to the accepted
base score under the same evaluator/protocol.

## Scope

- Start from current `origin/main` and the existing task243 corrected harness.
- Use the accepted task247 base score only if the protocol/cache/runner/prompt
  settings exactly match; otherwise rerun/report the same-harness Qwen3-4B base
  score before judging FT.
- Candidate FT artifact:
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
- Preserve corrected AIME2025 protocol:
  - 30 problems, denominator all 30 requests;
  - exact-normalized scoring;
  - parse and finish diagnostics;
  - same prompt variant, max tokens, sampling, parser, route, and scorer as the
    accepted base protocol;
  - Qwen chat/template settings with `enable_thinking=false` and
    `truncate_history_thinking=false`.
- Coordinate with task256: do not make a final PASS decision if task256 blocks
  or request-changes the artifact.

## Boundaries

- Do not train models.
- Do not use AIME2025 prompts/labels as trainable data.
- Do not run 30B/8-GPU or claim scale-up clearance.
- Do not claim promotion; report only PASS/FAIL/HOLD for the Qwen3-4B pilot
  gate.
- Do not push main or self-merge.
- Do not delete or overwrite anything under `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task257_qwen_aime_v10_task255_same_harness_eval_s1`.
- PR only if repo docs/config/scripts change; artifact-only closeout is
  acceptable if no repo changes are needed.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/`.
- Mailbox report with:
  - branch/head/PR or artifact-only status;
  - exact harness commit/config/cache/input paths;
  - base score evidence used or rerun;
  - FT endpoint/model path and launch command;
  - raw AIME outputs and per-problem rows;
  - numerator/denominator, parsed count, finish diagnostics, and exact-normalized score;
  - PASS/FAIL/HOLD disposition against accepted base `11/30`;
  - explicit boundary confirmation.

## Acceptance Criteria

- PASS only if task255 FT exact-normalized AIME2025 score is `>= 11/30` under
  the same corrected protocol.
- FAIL if task255 FT exact-normalized score is lower than `11/30`.
- HOLD/BLOCK if endpoint, artifact, protocol, or task256 review status prevents
  a valid same-harness judgment.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task243, task247, task255, task256
- First gate: corrected AIME2025 same-harness FT-vs-base comparison.
