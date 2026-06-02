# task294_qwen_aime_v11_task293_aime_gate_review_s1 - task knowledge

- task293 artifact score is FT `12/30 = 0.4`; accepted base is task247
  `11/30 = 0.36666666666666664`.
- The hard gate is FT >= base under the same corrected AIME2025
  evaluator/protocol. A metric pass is not promotion or scale-up authorization.
- Main review risk is `sampling_exact_parameter_match=false`; task293 claims
  deterministic greedy semantic match between task247 endpoint temperature-zero
  decoding and local MCore top-k-1 decoding.
- Export, endpoint, promotion, 30B, and 8-GPU remain HOLD regardless of review
  result until a later explicit gate authorizes them.
- #357 is lead-approved via comment `4601824155` for exact head `f1c00a0`;
  worker_4 may self-merge only if clean at merge time. #356 remains separately
  held until #357 lands and lead rechecks it.
- #357 merged at `2026-06-02T11:16:53Z` with merge commit `24268157...` from
  head `f1c00a0...`. Task294 review evidence is now merged.
