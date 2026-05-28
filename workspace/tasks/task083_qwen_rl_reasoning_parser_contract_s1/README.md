# task083_qwen_rl_reasoning_parser_contract_s1 - Qwen RL reasoning parser contract

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

PM assigned a follow-up audit after PR #188 merged the generic RL
Qwen chat-template kwargs and stop-string contract. The generic runnable
`stage2_rl/config/default.yaml` still used `reasoning_parser: deepseek_r1`,
while the four stage-specific RL configs use `reasoning_parser: nano_v3`
with `reasoning_parser_plugin: nemo_rl/utils/nano_v3_reasoning_parser.py`.

## Goals

- Start from latest `origin/main` and preserve local work.
- Align the generic RL HTTP serving reasoning parser contract with the
  stage-specific Qwen RL configs.
- Extend focused static config tests so the generic and stage-specific RL
  configs agree on `tool_parser`, `reasoning_parser`, and any required
  `reasoning_parser_plugin`.
- Keep scope static/config/test/docs only.

## Acceptance Criteria

- [x] Generic `stage2_rl/config/default.yaml` uses the same parser contract
  as the stage-specific RL defaults.
- [x] Focused tests cover generic plus stage-specific tool/parser/plugin
  agreement.
- [x] Required validation passes locally.
- [x] PR opened to `main`; no direct push to `main` or `master`.

## PR

- https://github.com/songCNMS/Nemotron/pull/190
