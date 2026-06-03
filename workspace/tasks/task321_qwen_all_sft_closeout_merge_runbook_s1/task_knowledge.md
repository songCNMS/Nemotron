# task321_qwen_all_sft_closeout_merge_runbook_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. #371/#377/#378/#379/#380 are documentation/evidence PRs, not promotion or
   runtime-action authorizations.
2. Current boundary requires coordinator/authorized non-author merge; no worker
   self-merge.
3. Next repair work remains no-training/no-eval until later explicit gate.
4. Current reviewed heads are #371
   `fc85b866ede0cdc95f31b6fcd6d61b817ceb2de8`, #377
   `c1b053b518137769b9b423d08d9590d8ae481a2e`, #378
   `df561ea93e696d8e704d4e969e2da83b719185f7`, #379
   `89cc7f74a737f174f4b8dbf9129c712fabbafa95`, and #380
   `9e57390bb33365157b73a8c93264b9dd57a2d489`.
5. #371 current drift from task317-reviewed `9361e6da` is
   status/history/task_knowledge-only; task311 metrics and artifact claims
   remain `AIME2025 +1`, `HMMT +2`, `MMLU-Pro -2`, with M1 launcher rows
   blocked.
6. Recommended merge sequence is support docs #378/#380/#379 first, then #371
   evidence/fail-closeout docs, then #377 repair plan docs, all through
   coordinator/authorized non-author merge only.
7. task318-task320 were visible only as lead assignment docs at review time.
   Allowed next actions are validation/termination preflight, raw
   blend/decontam feasibility, and MMLU data-repair linkage analysis only.
8. Worker PR for task321 is #382.
9. Refresh after #382 gate: task318-task320 are now visible as #384/#383/#381
   and all are gated as documentation/preflight evidence only.
10. #384 current head `9689b22bf0e198cbf6f7ca7cbdc30f05bdbe751c` carries
    forward lead gate `APPROVE_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED /
    HOLD_TRAINING` from gated head `2cdf39fd`; drift is gate-recording metadata
    only and does not change `validation_exit_repair_preflight_report.md`.
11. #383 current head `99713578c19a971683348128d7120f5822801337` is gated
    `APPROVE_FEASIBILITY_DOCS / NO_PACK_OR_TRAIN_RELEASE`; it enables only a
    later lead-gated raw materialize/count/decontam task, not packing/training.
12. #381 current head `4131915f14acb4ff551ae6cf3f2325a67cf89945` is gated
    `APPROVE_LINKAGE_DOCS / NO_ACTION_RELEASE`; it may carry a non-material
    residual that the report snapshot predated #383 visibility.
13. Updated recommended order is #378/#380/#379 support docs, #371 evidence
    closeout, #377 planning docs, then #384/#383/#381 repair docs, all through
    coordinator/authorized non-author merge only.
14. #380 current head is `6d43e0e7091f42af13a435c882f4ab035ca2c4c5`; drift
    from lead-refreshed `fc93290a` is metadata/session bookkeeping only.
15. #383 drift from lead-gated `4775bc17` to current `99713578` is
    status/history/task_knowledge gate-recording only.
