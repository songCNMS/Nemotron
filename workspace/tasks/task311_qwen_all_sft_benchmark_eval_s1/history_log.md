# task311_qwen_all_sft_benchmark_eval_s1 - History Log

<!-- METADATA:SESSION=78 -->

## Session 77 - 2026-06-03 UTC - Assigned

- Created by `intern_nemotron_lead` for all-SFT checkpoint-load/canary and
  available benchmark evaluation.
- Assigned to `intern_nemotron_worker_3`.
- Benchmark eval is blocked until task310 provides a usable checkpoint; AIME2025
  remains held-out eval/decontam only.

## Session 78 - 2026-06-03 UTC - HOLD preserved pending task313 salvage review

- Worker_5 task310 produced a checkpoint salvage candidate in #373 at exact head
  `7561a578f5f624cf1d3b85bef0dd8abb5c787533`, but the run ended with
  `train_rc.txt=1` after lead-cleared SIGTERM during validation hang.
- Lead created task313 for independent review of the #373/task310 checkpoint
  salvage evidence.
- Task311 remains HOLD: no checkpoint-load, non-AIME canary, benchmark eval,
  AIME/task243 eval, export, endpoint, promotion, task255 reuse, AIME2025 train
  data, shared deletion, direct main push, merge, or product-code edit is
  authorized until lead explicitly releases a reviewed checkpoint-load/canary
  path.

## Session 78 - 2026-06-03 UTC - Checkpoint-load plus non-AIME canary released

- task313/#376 merged at `2026-06-03T17:27:38Z` with merge commit
  `cb36dcab1aae10ec12991433bfddfeeeb02d3d46` from head
  `3f5db4059260dd4b90e204c3f553b07d83edc7f4`.
- task310/#373 merged at `2026-06-03T17:30:08Z` with merge commit
  `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` from head
  `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`.
- Lead released only checkpoint-load plus non-AIME canary/completion-retention
  for task310 checkpoint candidate
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`.
- Worker_3 was instructed to refresh #371 from current `origin/main`
  `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` before running.
- Benchmark eval, AIME/task243 eval, MMLU-Pro/HMMT/M1 basket eval, export,
  endpoint, promotion, additional training, task255 reuse, AIME2025 train data,
  shared deletion, self-merge, and main push remain HOLD pending canary report
  and explicit lead release.
