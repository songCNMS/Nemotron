# task297_qwen_aime_v11_current_main_equivalence_review_s1 - task knowledge

<!-- METADATA:SESSION=5 -->

- task297 reviews task296, not the original artifacts independently from
  scratch.
- Current main is `2d84ec75960fb51ba9091427638b00083625e137`.
- Approval can only mean no-rerun-needed for current-code equivalence; it does
  not authorize export, endpoint, promotion, further training/eval, task255
  reuse, AIME2025 train data, shared deletion, 30B, or 8-GPU.
- Session 1 status is `HOLD_WAITING_TASK296`: no worker_1 task296 branch or PR
  was visible during acceptance checks.
- Session 2 status remains HOLD: task296 branch
  `4c6dc0574844a48f70d85caca3288698ebd3caf9` is now visible but contains only
  acceptance/status/task docs, with no equivalence report or official review
  evidence. Do not refresh final task297 review until worker_1 publishes exact
  substantive task296 head/report.
- Session 4 final reviewed task296/#359 exact head is
  `b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06`; #359 was `OPEN`, base `main`,
  and `CLEAN`.
- The substantive task296 audit report from
  `b45308e99db75620dd421c4cdc44560cdcda8eec` is unchanged through
  `b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06`; drift is status/history/knowledge
  only.
- Current-main equivalence approval is
  `APPROVE_A_PROVED_NO_RERUN_WITH_RESIDUALS`: PR #312 changed only coordinator
  docs, task285/task293 scoped runner/source diffs to current main are clean for
  product paths, and representative artifact hashes/metrics match carried
  evidence.
- Residuals to preserve with any approval: task285 smoke command RC=1 after
  iteration-2 checkpoint during built-in validation/SIGTERM; task276 valid/test
  sparsity; task292 detokenized fallback residual; task293
  `sampling_exact_parameter_match=false` accepted only as semantic greedy
  equivalence.
- Session 5 did not change the substantive review: final reviewed #359 head
  remains `b9c1af2986f5cdfec20c7091ffa2bc6c0b246f06`, with the same
  `APPROVE_A_PROVED_NO_RERUN_WITH_RESIDUALS` disposition and the same
  residuals/boundaries.
