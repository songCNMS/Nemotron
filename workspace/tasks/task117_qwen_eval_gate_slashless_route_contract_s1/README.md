# task117_qwen_eval_gate_slashless_route_contract_s1

## Scope

- Extend the Qwen eval repro gate intended-path validator so it requires both
  slashless OpenAI routes:
  - `intended_eval_path.chat_route == "/v1/chat/completions"`
  - `intended_eval_path.completions_route == "/v1/completions"`
- Preserve existing evidence-record route checks as chat-completions-only where
  the evidence itself is chat endpoint evidence.
- Add focused tests for missing and trailing-slash intended completions routes.

## Boundaries

- No live benchmark/eval run.
- No endpoint call, W&B run, cluster job, deployment, direct `main`/`master`
  push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task117_qwen_eval_gate_slashless_route_contract_s1`
- Base: `40eab704f6d02dd65e94189f098e712be6a1f6f2`
- PR: https://github.com/songCNMS/Nemotron/pull/223
