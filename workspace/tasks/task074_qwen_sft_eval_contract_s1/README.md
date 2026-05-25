# task074_qwen_sft_eval_contract_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

Qwen SFT and eval runs must use a Qwen-compatible tokenizer and chat-template
contract. Matching repo `super3.jinja` across SFT/RL/eval is not sufficient
for Qwen target runs because Qwen tokenizer defaults and eval kwargs can drift
from Nemotron/Super3 assumptions.

## Goals

- Make Qwen scale-up SFT data prep explicitly use the Qwen tokenizer's chat
  template and Qwen chat-template kwargs.
- Prevent Qwen training entrypoints from silently falling back to the Nemotron
  tokenizer default when the Qwen HF model path is known.
- Tie eval `extra.chat_template_kwargs` to the same Qwen contract used by SFT
  and record eval task caveats for completions, parser-sensitive prompts, and
  short generation caps.

## Acceptance

- Focused tests cover SFT data wrapping, Qwen tokenizer/template planner
  overrides, and eval contract metadata.
- The Qwen scale-up data-prep script emits explicit `tokenizer.model`,
  `chat_template`, and `chat_template_kwargs` overrides.
- Eval contract metadata is retained for audit but stripped before
  `nemo-evaluator-launcher` invocation.
