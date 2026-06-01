# task250_qwen_aime_v10_live_runbook_artifacts_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. The canonical first-gate rule is
   `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy` under the
   same corrected AIME2025 harness.
2. task245's static runbook listed expected paths; this task must replace
   placeholders with real artifact paths or exact blockers.
3. No 30B/8-GPU scale is permitted until Qwen3-4B same-harness non-regression
   is proven and lead grants explicit permission.
4. Session 1 starts from `origin/main` commit `20973e7`, which includes PR
   #321's Qwen3-4B V10 planner/smoke merge.
5. Current live gate status is HOLD because real task246 corpus/input, task247
   base artifacts, task248 candidate artifacts, task249 review, and task243
   comparison artifacts are not yet published as accepted evidence.
6. Session 4 is a metadata/status correction for acceptance visibility; it does
   not change the live artifact gate or authorize runtime work.
