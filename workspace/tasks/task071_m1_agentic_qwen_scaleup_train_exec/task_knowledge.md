# task071_m1_agentic_qwen_scaleup_train_exec - task_knowledge

<!-- METADATA:SESSION=1 -->

## Notes

- Use `plan_qwen_scaleup_run.py` from latest `main` to generate the execution scripts instead of hand-writing shell commands.
- Local `/work-agents/.venv` is the preferred environment for M0/M1 data prep and Qwen tokenizer packing because NemTron is known to lack `cosmos_xenna`.
- NemTron training should run under `/root/nemotron_session5_venv` with Qwen3 4B TP=2 on GPUs 0/1 unless the host state requires a different allocation.
