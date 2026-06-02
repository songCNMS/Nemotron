# task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 - task knowledge

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
- Final read-only task293 artifacts from `run_20260602T085237Z` show FT
  `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664`, with
  disposition `PASS`. This is an AIME metric pass, not a promotion or scale-up
  authorization.
- Residual review risk: `sampling_exact_parameter_match=false`; task293 asserts
  deterministic greedy semantic match between task247 endpoint temperature-zero
  decoding and local MCore `top_k=1` decoding. This needs task294 independent
  review before final lead gate wording.
- Worker_3 official closeout/PR is still pending. Until it lands and task294
  reviews exact head `87de0a97...`, keep export, endpoint, promotion, 30B, and
  8-GPU on HOLD.
- Worker_3 opened #356 at head `672d0101`; report matches artifacts, but lead
  set HOLD via comment `4601765555` pending task294 independent review. #356
  must not be self-merged before that review is processed.
- task294/#357 is now merged and #356 has been rechecked clean. Lead approval/
  HOLD-lift comment `4601875731` allows worker_3 self-merge if exact head
  `672d0101` remains CLEAN/MERGEABLE at merge time. This still does not
  authorize export, endpoint, promotion, further training/eval, 30B, or 8-GPU.
