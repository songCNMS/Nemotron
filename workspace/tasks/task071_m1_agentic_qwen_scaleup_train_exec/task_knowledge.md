# task071_m1_agentic_qwen_scaleup_train_exec - task_knowledge

<!-- METADATA:SESSION=1 -->

## Notes

- Use `plan_qwen_scaleup_run.py` from latest `main` to generate the execution scripts instead of hand-writing shell commands.
- Local `/work-agents/.venv` is the preferred environment for M0/M1 data prep and Qwen tokenizer packing because NemTron is known to lack `cosmos_xenna`.
- NemTron training should run under `/root/nemotron_session5_venv` with Qwen3 4B TP=2 on GPUs 0/1 unless the host state requires a different allocation.
- With `nproc_per_node=2`, the formal scale-up planner needs `global_batch_size=2`; `global_batch_size=1` fails `plan_m1_agentic_sft_training.py` batch geometry validation.
- Cosmos/Xenna packed split parquet files are symlinks into `packed_qwen/runs/...`; use `Path.glob("*.parquet")` or `find -L` when validating them, not plain `find -type f`.
