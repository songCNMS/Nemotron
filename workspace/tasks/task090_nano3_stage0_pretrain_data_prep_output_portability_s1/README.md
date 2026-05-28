# task090_nano3_stage0_pretrain_data_prep_output_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=14 -->

## Background

PM assigned a Nano3 stage0 pretrain portability follow-up after the data/training
pipeline audit found
`src/nemotron/recipes/nano3/stage0_pretrain/config/data_prep/default.yaml`
still defaulted `output_dir` to a named-user `/lustre/.../mromeijn/...` path.
That path could silently write data-prep outputs to a developer-local location.

## Goals

- Start from `origin/main` at `c26dedfcbff336e3f827f59f39230d713d260e29`
  or newer.
- Replace the Nano3 stage0 pretrain default `output_dir` with a portable
  `NEMO_RUN_DIR`-relative path consistent with `data_prep.py`.
- Preserve `tiny.yaml` unless a concrete inconsistency is found.
- Add focused static tests covering output-dir portability and required
  Nano3 stage0 pretrain data-prep fields.
- Avoid live data prep, training, endpoints, W&B, cluster jobs, deploy, direct
  main/master push, or self-merge.

## Acceptance Criteria

- [x] Local `main` synced to `c26dedfcbff336e3f827f59f39230d713d260e29`.
- [x] Nano3 stage0 pretrain `default.yaml` no longer uses a named-user
  `/lustre` output default.
- [x] Focused static tests cover `default.yaml` and `tiny.yaml`.
- [x] Required validation passed locally.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/197
