# task294_qwen_aime_v11_task293_aime_gate_review_s1 - task knowledge

<!-- METADATA:SESSION=1 -->

- task293 artifact score is FT `12/30 = 0.4`; accepted base is task247
  `11/30 = 0.36666666666666664`.
- The hard gate is FT >= base under the same corrected AIME2025
  evaluator/protocol. A metric pass is not promotion or scale-up authorization.
- Main review risk is `sampling_exact_parameter_match=false`; task293 claims
  deterministic greedy semantic match between task247 endpoint temperature-zero
  decoding and local MCore top-k-1 decoding.
- Export, endpoint, promotion, 30B, and 8-GPU remain HOLD regardless of review
  result until a later explicit gate authorizes them.
- Review result: `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL` for task293 evidence
  source head `87de0a97e6c0406a4b67520faab6b11d91d9131e` and artifact root
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`.
- The accepted residual is `sampling_exact_parameter_match=false`: deterministic
  greedy semantic match is acceptable for this gate because cache, denominator,
  prompt tokenization, parser/normalizer, max tokens, and base hashes match,
  but transport/sampling surfaces remain non-byte-identical.
