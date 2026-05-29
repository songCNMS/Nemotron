# task168_lora_text2sql_bird_dataset_revision_pins_s1

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nem_dev_2 -->

Status: Merged and verified
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task168_lora_text2sql_bird_dataset_revision_pins_s1`
Base: `6328c018a86da7448e11a03bc1c71afc38e067f2`
PR: https://github.com/songCNMS/Nemotron/pull/275 (merged)
Merge Commit: `6500fdaa27735197da87ca25d641a2883b00e8e6`

## Summary

Pin the BIRD Text2SQL cookbook training dataset loaders to PM-verified Hugging
Face dataset revisions so cookbook fine-tuning data cannot drift silently.

## Scope

- `usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/dataset_bird.py`
- `usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/dataset_bird_reasoning.py`
- Focused static/AST tests under `tests/usage_cookbook/`
- Task/status docs for `intern_nem_dev_2`

## Pins

- `xu3kev/BIRD-SQL-data-train`:
  `9122256f9d14752ed80fb9b7d158e21d9f9261aa`
- `meowterspace45/bird-sql-train-with-reasoning`:
  `9e351e0057819f1b0917debb83c8e12f321157a4`

## Boundaries

- No live dataset download, Text2SQL data prep run, training/eval, endpoint,
  W&B, cluster, deploy, artifact upload/download, direct `main`/`master` push,
  or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_lora_text2sql_bird_revision_pins.py` (3 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/dataset_bird.py usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/dataset_bird_reasoning.py tests/usage_cookbook/test_lora_text2sql_bird_revision_pins.py`
- PASS: `/work-agents/.venv/bin/ruff check usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/dataset_bird.py usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/dataset_bird_reasoning.py tests/usage_cookbook/test_lora_text2sql_bird_revision_pins.py`
- PASS: structured static/AST probe for exact repos/revisions and matching `load_dataset` calls
- PASS: added-line live-surface scan showed only cookbook static pinning/tests/docs/status lines
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
