# task323_qwen_all_sft_validation_skip_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. Task310 reached iter 35/35 and checkpoint marker 35, but ended with
   `train_rc=1` after validation hang.
2. Task318 Route A prefers no exposed valid parquet and a separate same-harness
   eval handoff.
3. A later training task must not launch until this preflight or an equivalent
   validation-control task passes.
4. This task does not authorize training or eval.
