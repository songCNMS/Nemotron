# task317_qwen_all_sft_task311_closeout_review_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. #371 current head is `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`.
2. Lead gate comments `4615730412` and `4615769907` classify #371 as
   `APPROVE_EVIDENCE_CLOSEOUT / PERFORMANCE_FAIL_MIXED`.
3. The PR may be mergeable as evidence/fail-closeout docs, but it is not a
   promotion, training, export, endpoint, or new-eval authorization.
4. The current boundary disallows worker self-merge; coordinator/authorized
   non-author merge path is required if merge proceeds.
5. Worker_4 independently verified #371 current head
   `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6` as docs/task-owned scripts only,
   with no product-code edits.
6. Corrected-Qwen metrics are mixed: AIME2025 `16/30` vs base `15/30`, HMMT
   `11/30` vs base `9/30`, and MMLU-Pro `6756/12032` vs base `6758/12032`.
7. Endpoint cleanup is currently clean on NemTron: port `13231` free, no live
   SGLang server, all eight H200s idle at `1 MiB`/`0%`.
8. JSON checksum manifests for corrected benchmark runs have stale
   `logs/run.log` entries, but result-bearing artifacts and summaries match
   their hashes. This is a docs-closeout residual, not promotion evidence.
