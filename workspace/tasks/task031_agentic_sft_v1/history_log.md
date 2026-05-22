# task031_agentic_sft_v1 - History Log

<!-- METADATA:SESSION=2 -->

---

## Session 2 - 2026-05-22 - intern_nem_dev_1

Confirmed PR #149 was merged through PR flow at
`2026-05-22T03:34:12Z`; merge commit:
`f4acf31adf4220474c04bb9dbdae2d2508e9fe5e`.

Sync:
- Started from clean `intern_nem_dev_1/task031_agentic_sft_v1_s1` tracking
  origin.
- Switched to `main` before any further work, per PM closeout instruction.
- Ran `git pull --ff-only origin main`; local `main` fast-forwarded from
  `bb215b8739c99eaaafa812bb4be42e021cabebc7` to
  `f4acf31adf4220474c04bb9dbdae2d2508e9fe5e`.
- Confirmed `git status --short --branch` is clean on latest `main` before
  creating this closeout branch.

Closeout:
- Marked task031 completed after PR #149 merge.
- Set intern status to Idle because PM explicitly said there is no new sandbox
  assignment right now.
- Kept residual blockers separate from Session 1 sandbox scope: task013 cluster
  SFT loss/run verification, task070/task026 live cross-harness runtime/data
  collection, OpenHands/OpenCode/Codex production traces, real failure rollout
  mining, packed SFT generation at scale, cluster training, W&B/lineage
  publication, and eval gate against live M1/M2 checkpoints.

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
