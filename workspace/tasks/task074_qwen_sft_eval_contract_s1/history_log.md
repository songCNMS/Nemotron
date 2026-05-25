# task074_qwen_sft_eval_contract_s1 - History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-25

- PM assigned the critical Qwen SFT/eval chat-contract audit/fix.
- Preserved existing bookkeeping branch `intern_nem_dev_3/task036_sync_s4_history` and started from synced `main` at `9456469509539648a5a2ab4e4b36a16fa46a95dd`.
- Created branch `intern_nem_dev_3/task074_qwen_sft_eval_contract_s1`.
- Added SFT data-prep plumbing for `chat_template_kwargs` and `chat_template=tokenizer` so Qwen runs can use the tokenizer-provided Qwen chat template.
- Updated Qwen scale-up planning to emit explicit Qwen tokenizer, template, and chat-template kwargs overrides.
- Added Qwen train-entry tokenizer resolution guards so Qwen entrypoints do not silently use the Nemotron tokenizer fallback.
- Added eval-side Qwen contract metadata and task audit caveats while stripping that audit block before launcher execution.
- Verified focused pytest, py_compile for touched Python modules, and `git diff --check`.
