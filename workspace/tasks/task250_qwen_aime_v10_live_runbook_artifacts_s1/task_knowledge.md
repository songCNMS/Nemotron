# task250_qwen_aime_v10_live_runbook_artifacts_s1 - Task Knowledge

<!-- METADATA:SESSION=13 -->

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
5. Current live gate status is HOLD because task248 candidate artifacts,
   task243 comparison artifacts, and explicit 30B permission are not yet
   published/approved; task246 and task247 are now merged on main.
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
10. Session 9 supersedes the earlier base endpoint blocker: task247 #326 used
    a task-owned NemTron endpoint on `127.0.0.1:13147` for artifact collection
    and stopped it afterward; common ports `13000` and `30001` remained
    unavailable.
11. Session 7 task249 matrix result: task246 is BLOCK/HOLD, task247 is
    BLOCK/HOLD, task248 is approved only as a blocked-before-prep report while
    still HOLD for runtime evidence. Session 9 supersedes the task246/task247
    inputs with #325/#326 evidence below.
12. Session 13 task246 update: #325 is merged into current `origin/main` at
    merge commit `2775dff05948acce3a35a2d941bbd2f96d074b4a`, merged at
    `2026-06-01T17:43:24Z` from head
    `266b6a14262278b4fe27f75a3273fc156a5538ce`. Direct top manifest sha256 is
    `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`, and
    direct M0 manifest sha256 is
    `ca7864ce5ddbec20c0e0b1e67fdaefb2b09ef884f430b68fe7158c5b62951477`.
13. Session 9 task247 update: #326 is merged into current `origin/main` at
    merge commit `85f2bf5c11062741388ca114a84a2c26535b7df9`, merged at
    `2026-06-01T17:21:29Z` from head
    `8fb34bd9116e32aa8d191750f2510d2a843e0da5`; same-harness Qwen3-4B base
    pilot score is `11/30` = `0.36666666666666664`. Any FT comparison must use
    the same cache, runner, prompt variant, sampling, and all-request
    denominator.
14. Session 13 task249 update: #323 is open/CLEAN at
    `b2ae6d59c106225bdc318ccd3383ecf32cd3c37f` and remains HOLD/no-final-pass.
15. Session 13 combined gate: task246 corpus/M0 evidence and task247 base
    evidence are on current main, but NO-GO/HOLD remains because task248 FT
    artifacts are missing, task243 comparison output is missing, and 30B/8-GPU
    permission remains blocked.
