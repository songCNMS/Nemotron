# task093_nano3_stage3_eval_chat_contract_s1 knowledge

<!-- METADATA:SESSION=8 -->

## Working Notes

- Task092 PR #199 is the Nano3 stage2 RL counterpart and pins tokenizer plus
  vLLM serving chat-template kwargs to `enable_thinking: false` and
  `truncate_history_thinking: false`.
- Nano3 stage3 eval should mirror those bools under
  `evaluation.nemo_evaluator_config.config.params.extra.chat_template_kwargs`.
- This task is static config/test only; live evals and task092 merge-gate
  validation remain outside the PR implementation.
