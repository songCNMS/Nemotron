# task320_qwen_all_sft_mmlu_data_repair_linkage_s1 - MMLU-Pro drift to data-repair linkage

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_1,SESSION=78 -->

## Background

Task314 forensics showed task311 MMLU-Pro `-2` is real answer-choice drift, not
an evaluator artifact. Category deltas showed math gains but losses in physics,
health, chemistry, history, other, and smaller categories. Task316 recommends
repairing the all-SFT data blend before more 30B training.

## Goal

Map task314's MMLU-Pro row/category drift to data-repair requirements for the
next all-SFT blend, without training or packing.

## Scope

- Use task314 output tables and task308/task309 data inventory.
- Summarize which MMLU-Pro categories lost/gained and how that should constrain
  data-blend repair.
- Identify whether current accepted task299/V11 seed over-focuses math relative
  to broad MMLU-Pro retention needs.
- Recommend source/category balancing constraints or validation metrics that a
  later data repair/packing task should satisfy.
- Coordinate with task319 if available; otherwise mark dependencies clearly.

## Boundaries

- Analysis/docs only.
- No data materialization, final packing, training, eval rerun, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
  main push, merge, or self-merge.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task320_qwen_all_sft_mmlu_data_repair_linkage_s1`.
- Report:
  `workspace/tasks/task320_qwen_all_sft_mmlu_data_repair_linkage_s1/mmlu_data_repair_linkage_report.md`.
- Mailbox report with branch/head/PR or blocker, category findings, data-repair
  requirements, and residual risk.

## Acceptance Criteria

- `APPROVE_LINKAGE`: MMLU-Pro drift is translated into concrete data-repair
  constraints for later lead-gated tasks.
- `REQUEST_CHANGES`: linkage is too generic or misses key category/source
  evidence.
- `BLOCK`: task314/task308/task309 evidence is unavailable or contradictory.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task314, task308, task309, task316
- Gate state: no training/eval/packing authorized.
