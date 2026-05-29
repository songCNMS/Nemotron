# task179_super_grpo_dapo_rl_checkout_revision_pin_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

## Scope

- Pin the Super GRPO-DAPO notebook NeMo-RL `super-v3` checkout to the
  PM-provided exact commit.
- Add focused static notebook coverage for the exact checkout, preserved branch
  context, guarded setup cell, cleared outputs, and retained GRPO-DAPO context.

## Boundaries

- Static notebook/test/docs only.
- No notebook execution, live git clone/fetch/checkout, container build, data
  prep, train/eval, endpoint, W&B, cluster job, deploy, artifact op, direct
  `main`/`master` push, or self-merge.

## Status

- Base: `67bb428e4a992c608b8795795ced4f3fa9b9271c`
- Branch: `intern_nem_dev_3/task179_super_grpo_dapo_rl_checkout_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/285
- Head: `841fad547609db32fc5a4975c60bd11601cb8c15`
- Checks: focused static notebook pytest, py_compile, Ruff, structured notebook
  probe, product stale branch-only grep, added-line live-surface scan, and
  `git diff --check` passed.
