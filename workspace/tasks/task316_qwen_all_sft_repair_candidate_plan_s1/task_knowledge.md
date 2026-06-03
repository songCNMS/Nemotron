# task316_qwen_all_sft_repair_candidate_plan_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. Task310 checkpoint `iter_0000035` is a salvage candidate with finite train
   loss but validation hang and `train_rc=1`.
2. Task311 performance is mixed: AIME/HMMT improved, MMLU-Pro regressed by 2
   rows, and M1 launcher rows are blocked.
3. A safe next step must preserve no AIME2025 train data, no task255 reuse, no
   shared deletion, and no promotion.
4. Proposed new training/eval requires a later lead-gated task.
5. Worker_5 #377 head `7261b5fb60190f5522c05c5ae49451828f979126` recommends
   repairing data blend and validation/termination before any more 30B
   training.
6. Lead gate for task316 is `APPROVE_PLAN_DOCS / NO_ACTION_RELEASE`, recorded
   in #377 issuecomment `4615905391`.
7. The plan is conditional: task314 MMLU-Pro forensics, task315 M1 launcher
   runtime route/blocker, and task317 independent #371 closeout review remain
   pending.
8. #377 current head `cf1decab95339935dfbc41cc50cacd3f5381d805` is held as
   not merge-ready because docs mention stale head `bbb79845`; lead comment is
   issuecomment `4615946306`.
9. After task314/task315/task317, the planning direction remains data-blend plus
   validation/termination repair before later lead-gated 30B training.
10. #377 current head `2ef6d6e72ec8588a3cf16acf19708ebbb28a50a5` has stale
    `bbb79845` wording removed; lead carry-forward comment is issuecomment
    `4615987506`.
