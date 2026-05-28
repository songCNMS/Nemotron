# task089_stage0_pretrain_data_prep_output_portability_s1 - Stage0 pretrain data-prep output portability

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

Stage0 pretrain data-prep configs for the non-tiny runnable defaults hard-coded
output directories under a named `/lustre` user path. `tiny.yaml` already uses a
portable repo-relative output directory.

## Goals

- Replace hard-coded `/lustre` output directories in `default`, `phase1`,
  `phase2`, and `long_context` data-prep configs with portable defaults.
- Keep phase-specific output subdirectories distinct.
- Preserve blend paths, tokenizer settings, shard/split counts, sampling,
  `force`, and observability fields.
- Add focused static tests that reject hard-coded `/lustre` or named-user
  output paths and verify required config fields.

## Out Of Scope

- Live dataset downloads, tokenization, W&B runs, cluster jobs, deployments,
  endpoint calls, promotion, direct `main` pushes, or self-merge.

## Acceptance

- Focused stage0 pretrain data-prep config pytest passes.
- Static probe confirms runnable data-prep config output defaults no longer use
  `/lustre` or named-user paths.
- `python -m py_compile` passes for touched Python tests.
- Ruff passes for touched Python tests when available.
- `git diff --check` and `git diff --cached --check` pass.
