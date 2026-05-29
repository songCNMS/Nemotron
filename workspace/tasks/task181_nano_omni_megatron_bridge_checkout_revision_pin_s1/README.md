# task181_nano_omni_megatron_bridge_checkout_revision_pin_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

## Scope

- Fix the Nano-Omni Megatron-Bridge notebook branch reference from the stale
  `nemotron-3-omni` spelling to the existing `nemotron_3_omni` branch context.
- Pin the executable Megatron-Bridge setup to the PM-provided exact commit with
  a `git rev-parse HEAD` equality guard.
- Add focused static notebook coverage for the checkout pin, branch context,
  cleared outputs, and preserved Nano-Omni Megatron-Bridge / CORD-v2 LoRA
  context.

## Boundaries

- Static notebook/test/docs only.
- No notebook execution, live git clone/fetch/checkout, container build,
  dataset download, data prep, train/eval, endpoint, W&B, cluster job, deploy,
  artifact op, direct `main`/`master` push, or self-merge.

## Status

- Base: `3394671e1fe0b5cf5aecd9d53b714f1c6e007b2f`
- Branch: `intern_nem_dev_3/task181_nano_omni_megatron_bridge_checkout_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/288
- Head: `b7a13b55617032fc90f781a48f3b98134d109821`
- Checks: focused static notebook pytest, adjacent Nano-Omni CORD-v2 notebook
  pytest, py_compile, Ruff, structured notebook probe, stale-branch grep,
  added-line live-surface scan, and `git diff --check` passed.
