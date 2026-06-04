# task314_qwen_all_sft_mmlu_pro_regression_forensics_s1 - Task Knowledge

<!-- METADATA:SESSION=103 -->

## Knowledge Entries

1. Task311 MMLU-Pro base was `6758/12032`; task311 FT was `6756/12032`.
2. A `-2` MMLU-Pro delta prevents a uniform non-regression claim even though
   AIME2025 and HMMT improved.
3. Row-level transitions are required before deciding whether the issue is
   model behavior, parser/prompt artifact, or an evaluator/protocol mismatch.
4. New evaluation or endpoint launch is not authorized by this task.
5. Task314 row comparison found `92` base-correct to FT-wrong rows and `90`
   base-wrong to FT-correct rows, producing the net MMLU-Pro `-2`.
6. Parser/protocol evidence is clean: both runs have `12032/12032` parsed rows,
   `ok` status, `stop` finish reason, valid compact JSON answer responses, and
   identical protocol/input sha.
7. Result-bearing source files match task311 checksum manifests. Direct
   `logs/run.log` hashes differ because `summary.json` was appended after the
   manifest-sized prefix; prefix hashes match and suffixes equal `summary.json`.
8. Forensics recommendation is `APPROVE_FORENSICS`, but task311 gate remains
   `FAIL_MMLU_PRO_BELOW_BASE_WITH_AIME_HMMT_PASS` with no promotion claim.
9. Lead accepted task314/#380 at head `d3bd9733` as
   `APPROVE_FORENSICS_DOCS / NO_ACTION_RELEASE`; no self-merge is authorized
   without an explicit coordinator/authorized non-author path.
10. Task320 follow-up visibility was addressed by verifying PR #381 at head
    `4131915f14acb4ff551ae6cf3f2325a67cf89945`, `OPEN`/base `main`/
    `CLEAN/MERGEABLE`; task314 remains unmerged pending authorized path.
11. Lead accepted task320/#381 at head `4131915f` as
    `APPROVE_LINKAGE_DOCS / NO_ACTION_RELEASE`, and carried task314/#380 at
    `fc93290a`; neither PR has self-merge authorization.
12. Lead assigned task324 to design an MMLU-aware all-SFT blend using
    task319/task320/task314; task324 remains docs/analysis only with no data
    materialization, packing, training, eval, export, endpoint, promotion, main
    push, merge, or self-merge authorization.
13. Task324 was completed as PR #386 at head `8c4f7aa7` from a separate
    worktree, with recommendation `APPROVE_BLEND_DESIGN`; task314 remains the
    active primary branch metadata task and is still not self-merged.
14. Lead accepted task325/#387 at head `e6c5e1f` as
    `APPROVE_BLOCKER_DOCS / BLOCK_RUNTIME_CONFIRMED`: current M1 runnable rows
    remain `0/19`, so any M1 benchmark row execution remains blocked until a
    separate lead-gated runtime/container/scheduler/credential proof exists.
15. Task333 completed as PR #396 at head `8546ae8d` with no-training combined
    packed-contract candidate `run_20260604T074500Z`; this is review evidence
    only and does not authorize task310 release, training, eval, export,
    endpoint, promotion, 30B release, main push, merge, or self-merge.
16. Task333/#396 report checksum fix at head `9a9471e3` changed only
    worker status and `combined_packed_contract_report.md`; the task299 seed
    row-manifest hashes now match source_provenance/direct files:
    from-m0 `7562c864`, math-final `e466ee7`, hard-verified `89ab29`.
17. Task333/#396 was approved for docs closeout and self-merged at exact head
    `6261daaa37172caa11929b0b88f685b63f987221`; merge commit
    `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`, merged at
    `2026-06-04T08:37:16Z`. Approval remains `HOLD_TRAINING`, with no
    training, eval, export, endpoint, promotion, 30B/task310 release, task255
    reuse, or AIME2025 train rows authorized.
18. Session 102 refresh rebased open all-SFT docs PRs #380, #381, and #386
    onto `origin/main` `8a757c32`. Conflicts were limited to worker status;
    diff-check passed and each PR diff remains task-local docs/report plus
    worker status only. Dispositions remain evidence-only with no self-merge
    or release authorization.
19. Session 103 merged task314/#380 at approved head
    `fe34e52d19ec9cc9a384588a3e900924280fe16e`; merge commit
    `4ccedc1a6e30f08b6ab844c0b387714d9ef16063`, merged at
    `2026-06-04T13:36:32Z`. After fetching current main
    `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`, #381 refreshed clean at
    `63b58a86848a108dde8bae3f9f10a7a1e25f64c4` and #386 refreshed clean at
    `ea1607940796ce86ff39bfa22aba8d7754602fde`; both remain HOLD for lead
    sequencing.
