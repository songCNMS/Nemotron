# task206_qwen_sft_train_stack_unblock_probe_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Goal

Probe whether any local or project-provided environment can unblock the minimal
Qwen SFT one-iteration smoke that task203 could not run.

## Baseline

`0460c1f0262875fb27ae530d30cd80d805752851`

## Scope

- Check `/work-agents/.venv/bin/python` imports for `torch`, `megatron`,
  `megatron.bridge`, and `nemo_run`.
- Check bounded alternate environment inventory: `conda env list`,
  `/work-agents/*/.venv/bin/python`, and obvious project venvs only.
- Check GPU visibility with `nvidia-smi` or equivalent if available.
- Check Qwen model path and packed Qwen splits.
- Always run the `m1_agentic_smoke` dry-run under
  `/tmp/nemotron-live-validation/task206`.
- Run one-iteration local smoke only if all prerequisites are present.
- Run focused SFT/Qwen validators and diff checks.

## Boundaries

- No package install.
- No cluster launch.
- No full train/eval.
- No endpoint, W&B, deploy, artifact upload.
- No direct `main`/`master` push or self-merge.
