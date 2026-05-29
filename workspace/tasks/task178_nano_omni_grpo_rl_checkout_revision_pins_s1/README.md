# task178_nano_omni_grpo_rl_checkout_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

Status: In progress
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task178_nano_omni_grpo_rl_checkout_revision_pins_s1`
Base: `67bb428e4a992c608b8795795ced4f3fa9b9271c`
PR: https://github.com/songCNMS/Nemotron/pull/286

## Summary

Pin the Nano-Omni GRPO cookbook NeMo-RL checkout examples so executable setup
uses a fixed `nano-v3-omni` commit instead of a drifting branch head.

## Scope

- `usage-cookbook/Nemotron-3-Nano-Omni/grpo/grpo_training_cookbook.ipynb`
- `usage-cookbook/Nemotron-3-Nano-Omni/grpo_nemo_gym/grpo_nemo_gym_training_cookbook.ipynb`
- Focused static notebook test under `tests/usage_cookbook/`
- Task/status docs for `intern_nem_dev_2`

## Pin

- Repo: `https://github.com/NVIDIA-NeMo/RL`
- Branch context: `nano-v3-omni`
- Revision: `98ba11c0a77e177a903cd3756570684437a08e8d`

## Boundaries

- Static notebook/test/docs only.
- No notebook execution, live git clone/fetch/checkout, container build, data
  prep, train/eval, endpoint, W&B, cluster, deploy, artifact operation, direct
  `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_nano_omni_grpo_nemo_rl_revision.py` (4 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_nano_omni_grpo_nemo_rl_revision.py`
- PASS: `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_nano_omni_grpo_nemo_rl_revision.py`
- PASS: structured static notebook probe for exact NeMo-RL repo/branch/revision checkout guards
- PASS: added-line live-surface scan showed notebook command examples and static docs/status only
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
