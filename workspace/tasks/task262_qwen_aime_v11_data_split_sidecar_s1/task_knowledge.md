# task262_qwen_aime_v11_data_split_sidecar_s1 - Task Knowledge

<!-- METADATA:SESSION=6 -->

## Knowledge Entries

1. task261 found the task253 exposed train split omitted intended M0 shards 5-6
   and hard-math shards 0-4 because dataset-qualified blend entries collapsed to
   basename symlinks.
2. V11 must not train until intended and exposed split rows/tokens/shards match
   or the pipeline fails closed before training.
3. AIME2025 prompts and labels are held-out eval/decontamination material only.
4. This task is data/packing readiness evidence only; it cannot authorize
   training, task243 comparison, promotion, or 30B/8-GPU.
5. Task262 branch base is `origin/main`
   `513fefa1f1ace94302b56413769c78fb7224624c`, and task docs were imported
   from lead docs branch `81253415dd3285ce0eb56e69733d210742edcb50`.
6. The V11 code repair preserves old basename links only when unique; colliding
   shard basenames become dataset-qualified names such as
   `dataset-name__hash__shard_000000.parquet`.
7. The Qwen packed-data contract now fails before training if exposed split
   parquet targets do not match `blend.json` intended targets as multisets.
8. task253 train audit: intended 15 shards / 113 rows / 835223 input tokens /
   156569 supervised tokens; exposed 8 shards / 79 rows / 596944 input tokens /
   110945 supervised tokens.
9. V11 sidecar plan artifact includes base M0 1100 rows, all 8 hard-math rows,
   and 200 final-answer rows with explicit weight 1.0; no packing/training was
   run.
10. Exact task246-style heldout prompt-hash overlap counts are 0 for base,
    hard-math, and final-answer sources. Fresh full final-answer n-gram
    decontamination evidence was added in Session 4.
11. PR #336 received lead approval for exact head
    `8fd3ff6065290b850c98db5f7abff91aa6880967` and was self-merged in Session
    6 after confirming it was OPEN/base main/CLEAN at that head.
12. Official exact-head closeout for PR #336 head
    `1a440c155a3049ece488483c1ce99ff4c89a3eb8` was resent by mailbox in
    Session 3; message id `adcbeda5b09d457b949aa51c89747d91`.
13. `history_log.md` must keep unique `## Session N` headings; the V11
    implementation block is recorded as a non-session subheading under
    Session 1 to avoid duplicate Session 1 headings.
14. Fresh task262 full final-answer token 8-gram scan covers 200 final-answer
    rows against 560 heldout prompts: 112000 pair comparisons, 4 overlap pairs,
    1 informational pair, 0 blocker pairs, 0 rows with blocker overlap, max
    score 0.257143.
15. The standard `decontaminate_math_rows` check over
    `math_competition_numeric` final-answer rows scanned 100 rows, found 0
    blocker findings, and dropped 0 rows.
16. Lead's Session 5 update referenced prior head `69f32c6`; PR #336 had
    already advanced to `5e431f4` with the requested final-answer n-gram
    evidence before this reconciliation metadata was recorded.
17. PR #336 merge details: mergedAt `2026-06-01T23:14:37Z`, merge commit
    `2ca6541c275d1eb64068e665af24147a796c818a`, merged head
    `8fd3ff6065290b850c98db5f7abff91aa6880967`.
