# task081_qwen_rl_config_contract_s2 - Task Knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

1. supervisor request: PM assigned a second-wave audit/fix for generic RL config Qwen chat-contract drift after task078.
2. technical fact: the stage-specific RL configs already pin tokenizer and vLLM serving `chat_template_kwargs` to `enable_thinking=false` and `truncate_history_thinking=false`.
3. technical fact: Qwen RL generation should stop on the assistant-turn delimiter `<|im_end|>` to avoid running past the chat response boundary.
4. implementation choice: make the generic `stage2_rl/config/default.yaml` explicitly Qwen-compatible and expand existing focused tests to cover it.
