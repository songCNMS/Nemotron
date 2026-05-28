# task099_super3_generic_rl_tokenizer_name_contract_s1 - Generic Super3 RL tokenizer name contract

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2,SESSION=11 -->

## Background

PM assigned a static Super3 stage2 RL config follow-up after `main` reached
`9ab5e264b110095c0a1c9ea33c9b49ccd8d44909`. The generic RL default and tiny
configs had been aligned on Qwen chat kwargs, stop strings, tool parser, and
reasoning parser, but still hard-coded
`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16` as
`policy.tokenizer.name`.

## Goals

- Start from latest `origin/main` at or after
  `9ab5e264b110095c0a1c9ea33c9b49ccd8d44909`.
- Update generic Super3 stage2 RL `default.yaml` and `tiny.yaml` so
  `policy.tokenizer.name` follows `${policy.model_name}`.
- Keep stage-specific RL configs, Nano3 configs, launch behavior, node counts,
  and live runtime behavior unchanged.
- Add focused tests proving the fixed Nemotron Nano tokenizer default is gone
  from generic default/tiny and the Qwen RL contract protections still pass.

## Acceptance Criteria

- [x] Branch created from current `origin/main`.
- [x] Generic default and tiny tokenizer names follow `${policy.model_name}`.
- [x] Focused test coverage added to the Super3 RL contract shard.
- [x] Required pytest, py_compile, ruff, static tokenizer probe, and whitespace
  checks pass locally.
- [ ] PR opened to `main`.
