# task287_qwen_aime_v11_non_aime_canary_retention_s1 - task knowledge

1. #350/task285 merged at `2026-06-02T06:53:14Z` with merge commit
   `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0` from exact head
   `fc379240c8517de10e37a5438f87b6b0994399f0`.
2. task285 retry3 checkpoint evidence is bounded smoke only: latest iteration
   `2`, checkpoint root
   `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`,
   inventory sha
   `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`, and
   checksum manifest sha
   `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`.
3. retry3 `RC=1` after built-in validation/SIGTERM must be carried. It does not
   invalidate the iter2 bounded smoke checkpoint evidence, but it means no clean
   train/eval pass or validation quality claim exists.
4. Current boundary for task287 is stricter than the older "export-load canary"
   wording: no export and no endpoint are allowed. If canary cannot run through
   an allowed local checkpoint-load/generation path, report BLOCK instead of
   launching an endpoint.
5. Corrected AIME2025 comparison remains blocked until task287 passes and lead
   creates a separate AIME/task243 release.
