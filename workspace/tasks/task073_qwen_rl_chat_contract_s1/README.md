# task073_qwen_rl_chat_contract_s1 - Qwen RL chat contract audit/fix

<!-- METADATA:STATUS=MERGED,ASSIGNEE=intern_nem_dev_2 -->

## Background

PM assigned a critical Qwen RL chat-contract audit/fix from latest `main`.
The target model family is Qwen, so the RL tokenizer kwargs and rollout
serving kwargs must share one explicit Qwen chat-template contract.

## Goals

- Pin `policy.tokenizer.chat_template_kwargs` in all owned RL stage configs.
- Keep tokenizer kwargs identical to
  `policy.generation.vllm_cfg.http_server_serving_chat_kwargs.chat_template_kwargs`.
- Remove or resolve conflicting sibling `policy.generation.vllm_cfg.enable_thinking`.
- Keep Qwen assistant-turn `stop_strings` contract covered by tests.
- Preserve PR flow; no direct push to `main` or self-merge.

## Acceptance Criteria

- [x] Focused RL chat-template kwargs consistency tests cover tokenizer/serving equality.
- [x] Focused tests fail on missing tokenizer kwargs and sibling/nested `enable_thinking` conflicts.
- [x] Stop strings stay aligned on the Qwen assistant-turn delimiter.
- [x] PR opened: https://github.com/songCNMS/Nemotron/pull/172
- [x] PR #172 merged through PR flow.
