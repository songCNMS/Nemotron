# task073_qwen_rl_chat_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

- Qwen RL chat-template contract is explicitly `enable_thinking: false` and `truncate_history_thinking: false` for the current configs.
- Tokenizer-side `policy.tokenizer.chat_template_kwargs` must equal rollout serving `policy.generation.vllm_cfg.http_server_serving_chat_kwargs.chat_template_kwargs`.
- A sibling `policy.generation.vllm_cfg.enable_thinking` can silently conflict with nested serving kwargs, so tests now reject mismatch.
- Qwen assistant-turn stop delimiter remains `<|im_end|>` across RLVR1, SWE1, SWE2, and RLHF.
