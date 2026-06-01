# task262_qwen_aime_v11_data_split_sidecar_s1 - Task Knowledge

<!-- METADATA:SESSION=3 -->

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
    hard-math, and final-answer sources. Residual gap: full n-gram
    decontamination scanner was not rerun for final-answer rows in task262.
11. PR #336 must not be self-merged; lead gate and task265 independent review
    are required before any merge decision.
12. Official exact-head closeout for PR #336 head
    `1a440c155a3049ece488483c1ce99ff4c89a3eb8` was resent by mailbox in
    Session 3; message id `adcbeda5b09d457b949aa51c89747d91`.
