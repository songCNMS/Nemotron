# task323_qwen_all_sft_validation_skip_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Task310 reached iter 35/35 and checkpoint marker 35, but ended with
   `train_rc=1` after validation hang.
2. Task318 Route A prefers no exposed valid parquet and a separate same-harness
   eval handoff.
3. A later training task must not launch until this preflight or an equivalent
   validation-control task passes.
4. This task does not authorize training or eval.
5. Task323 output root
   `/work-agents/intern_nemotron_worker_5/outputs/task323_qwen_all_sft_validation_skip_preflight_s1/run_20260603T203404Z`
   contains a dereferenced train-only packed root with no exposed `valid` or
   `test` directories.
6. Route A preflight proof records `train_parquet_count=46`,
   `valid_parquet_count=0`, `test_parquet_count=0`, `mirror_symlink_count=0`,
   source-vs-mirror hash parity `46/46`, and `do_validation=false`.
7. Same-harness eval handoff remains mandatory after any later lead-gated
   training/checkpoint review; task323 does not authorize eval or training.
