# task289_qwen_aime_v11_post_smoke_runbook_provenance_s1 - task knowledge

<!-- METADATA:SESSION=2 -->

1. #350/task285 is bounded smoke evidence only: it does not create a clean
   end-to-end train/eval pass and does not clear AIME/task243 eval.
2. #352/task287 is the current non-AIME canary blocker gate; task288 and task290
   are its independent review gates. Corrected AIME2025 same-harness FT-vs-base
   comparison remains blocked until the blocker is resolved and processed by
   lead.
3. The accepted same-harness base comparator remains Qwen3-4B `11/30 =
   0.36666666666666664`.
4. #349/task283 merged at `2026-06-02T06:03:58Z` with merge commit
   `f82f8f73c39bc93ff268f45845a94060585b8290`; disposition
   `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`.
5. #350/task285 merged at `2026-06-02T06:53:14Z` with merge commit
   `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`; the smoke checkpoint latest
   iteration is `2`, inventory sha
   `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`, and
   checksum manifest sha
   `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`.
6. task286 approved #350 exact head
   `fc379240c8517de10e37a5438f87b6b0994399f0` as bounded smoke evidence only;
   it cannot be used as a clean train/eval pass, quality claim, AIME release,
   export release, endpoint release, promotion release, 30B release, or 8-GPU
   release.
7. #352/task287 is OPEN/base main/CLEAN at exact head
   `52834d74c79ab98b5e125434160843752c34d47a` with disposition `BLOCK`.
   It passed checkpoint load proof (`LOAD_MEGATRON_MODEL=PASS`) but retained no
   completions, wrote no `canary_summary.json`, recorded retained completion
   rows `0`, and had correct canary answers `0/5`.
8. task287 output root is
   `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`;
   the final blocker log sha is
   `f32df07a0ab624057a93b3615f28416dc212c3d511bd617fa1c2508825e65473`, and
   blocker json sha is
   `aa451bfb364e1c44b67f6a0beb2612a2f331582555909445099c228c480aab2e`.
9. task288 current fetched branch head is
   `e62fad1da9a4279869e939a34604c4f1ce13827b`; no task288 PR was visible in
   this refresh.
10. task290 current fetched branch head is
   `dab9a8bb87315bed529af0f00e3c843b1f910d0e`; no task290 PR was visible in
   this refresh.
