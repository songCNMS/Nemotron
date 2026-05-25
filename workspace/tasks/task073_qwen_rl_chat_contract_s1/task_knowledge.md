# task073_qwen_rl_chat_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

- Qwen RL chat-template contract is explicitly `enable_thinking: false` and `truncate_history_thinking: false` for the current configs.
- Tokenizer-side `policy.tokenizer.chat_template_kwargs` must equal rollout serving `policy.generation.vllm_cfg.http_server_serving_chat_kwargs.chat_template_kwargs`.
- A sibling `policy.generation.vllm_cfg.enable_thinking` can silently conflict with nested serving kwargs, so tests now reject mismatch.
- Qwen assistant-turn stop delimiter remains `<|im_end|>` across RLVR1, SWE1, SWE2, and RLHF.
- Post-merge sync note: task073's Qwen RL chat contract is present on `main` at `ab1fbbf64f892abda34582a7cfc18229fb6f1824`; Session 2 added no new technical contract beyond recording the merged state.
