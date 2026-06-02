# task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1 - task knowledge

<!-- METADATA:SESSION=88 -->

## Knowledge Entries

1. task301 checkpoint `iter_0000035` is a salvage candidate, not a clean
   training PASS. Validation did not complete and `train_rc=1`.
2. task303 approved only later non-AIME canary consideration:
   `APPROVE_SALVAGE_CANDIDATE_FOR_LATER_NON_AIME_CANARY_CONSIDERATION_ONLY`.
3. Candidate checkpoint path:
   `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
4. Model/tokenizer path:
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
5. task301 saved with TP `4`, PP `2`, EP `4`, ETP `1`, sequence parallel, and
   8x H200. task304 may use only the minimum resources required to load/generate
   from that checkpoint, up to the same 8x H200 route, and must document it.
6. AIME2025/task243 remains blocked until task304 passes and lead creates a
   separate corrected AIME FT-vs-base task.
7. task304/#367 merged at `2026-06-02T18:42:02Z` with merge commit
   `7a93a6cea16e45284a58287b91c0069b7416fa99` from exact approved head
   `1f23d8339c123702eaa9336c1fe2b25afcd6122a`.
8. worker_3 final closeout mailbox `eb40f945d1134bb2be2fa8f82cb8b93a` confirms
   branch-only post-merge closeout head `2f480f7d17276c09ef912e8e1f4907146420c4cf`
   is only status/history/task_knowledge bookkeeping.
9. task304 acceptance clears only the non-AIME canary precondition for a later
   corrected AIME FT-vs-base task; it is not benchmark evidence or promotion,
   export, endpoint, or new training clearance.
