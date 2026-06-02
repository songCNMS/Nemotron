# task294_qwen_aime_v11_task293_aime_gate_review_s1 - history log

<!-- METADATA:SESSION=1 -->

## Session 76 - 2026-06-02 UTC - assignment

- Created after task293 read-only artifacts showed `TASK293_DISPOSITION=PASS`
  with FT `12/30 = 0.4` versus accepted base `11/30 =
  0.36666666666666664`.
- Assigned to worker_4 for independent read-only artifact and same-harness
  protocol review of exact task293 head
  `87de0a97e6c0406a4b67520faab6b11d91d9131e`.
- Required decision: `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`,
  `REQUEST_CHANGES`, or `BLOCK_REVIEW`.
- Boundaries: no edits beyond review docs/status, no training, no live eval, no
  export, no endpoint, no promotion, no task255, no AIME2025 train data, no
  shared deletion, no 30B, no 8-GPU, no merge, and no main push.

## Session 1 - independent task293 artifact review

- Accepted task294 on worker branch
  `intern_nemotron_worker_4/task294_qwen_aime_v11_task293_aime_gate_review_s1`
  from current `origin/main` `228ffd741bb9fa4eae6abf8d37bc171397151d7a`.
- Imported task294 docs from lead branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `70d7aafd0ef4c5073561dcea89cad5fb1d876b6d`.
- Fetched worker_3 task293 branch. The assigned evidence head
  `87de0a97e6c0406a4b67520faab6b11d91d9131e` is in branch history; current
  task293 PR #356 head observed during review is
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`.
- Reviewed artifact root
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`.
- Verified checksums, checksum manifest consistency, 30-row denominator,
  retained completion rows, checkpoint load, command/env boundaries, accepted
  task247 base hashes, and same-harness proof.
- Decision: `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`. FT score is `12/30 = 0.4`
  versus accepted base `11/30 = 0.36666666666666664`.
- Explicit residual accepted: `sampling_exact_parameter_match=false` because
  base used an endpoint route while FT used the task291-approved no-export
  MCore top-k-1 greedy route. This is acceptable only as a bounded semantic
  greedy-match residual, not a byte-identical sampling surface.
- No code edits, AIME/eval rerun, training, optimizer step, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, shared deletion, merge, main
  push, 30B, or 8-GPU action was performed.
