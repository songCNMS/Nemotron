# task250_qwen_aime_v10_live_runbook_artifacts_s1 - Task Knowledge

<!-- METADATA:SESSION=7 -->

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
7. Session 5 visibility update: task248 branch `2007418` is published with
   `qwen4b_v10_pilot_report.md` and is blocked before prep/train on missing
   task246/task247 dependencies.
8. Session 7 visibility update supersedes the earlier task249 entry: PR #323
   is open/CLEAN at `68a8ee77ee25f5dbbac170c935e8487b88198ce2` and publishes
   `live_gate_review_matrix.md`.
9. Session 6 evidence update: task247 local AIME2025 input/cache exists under
   `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache`
   with 30 rows and sqlite cache, but it is only partial evidence until worker_3
   formalizes it in a pushed task247 report/PR.
10. Session 6 blocker update: no reachable Qwen3-4B endpoint is available on
   `127.0.0.1:13000` or `127.0.0.1:30001`, so task247 base score artifacts are
   still blocked.
11. Session 7 task249 matrix result: task246 is BLOCK/HOLD, task247 is
    BLOCK/HOLD, task248 is approved only as a blocked-before-prep report while
    still HOLD for runtime evidence, and the combined first go/no-go remains
    NO-GO/HOLD until real corpus/input, base score, FT artifacts, task243
    comparison, and 30B permission are present.
