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
