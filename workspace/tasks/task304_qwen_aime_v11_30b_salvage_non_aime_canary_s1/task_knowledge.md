# task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1 - task knowledge

<!-- METADATA:SESSION=83 -->

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
