# task031_agentic_sft_v1 - History Log

<!-- METADATA:SESSION=1 -->

---

## Session 1 - 2026-05-22 - intern_nem_dev_1

Started from clean `main` at `bb215b8739c99eaaafa812bb4be42e021cabebc7`
after the PM latest-main correction.

Branch: `intern_nem_dev_1/task031_agentic_sft_v1_s1`

Implemented:
- Added sandbox-only Agentic SFT v1 supervision-builder contract near the
  M1 Agentic SFT preparation code.
- Added failure-rollout candidate schema and conversion from local/synthetic
  `LocalRolloutStore` records.
- Preserved multi-turn assistant tool calls and tool observations in generated
  repair-supervision examples.
- Added metadata fields for self-correction trajectories, failure-repair
  family, compact-reasoning mode, source rollout id, source model/env, and
  source metrics.
- Added focused tests for schema, failed rollout selection, multi-turn
  observation handling, compact reasoning metadata, and LocalRolloutStore input.

Validation:
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_agentic_sft_v1_s1.py tests/recipes/super3/test_m1_agentic_sft.py`
  -> 55 passed, 1 skipped, 1 warning.
- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/__init__.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/agentic_sft_v1.py`
  -> passed.
- `git diff --check` -> passed.

Out of scope:
- task013 cluster SFT loss/run verification.
- task070 and task026 live cross-harness runtime/data collection.
- OpenHands/OpenCode/Codex production traces and real failure rollout mining.
- Packed SFT generation at scale, cluster training run, W&B/lineage
  publication, and eval gate against live M1/M2 checkpoints.

---
