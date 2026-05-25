# task074_qwen_sft_eval_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

- For Qwen target SFT data prep, use `tokenizer.model=<Qwen model/path>` together with `chat_template=tokenizer` so the HF tokenizer's own Qwen chat template is used.
- Qwen SFT/eval contract kwargs are `enable_thinking: false` and `truncate_history_thinking: false`.
- `super3.jinja` remains the repo-pinned Super3/Nemotron default, but it is not a sufficient default for Qwen target runs.
- The Qwen scale-up planner records a `qwen_chat_contract` manifest block and emits matching data-prep overrides in `run_local_data_prep.sh`.
- Eval config carries audit-only `qwen_chat_contract` metadata; `normalize_evaluator_launcher_config` strips it before handing config to `nemo-evaluator-launcher`.
- Eval task caveats are separated into valid Qwen-chat tasks, completion/non-chat prompt tasks, and short-generation-cap or parser-sensitive tasks.
- Session 2 added no new implementation knowledge; it only confirmed PR #174 is merged and local `main` is synced to `ab1fbbf64f892abda34582a7cfc18229fb6f1824`.
