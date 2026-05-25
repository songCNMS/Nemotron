# task074_qwen_sft_eval_contract_s1 - History Log

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-25

- PM assigned the critical Qwen SFT/eval chat-contract audit/fix.
- Preserved existing bookkeeping branch `intern_nem_dev_3/task036_sync_s4_history` and started from synced `main` at `9456469509539648a5a2ab4e4b36a16fa46a95dd`.
- Created branch `intern_nem_dev_3/task074_qwen_sft_eval_contract_s1`.
- Added SFT data-prep plumbing for `chat_template_kwargs` and `chat_template=tokenizer` so Qwen runs can use the tokenizer-provided Qwen chat template.
- Updated Qwen scale-up planning to emit explicit Qwen tokenizer, template, and chat-template kwargs overrides.
- Added Qwen train-entry tokenizer resolution guards so Qwen entrypoints do not silently use the Nemotron tokenizer fallback.
- Added eval-side Qwen contract metadata and task audit caveats while stripping that audit block before launcher execution.
- Verified focused pytest, py_compile for touched Python modules, and `git diff --check`.
- Opened PR https://github.com/songCNMS/Nemotron/pull/174 to `main`.

## Session 2 - 2026-05-25

- PM reported PR #174 merged and latest `origin/main` at `ab1fbbf64f892abda34582a7cfc18229fb6f1824`.
- Confirmed the task branch `intern_nem_dev_3/task074_qwen_sft_eval_contract_s1` was clean and pushed before syncing.
- Switched to `main`, fetched `origin/main`, and fast-forwarded with `git pull --ff-only origin main`.
- Verified local `main`, `origin/main`, and `HEAD` reached `ab1fbbf64f892abda34582a7cfc18229fb6f1824`.
- Created bookkeeping branch `intern_nem_dev_3/task074_postmerge_sync_s2` from synced `main`; no new implementation work is active.
