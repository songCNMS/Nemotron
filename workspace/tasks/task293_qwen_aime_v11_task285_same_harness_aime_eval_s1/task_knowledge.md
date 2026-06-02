# task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 - task knowledge

<!-- METADATA:SESSION=3 -->

- Accepted base comparator is task247 Qwen3-4B corrected AIME2025 `11/30 =
  0.36666666666666664`; use it only if same-harness equivalence is proven.
- Candidate FT checkpoint is task285 iter2:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`.
- task291/#354 provides the allowed no-export/no-endpoint one-GPU route proof;
  task292 approved it with residual detokenized fallback risk.
- A PASS requires FT `>= 11/30`. A score below `11/30` is FAIL, not a promotion
  candidate.
- No export, endpoint, promotion, task255 reuse, AIME2025 train data, shared
  deletion, 30B, or 8-GPU is authorized.
- Session 2 branch refresh: current base is `origin/main`
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a` after #355/task292; task293
  branch rebased cleanly before continuing evidence work.
- Task293 result: task285 Qwen3-4B V11 iter2 scored `12/30` corrected AIME2025
  exact-normalized accuracy `0.4` via no-export/no-endpoint MCore route,
  beating accepted task247 base `11/30` by one row. This is eval-gate evidence
  only and does not authorize promotion, export, endpoint, 30B, or 8-GPU.
- Sampling residual risk for closeout: exact sampling parameters are not
  byte-identical to task247 because endpoints are forbidden in task293; the
  accepted comparison claim relies on deterministic greedy semantic match plus
  matching prompt tokens, parser, cache, max tokens, normalization, and
  denominator.
