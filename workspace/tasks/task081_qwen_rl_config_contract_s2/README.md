# task081_qwen_rl_config_contract_s2 - Qwen RL config contract S2

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

PM assigned a critical second-wave RL config contract audit after task078.
The four stage-specific RL configs pin the Qwen chat-template kwargs and
`<|im_end|>` stop string, but the generic runnable
`stage2_rl/config/default.yaml` still carried an implicit legacy contract.

## Goals

- Preserve local work, sync from latest `origin/main`, and work only on a
  feature branch.
- Fix or explicitly guard the generic RL default so it cannot silently drift
  from the active Qwen target contract.
- Expand focused RL config tests to cover the generic config surface.
- Keep live RL training, cluster launches, and self-merge out of scope.

## Acceptance Criteria

- [x] Generic `stage2_rl/config/default.yaml` has an explicit Qwen-compatible
  tokenizer, rollout-serving, and stop-string contract or an equivalent guard.
- [x] Focused RL kwargs and stop-string tests cover the generic config.
- [x] Stage2 RL config audit for null/missing/conflicting Qwen chat-template
  fields is reported.
- [x] Required local checks pass.
- [ ] PR opened to `main`; no direct push to `main` or `master`.

## PR

- Pending.
