# task289_qwen_aime_v11_post_smoke_runbook_provenance_s1 - task knowledge

1. #350/task285 is bounded smoke evidence only: it does not create a clean
   end-to-end train/eval pass and does not clear AIME/task243 eval.
2. task287 is the current non-AIME canary gate; task288 is its independent
   review gate. Corrected AIME2025 same-harness FT-vs-base comparison remains
   blocked until these are processed by lead.
3. The accepted same-harness base comparator remains Qwen3-4B `11/30 =
   0.36666666666666664`.
