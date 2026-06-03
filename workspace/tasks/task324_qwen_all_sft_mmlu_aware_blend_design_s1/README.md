# task324_qwen_all_sft_mmlu_aware_blend_design_s1 - MMLU-aware all-SFT blend design

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=96 -->

## Background

Task320 accepted the MMLU-Pro regression as a data-repair constraint. Task311
showed AIME25/HMMT gains but MMLU-Pro `-2`; task314 showed math `+13` but
non-math aggregate `-15`, with 86/92 loss rows outside math. Task319 showed
broader raw sources are feasible candidates but not yet packing-ready.

## Goal

Design a future all-SFT blend contract that preserves math gains while adding
MMLU-Pro retention coverage. The design must be ready to consume task322
materialized/decontaminated sources, but must not materialize data, pack,
train, or evaluate in this task.

## Scope

- Map task319's 12 raw source candidates and task299/V11 seed sources into
  task320 retention buckets: physical sciences, bio-health, humanities/social,
  technical/coding, math, and broad instruction/other.
- Propose source/bucket inclusion criteria, target reporting fields, and
  fail-closed minimums for rows, input tokens, supervised tokens, checksums,
  decontam, and train/valid/test splits.
- Define how task322 outputs should be consumed by a later packed-contract
  task, including how to exclude blocked sources.
- Define later same-harness evaluation requirements if training is separately
  authorized: MMLU-Pro aggregate >= base, non-math aggregate >= 0, AIME25 >=
  base, HMMT >= base, and parser/row/endpoint cleanup evidence.

## Boundaries

- Docs/analysis only.
- No data materialization, final packing, training, eval rerun, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
  product-code edits, main push, merge, or self-merge.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task324_qwen_all_sft_mmlu_aware_blend_design_s1`.
- Report:
  `workspace/tasks/task324_qwen_all_sft_mmlu_aware_blend_design_s1/mmlu_aware_blend_design_report.md`.
- Mailbox report with branch/head/PR or blocker, bucket mapping, blend contract
  requirements, dependency on task322, and residual risk.

## Acceptance Criteria

- `APPROVE_BLEND_DESIGN`: concrete MMLU-aware blend constraints are ready for a
  later packed-data contract task after task322 source evidence.
- `REQUEST_CHANGES`: bucket mapping or acceptance metrics are too generic.
- `BLOCK`: task319/task320 evidence is insufficient or contradictory.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task319, task320, task314, task308, task309
- Gate state: no materialization/packing/training/eval authorized.
