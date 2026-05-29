# task179_super_grpo_dapo_rl_checkout_revision_pin_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

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
- PR head: `9b64e919381df048bd58b84b6051332103319604`
- Merge SHA: `3394671e1fe0b5cf5aecd9d53b714f1c6e007b2f`
- Checks: focused static notebook pytest, py_compile, Ruff, structured notebook
  probe, product stale branch-only grep, added-line live-surface scan, and
  `git diff --check` passed.
- Session 2: PR #285 passed PM gate and independent exact-head gate, then
  squash-merged to `main`; local `main` was synced to the merge SHA.
