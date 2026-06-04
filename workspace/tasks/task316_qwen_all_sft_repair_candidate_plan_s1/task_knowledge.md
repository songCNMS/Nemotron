# task316_qwen_all_sft_repair_candidate_plan_s1 - Task Knowledge

<!-- METADATA:SESSION=94 -->

## Knowledge Entries

1. Task310 checkpoint `iter_0000035` is a salvage candidate with finite train
   loss but validation hang and `train_rc=1`.
2. Task311 performance is mixed: AIME/HMMT improved, MMLU-Pro regressed by 2
   rows, and M1 launcher rows are blocked.
3. A safe next step must preserve no AIME2025 train data, no task255 reuse, no
   shared deletion, and no promotion.
4. Proposed new training/eval requires a later lead-gated task.
5. Task308/task309 only approve the constrained task299 V11 seed for task310;
   generic `stage1_sft/data_blend_raw` remains excluded until materialized,
   counted, decontam-scanned, and Qwen-packed with supervised-token proof.
6. Task311 #371 is merged at `2026-06-04T13:36:33Z`, merge
   `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`, merged head
   `2e0cd5a5c7d788ded67334ff25608f8aaedfeffe`; lead approved evidence
   closeout as `PERFORMANCE_FAIL_MIXED`, with AIME/HMMT above base but
   MMLU-Pro below base by 2 rows.
7. The next safe repair candidate is not immediate more-of-same training; it
   should first freeze task311 evidence, repair validation/exit behavior, and
   repair the all-SFT data blend before any later lead-gated 30B run.
8. Lead approved #377 head
   `7261b5fb60190f5522c05c5ae49451828f979126` as
   `APPROVE_PLAN_DOCS / NO_ACTION_RELEASE`, but this is conditional planning
   evidence only and explicitly releases no training/eval/packing/export or
   endpoint action.
9. Current #377 head advanced after session-numbering bookkeeping, so worker_5
   must not self-merge unless lead refreshes approval for the current exact
   head and explicitly authorizes merge.
10. Task314 #380 is merged at `2026-06-04T13:36:32Z`, merge
    `4ccedc1a6e30f08b6ab844c0b387714d9ef16063`; task325 #387, task341 #404,
    and task342 #405 are also merged blocker evidence on current main.
11. Lead refreshed #377 at head
    `cf1decab95339935dfbc41cc50cacd3f5381d805` and kept the plan direction
    accepted but `HOLD_NOT_MERGE_READY`; stale docs wording that treated an
    older bookkeeping head as current must not be carried forward.
12. #377 remains no-action-release: no self-merge, training, eval, packing,
    export, endpoint, promotion, task255 reuse, AIME2025 train rows, shared
    deletion, product-code edit, main push, or merge.
13. Lead assigned task318 for the validation/exit repair preflight proposed by
    task316; accepting task318 does not release task316 #377 for self-merge or
    any runtime action.
14. Session 94 reconciliation refreshed #377 from `origin/main`
    `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`; the prior DIRTY state was a
    status-only conflict, and the refreshed PR remains planning docs only with
    no task310/task341 release.
