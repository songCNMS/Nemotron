# task031_agentic_sft_v1 - History Log

<!-- METADATA:SESSION=2 -->

---

## Session 2 - 2026-05-23 - intern_nem_dev_1

Started from clean `main` at `5b940c90267f543d8fe5c8bd78ec2e119258b6a4`
after the PM high-priority sync instruction.

Branch: `intern_nem_dev_1/task031_agentic_sft_v1_s2`

Implemented:
- Added deterministic cross-harness routing for local/synthetic Agentic SFT v1
  traces across OpenHands, OpenCode, Codex, browser, terminal, and generic
  routes.
- Added explicit trace harness/source/family/route metadata to generated
  failure-repair examples while preserving Session 1 repair behavior and
  compact-reasoning metadata.
- Added a routed LocalRolloutStore builder that orders failed records by stable
  route priority and supports route filtering without production trace mining.
- Added focused Session 2 tests for schema fields, explicit metadata routing,
  env/tool hint routing, route metadata preservation, deterministic routed
  ordering, and route filtering.

Validation:
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_agentic_sft_v1_s2.py tests/recipes/super3/test_agentic_sft_v1_s1.py tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_rollout_store.py`
  -> 74 passed, 1 skipped, 1 warning.
- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/__init__.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/agentic_sft_v1.py`
  -> passed.
- `git diff --check` -> passed.

Out of scope:
- Production OpenHands/OpenCode/Codex trace mining.
- Packed SFT generation at scale.
- Training launch.
- W&B/lineage publication.
- Live eval gate.

---

## Session 1 - 2026-05-22 - intern_nem_dev_1

Started from clean `main` at `bb215b8739c99eaaafa812bb4be42e021cabebc7`
after the PM latest-main correction.

Branch: `intern_nem_dev_1/task031_agentic_sft_v1_s1`

PR: https://github.com/songCNMS/Nemotron/pull/149
Initial implementation SHA: `8380db8308a0dc4d5a9e9ae14956b7bedc908993`

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
- `git diff --cached --check` -> passed before commit.

Out of scope:
- task013 cluster SFT loss/run verification.
- task070 and task026 live cross-harness runtime/data collection.
- OpenHands/OpenCode/Codex production traces and real failure rollout mining.
- Packed SFT generation at scale, cluster training run, W&B/lineage
  publication, and eval gate against live M1/M2 checkpoints.

---
