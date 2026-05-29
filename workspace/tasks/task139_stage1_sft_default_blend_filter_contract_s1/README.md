# task139_stage1_sft_default_blend_filter_contract_s1 - Stage1 SFT default blend/filter

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

The generic Super3 stage1 SFT data-prep `default.yaml` still pointed at the
Nano3 stage1 SFT blend and carried `used_in_filter: nano_v3`. That is unsafe
for the generic Super3 profile because the row filter rejects records with a
missing `used_in` field whenever a filter is configured.

## Goals

- Point generic Super3 stage1 SFT default data prep at the Super3-owned blend.
- Neutralize the stale Nano-specific `used_in_filter`.
- Keep Qwen agentic and agentic_v0 profiles unchanged.
- Add focused static/config tests and a structured YAML probe.

## Acceptance Criteria

- [x] Branch starts from `main`
  `70d3541cdbc993fa113bdc62fa9be61f83b72d9e`.
- [x] Generic Super3 SFT default blend path contains the Super3 data-prep
  blend path and not `/nano3/`.
- [x] Generic default `used_in_filter` is not `nano_v3`.
- [x] Super3 stage1 SFT blend has non-empty `datasets`.
- [x] Row-filter helper test documents why missing `used_in` plus stale filter
  is dangerous.
- [x] Focused pytest, py_compile, Ruff, structured probe, and diff checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/246
