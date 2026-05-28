# task093_nano3_stage3_eval_chat_contract_s1 - Nano3 stage3 eval chat contract

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

Nano3 stage3 eval config pins evaluator tokenizer fields but did not explicitly
pin `extra.chat_template_kwargs`. Task092 is aligning Nano3 stage2 RL to the
Qwen-style Nano3 chat contract, so eval should not depend on checkpoint
tokenizer defaults that may drift from training and rollout rendering.

## Goals

- Add `evaluation.nemo_evaluator_config.config.params.extra.chat_template_kwargs`
  to Nano3 stage3 eval default.
- Use the task092/Super3 Qwen contract values:
  `enable_thinking: false` and `truncate_history_thinking: false`.
- Preserve tokenizer, tokenizer backend, benchmark task list, deployment
  command, mounts, artifact resolution, W&B export, and launcher behavior.
- Add focused static tests under `tests/recipes/nano3/stage3_eval/`.

## Gate Dependency

- PM should gate/merge this after task092 PR #199, or re-check the contract
  against task092 if both PRs remain open concurrently.

## Out Of Scope

- Live evals, endpoint calls, W&B export runs, cluster jobs, deployments,
  benchmark execution, direct `main`/`master` pushes, self-merge, or promotion.

## Acceptance

- Focused Nano3 stage3 eval chat-template pytest passes.
- `python -m py_compile` passes for the new focused test files.
- Ruff passes for the new focused test files when available.
- Static probe confirms Nano3 eval extra chat-template kwargs are explicit.
- `git diff --check` and `git diff --cached --check` pass.
