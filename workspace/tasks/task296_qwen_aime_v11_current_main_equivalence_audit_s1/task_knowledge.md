# task296_qwen_aime_v11_current_main_equivalence_audit_s1 - task knowledge

<!-- METADATA:SESSION=79 -->

- Current main for this task is
  `2d84ec75960fb51ba9091427638b00083625e137`.
- The immediate prior accepted V11 main after #351 was
  `5d8b8d850d26e785332f8b707c772d99881a1b5d`.
- #312 merge changed only coordinator workspace docs in lead's preliminary
  check; worker_1 must independently classify the diff.
- Existing candidate metric remains task293 FT `12/30 = 0.4` versus accepted
  base `11/30 = 0.36666666666666664`.
- If equivalence is not provable, the correct result is `B_REQUIRED_RERUN`, not
  a weak approval.
- worker_1 audit result: `A_PROVED_NO_RERUN`. Current main after #312 differs
  from post-#351 main only by coordinator workspace docs/status/handoff files.
- task285 source head to current main has zero `src/`/`tests/` diffs; the
  Qwen local train script/config are unchanged, task276 is unchanged, and only
  task283/task285 evidence docs changed.
- task293 source head to current main has zero `src/`/`tests/` diffs;
  `run_no_export_aime_eval.py` and the task291 canary runner are unchanged,
  and only task293 evidence docs changed.
- Key task285/task293 artifact hashes were recomputed from local output roots
  and matched the merged reports.
- PR #359 merged at `2026-06-02T12:56:15Z` with merge commit
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7` from exact approved head
  `b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06`.
