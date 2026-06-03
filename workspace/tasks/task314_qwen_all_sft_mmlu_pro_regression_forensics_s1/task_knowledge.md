# task314_qwen_all_sft_mmlu_pro_regression_forensics_s1 - Task Knowledge

<!-- METADATA:SESSION=96 -->

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
