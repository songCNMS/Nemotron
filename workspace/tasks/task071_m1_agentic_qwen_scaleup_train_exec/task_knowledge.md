# task071_m1_agentic_qwen_scaleup_train_exec - task_knowledge

<!-- METADATA:SESSION=2 -->

## Notes

- Use `plan_qwen_scaleup_run.py` from latest `main` to generate the execution scripts instead of hand-writing shell commands.
- Local `/work-agents/.venv` is the preferred environment for M0/M1 data prep and Qwen tokenizer packing because NemTron is known to lack `cosmos_xenna`.
- NemTron training should run under `/root/nemotron_session5_venv` with Qwen3 4B TP=2 on GPUs 0/1 unless the host state requires a different allocation.
- With `nproc_per_node=2`, the formal scale-up planner needs `global_batch_size=2`; `global_batch_size=1` fails `plan_m1_agentic_sft_training.py` batch geometry validation.
- Cosmos/Xenna packed split parquet files are symlinks into `packed_qwen/runs/...`; use `Path.glob("*.parquet")` or `find -L` when validating them, not plain `find -type f`.
- Checkpoint export fact: `iter_0000122` converts successfully with Megatron-Bridge `AutoBridge.from_hf_pretrained(...).export_ckpt(...)` using Qwen3 base path `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`.
- Model artifact fact: the exported HF directory is registered as manifest artifact `task071-qwen3-4b-agentic-sft-iter0000122-hf:v1` under `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/artifacts`.
- Deployment fact: SGLang can serve the exported checkpoint on NemTron GPU 0 via `http://127.0.0.1:30000/v1/chat/completions` with model id `task071-qwen3-4b-agentic-sft-iter0000122-hf`.
- Eval blocker: current `m1_full_basket.yaml` uses `adlr_*` registry aliases that are not present in `nemo-evaluator-launcher==0.2.5` task mapping; examples of mapped task names are `AIME_2025`, `gpqa_diamond`, `scicode`, `bfclv3`, `tooltalk`, `ns_hmmt_feb2025`, and `ns_wmt24pp`.
- Eval blocker: NemTron has no Docker, `sbatch`, or `srun`, so `nemo-evaluator-launcher` cannot run local Docker-based eval containers or Slurm jobs on this node even when the model endpoint is live.
