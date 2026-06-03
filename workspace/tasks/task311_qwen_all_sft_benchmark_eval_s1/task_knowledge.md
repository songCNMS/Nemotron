# task311_qwen_all_sft_benchmark_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. A corrected same-harness base result must exist before judging any all-SFT FT
   checkpoint on AIME2025, HMMT, MMLU-Pro, or M1 launcher-available benchmarks.
2. Non-AIME canary/checkpoint-load is required before benchmark evaluation.
3. Eval-only export or endpoint may be used only if required for evaluation and
   must not be described as promotion.
4. Session 78 task310 produced only a salvage checkpoint candidate; task311 must
   wait for accepted task313 review and explicit lead release before
   checkpoint-load or non-AIME canary.
5. After task313/#376 merged at `cb36dcab` and task310/#373 merged at
   `292c5bfa`, lead released only checkpoint-load plus non-AIME
   canary/completion-retention for checkpoint
   `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`.
6. Benchmark eval, AIME/task243 eval, MMLU-Pro/HMMT/M1 basket eval, export,
   endpoint, promotion, additional training, task255 reuse, AIME2025 train data,
   shared deletion, self-merge, and main push remain HOLD until canary evidence
   is reported and lead releases the next gate.
