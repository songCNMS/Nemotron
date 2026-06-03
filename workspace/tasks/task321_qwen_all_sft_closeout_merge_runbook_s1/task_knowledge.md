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
