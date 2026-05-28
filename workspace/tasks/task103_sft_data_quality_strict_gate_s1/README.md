# task103_sft_data_quality_strict_gate_s1 - M1 Agentic SFT strict data-quality gate

<!-- METADATA:STATUS=ReadyForGate,ASSIGNEE=intern_nem_dev_2,SESSION=12 -->

## Background

PM assigned a PR-sized strict data-quality enforcement path for
`prepare_m1_agentic_sft.py` after `main` reached
`efcf0e6f5b5c043cc4c9b701d4faabe63ce69156`. The prep step already computed
missing source metadata, duplicate source keys, duplicate normalized prompts,
and train/val leakage counters, but only recorded them in manifest/report.

## Goals

- Start from latest `origin/main` at or after
  `efcf0e6f5b5c043cc4c9b701d4faabe63ce69156`.
- Add an opt-in strict gate for M1 Agentic SFT prep, exposed as
  `--fail-on-data-quality-issues`.
- Fail strict mode when any checked data-quality count is nonzero:
  missing required source metadata, duplicate source keys, duplicate normalized
  prompts, train/val source-key overlap, or train/val normalized-prompt overlap.
- Preserve default report-only behavior for smoke/backcompat paths.
- Record strict enforcement status and checked counts in manifest/report.
- Add focused tests for default report-only behavior, strict failure, and clean
  strict pass.

## Acceptance Criteria

- [x] Branch created from current `origin/main`.
- [x] Strict data-quality gate implemented behind an explicit opt-in flag.
- [x] Manifest/report record strict enforcement status and checked issue counts.
- [x] Focused M1 SFT tests cover default, failing strict, and clean strict paths.
- [x] Required pytest, py_compile, ruff, structured prepare probe, and whitespace
  checks pass locally.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/212
