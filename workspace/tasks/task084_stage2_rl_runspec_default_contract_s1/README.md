# task084_stage2_rl_runspec_default_contract_s1 - Stage2 RL runspec default contract

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

PM assigned a static follow-up after PR #190 merged. The generic Super3 RL
runspec in `stage2_rl/train.py` declares config default `tiny`, while direct
script execution defaults to `config/default.yaml`. The generic `tiny.yaml`
did not inherit `default.yaml`, so the runspec default path could bypass the
Qwen RL chat-template, parser, and stop-string contract.

## Goals

- Start from latest `origin/main` and preserve local work.
- Make generic `config/tiny.yaml` inherit or otherwise enforce the Qwen RL
  contract from `config/default.yaml`.
- Add focused static regression coverage proving the runspec default path
  resolves the Qwen tokenizer, rollout-serving, parser, plugin, and stop-string
  contract.
- Keep scope static config/test/docs only.

## Acceptance Criteria

- [x] Local `main` synced to `d2f37f7e647bce186922f41da9476fa6e734576c` or newer.
- [x] Generic runspec default `tiny` path inherits the generic RL default config.
- [x] Focused tests prove the resolved runspec default path has `policy.generation`,
  `<|im_end|>` stop strings, tokenizer/serving `chat_template_kwargs`,
  `tool_parser=qwen3_coder`, `reasoning_parser=nano_v3`, and
  `reasoning_parser_plugin=nemo_rl/utils/nano_v3_reasoning_parser.py`.
- [x] Required validation passes locally.
- [x] PR opened to `main`; no direct push to `main` or `master`.

## PR

- https://github.com/songCNMS/Nemotron/pull/191
