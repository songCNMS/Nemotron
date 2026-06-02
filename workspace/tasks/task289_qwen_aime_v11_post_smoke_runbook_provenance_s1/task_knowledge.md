# task289_qwen_aime_v11_post_smoke_runbook_provenance_s1 - task knowledge

<!-- METADATA:SESSION=1 -->

1. #350/task285 is bounded smoke evidence only: it does not create a clean
   end-to-end train/eval pass and does not clear AIME/task243 eval.
2. task287 is the current non-AIME canary gate; task288 is its independent
   review gate. Corrected AIME2025 same-harness FT-vs-base comparison remains
   blocked until these are processed by lead.
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
7. task287 current fetched branch head is
   `aa5ff74046221926c53eddfe1afbd7df38baaa89`, but no task287 PR or accepted
   canary artifact report is visible to task289.
8. task288 current fetched branch head is
   `2c64e1da7af63a52092f7a323e94752961ee3251`; it is HOLD pending official
   task287 evidence.
