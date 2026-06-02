# task281_qwen_aime_v11_canary_aime_eval_plan_hold_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. Accepted base comparator remains Qwen3-4B `11/30 =
   0.36666666666666664`.
2. Non-AIME canary must run before any AIME/task243 comparison once an FT
   artifact exists.
3. This task is no-run planning only.
4. Acceptance branch is
   `intern_nemotron_worker_3/task281_qwen_aime_v11_canary_aime_eval_plan_hold_s1`
   from `origin/main` at `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`.
5. task281 plan disposition is `PLAN_READY_HOLD`: future canary/AIME launch
   remains blocked until lead releases a live task for an exact accepted
   Qwen3-4B V11 FT candidate artifact.
6. Future canary must use task264 prompt set
   `qwen_v11_non_aime_export_load_canary_v1`, require `5/5` exact expected
   answers, retain full completions, and fail on reasoning-content-only,
   mixed-script, code-token, error, timeout, or length-capped rows.
7. Future AIME pilot must use the same task247/task273 corrected AIME2025
   `30x1` harness and all-request denominator; FT must be
   `>= 11/30 = 0.36666666666666664`, otherwise FAIL/no promotion.
8. task276/#344 produced fresh packed-data evidence, but it is not a model
   candidate and does not authorize training, live canary, or AIME eval.
