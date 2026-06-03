# task314_qwen_all_sft_mmlu_pro_regression_forensics_s1 - Qwen all-SFT MMLU-Pro regression forensics

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=92 -->

## Background

Task311/#371 Session 12 produced corrected-Qwen eval evidence for the all-SFT
task310 checkpoint. AIME2025 and HMMT improved versus base, but MMLU-Pro
regressed by 2 rows under the same endpoint route:

- MMLU-Pro base: `6758/12032 = 0.5616688829787234`.
- MMLU-Pro FT: `6756/12032 = 0.5615026595744681`.
- Current #371 head: `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`.

The benchmark basket is therefore not uniformly non-regressing, and no
promotion or further training claim is allowed from task311.

## Goal

Independently analyze the MMLU-Pro base-vs-FT row-level regression and identify
whether the `-2` result is explained by parser/prompt/protocol artifacts,
category-level drift, endpoint/completion differences, or actual model behavior.

## Scope

- Use task311 artifacts under:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z`.
- Compare MMLU-Pro base and FT:
  - `results.jsonl`;
  - `full_completions.jsonl`;
  - `parser_diagnostics.jsonl`;
  - `summary.json`;
  - row and command/env manifests.
- Produce row transition counts:
  - base correct -> FT wrong;
  - base wrong -> FT correct;
  - both correct;
  - both wrong.
- Report category-level deltas, prompt/hash alignment, parser extraction
  differences, response-shape differences, and any suspicious non-determinism
  or artifact mismatch.
- Confirm whether task311's `FAIL_MMLU_PRO_BELOW_BASE_WITH_AIME_HMMT_PASS`
  disposition remains correct.
- Recommend the next gate action: docs-only fail closeout, targeted evaluator
  fix, data/training repair task, or bounded rerun request.

## Boundaries

- Read-only artifact analysis and docs/status only.
- Do not train, pack, run new eval rows, export, launch endpoint, promote,
  merge, push main, reuse task255, use AIME2025 train data, or delete shared
  files.
- Do not rewrite worker_3's #371 branch.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1`.
- Report:
  `workspace/tasks/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/mmlu_pro_regression_forensics_report.md`.
- Optional task-owned analysis tables under worker_1 outputs with row-level
  transition CSV/JSONL, checksums, and commands/env.
- Mailbox report with branch/head/PR or blocker, exact artifacts inspected,
  row/category deltas, findings, residual risk, and recommended gate action.

## Acceptance Criteria

- `APPROVE_FORENSICS`: row-level and category-level regression evidence is
  complete and supports a clear gate recommendation.
- `REQUEST_CHANGES`: analysis is plausible but misses key artifacts, row
  transitions, checksums, or protocol details.
- `BLOCK`: artifact access fails, evidence contradicts task311 metrics, or a
  boundary violation is observed.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Review target: #371 current head `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`
- Gate state: no promotion or new training/eval authorized.
