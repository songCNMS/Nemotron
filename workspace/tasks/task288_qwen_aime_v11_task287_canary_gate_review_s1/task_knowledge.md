# task288_qwen_aime_v11_task287_canary_gate_review_s1 - task knowledge

<!-- METADATA:SESSION=27 -->

1. task288 reviews task287 only after worker_3 provides official evidence for
   an exact task287 head/PR/artifact report.
2. Approval must be for non-AIME canary evidence only. It must not authorize
   corrected AIME2025/task243 comparison, export, endpoint, promotion, 30B, or
   8-GPU.
3. If task287 cannot load/generate from task285 iter2 checkpoint without export
   or endpoint, the correct task288 disposition is `BLOCK`, not a workaround.
4. If only a task287 acceptance/docs branch is visible, task288 must remain
   HOLD even when local probe outputs exist; official task287 PR or mailbox
   artifact evidence is required before substantive review.
5. The expected task285 checkpoint references for later task287 review are
   latest iteration `2`, inventory sha
   `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`, and
   checksum manifest sha
   `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`.
6. The task287 acceptance placeholder head is
   `aa5ff74046221926c53eddfe1afbd7df38baaa89`; the earlier
   `aa5ff7408766e44cfdb073734cff1e836c2e4e17` value was a lead-doc copy
   error and should not be used.
7. Future task288 substantive review must pin the eventual official task287
   evidence head/PR/mailbox report, not the acceptance-only placeholder.
8. PR #352 head `52834d74c79ab98b5e125434160843752c34d47a` supports
   `APPROVE_BLOCKER_CLOSEOUT` for task287 BLOCK evidence only: checkpoint load
   passed, but no retained non-AIME canary completions were produced.
9. Lead may close task287 as BLOCK and create a bounded unblock task for an
   approved no-export/no-endpoint generation route. This does not release
   AIME/task243 eval, export, endpoint, promotion, 30B, or 8-GPU.
10. The task287 blocker is route/runtime, not model quality: direct local MCore
    generation failed before retained completions despite checkpoint-load PASS.
