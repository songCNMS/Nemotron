# task289_qwen_aime_v11_post_smoke_runbook_provenance_s1 - task knowledge

<!-- METADATA:SESSION=7 -->

1. #350/task285 is bounded smoke evidence only: it does not create a clean
   end-to-end train/eval pass and does not clear export, endpoint, promotion,
   30B, or 8-GPU.
2. #352/task287 is the merged non-AIME canary blocker record; task288 and merged
   #353/task290 approve that blocker closeout as evidence only.
3. #354/task291 is MERGED at `2026-06-02T08:30:04Z` with merge commit
   `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf` from exact head
   `2fda1ed46da4c82712a5c22c85bf124c26c6376f`. It records a retained synthetic
   non-AIME no-export/no-endpoint route pass for the task285 iter2 checkpoint.
4. #355/task292 is MERGED at `2026-06-02T08:37:35Z` with merge commit
   `228ffd741bb9fa4eae6abf8d37bc171397151d7a` from exact head
   `e519fecc1065bd055a69fdf271bd21994facd13b`. The decision is
   `APPROVE_CANARY_ROUTE_PASS`.
5. task292 carries a narrow residual risk: `synthetic_word_completion_ready_set`
   used `generated_tokens_detokenize_fallback` because MCore `generated_text`
   was empty while generated token ids decoded to retained text.
6. #357/task294 is MERGED at `2026-06-02T11:16:53Z` with merge commit
   `24268157bd7088fea0f37d149cfc6ec042aa0e5a` from exact head
   `f1c00a0cc8e2a9cda5e2caef9bc5137cda7835a1`; decision
   `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`.
7. #356/task293 is MERGED at `2026-06-02T11:22:34Z` with merge commit
   `31a3e962544202954f0afba211888f7414b38d7c` from exact head
   `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`. It reports task285 iter2
   corrected AIME2025 FT `12/30 = 0.4`.
8. The accepted same-harness base comparator remains Qwen3-4B `11/30 =
   0.36666666666666664`; task293 delta is `+1/30` and accuracy delta is
   `+0.03333333333333338`.
9. task293 local output root is
   `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`;
   remote output root is
   `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`.
10. task293 key hashes: summary
   `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7`,
   results
   `4cbc2a9543a658df6a3e18e3128c5a5c9a173f9a575372095cfcbe5d6232aca5`,
   full completions
   `5cb1e11ab8d331127c7c12f2cd8c04d83d2e6bd93445a5ebffc62363e2a818b4`,
   checksum manifest
   `6a47e802433648248658010125db51474d0b4af565dc10c637d004900948e7d4`.
11. task293 same-harness proof: accepted task247 AIME cache, `0` prompt-token
    mismatches across all `30` rows, same prompt variant `original`, max-token
    cap `8192`, denominator `30`, and copied task247 parser/normalizer logic.
12. task293 residual risk: `sampling_exact_parameter_match=false` because the FT
    eval used the no-export/no-endpoint MCore greedy route while the accepted
    base comparator used SGLang `/v1/chat/completions`; task294 accepted this
    as a bounded residual for metric-gate evidence.
13. AIME2025 prompts/labels were held out for eval/decontamination evidence
    only and are not trainable data.
14. task255 remains discarded and must not be reused.
15. Export, endpoint, promotion, task255 reuse, AIME2025 train data, shared
    deletion, 30B, and 8-GPU remain blocked.
16. #351 merged at `2026-06-02T11:35:48Z` with merge commit
    `5d8b8d850d26e785332f8b707c772d99881a1b5d` from approved head
    `c2c217231c9d377430171166c85d1165ac75db69`. The merge was
    docs/provenance only and did not authorize export, endpoint, promotion,
    further training/eval, task255 reuse, AIME2025 train data, shared deletion,
    30B, or 8-GPU.
