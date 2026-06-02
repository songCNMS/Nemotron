# task287_qwen_aime_v11_non_aime_canary_retention_s1 - task knowledge

<!-- METADATA:SESSION=2 -->

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
6. Worker_3 accepted task287 on branch
   `intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1`
   from `origin/main` at `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`.
7. task287 direct checkpoint load fact: task285 iter2 can be loaded on a single
   H200 with `load_megatron_model`; the probe reports
   `LOAD_MEGATRON_MODEL=PASS`, `MODEL0_DEVICE=cuda:0`,
   `MODEL0_DTYPE=torch.bfloat16`, and `MODEL_EVAL_SET=PASS`.
8. task287 generation blocker: the no-export/no-endpoint in-process MCore route
   did not produce canary completions. The terminal blocker artifact is
   `qwen4b_task285_iter2_non_aime_canary_20260602T072800Z/canary_blocker.json`,
   with `torch.AcceleratorError: CUDA error: device-side assert triggered`
   during sampling after generation entered `StaticInferenceEngine`.
9. task287 remains a `BLOCK`, not a canary PASS. Corrected AIME2025 comparison
   remains blocked until lead creates a new release and a valid non-AIME
   canary with retained completions exists.
10. task287/#352 merged at `2026-06-02T07:39:18Z` with merge commit
    `ca1ab63588651351b3e669450659abd2ad2c73e8` from exact approved head
    `52834d74c79ab98b5e125434160843752c34d47a`. Merge preserved blocker-only
    scope; it does not authorize canary pass, AIME release, promotion, export,
    endpoint, training, 30B, or 8-GPU work.
