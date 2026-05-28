# task083_qwen_rl_reasoning_parser_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. supervisor request: PM assigned a static/config/test-only follow-up to align the generic RL reasoning parser contract with stage-specific Qwen RL configs.
2. technical fact: stage-specific RL configs use `tool_parser=qwen3_coder`, `reasoning_parser=nano_v3`, and `reasoning_parser_plugin=nemo_rl/utils/nano_v3_reasoning_parser.py`.
3. technical fact: the generic `stage2_rl/config/default.yaml` was already covered by Qwen kwargs/stop-string tests after task081, so parser drift there is a runnable contract mismatch.
4. implementation choice: align the generic config to the stage-specific `nano_v3` parser contract and lock it with focused config tests.
