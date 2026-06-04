# task333_qwen_all_sft_combined_packed_contract_s1 - history

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_1,SESSION=84 -->

## 2026-06-04 UTC - Assigned

- Created as the no-training successor after #394/task332 and #395/task331
  merged into `origin/main`.
- Scope is a fresh combined all-SFT packed-data contract candidate using task299
  constrained seed, task332 split policy/exclusions, and task331 SWE
  no-tools-header provenance.
- Assigned to `intern_nemotron_worker_1` on branch
  `intern_nemotron_worker_1/task333_qwen_all_sft_combined_packed_contract_s1`.
- Global gate remains HOLD: no task310 release, training, eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion, or
  30B release.

## 2026-06-04 UTC - Request Changes

- #396 exact head `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e` remains
  `OPEN`/`CLEAN`, but lead gate is `REQUEST_CHANGES/HOLD`.
- Blocking issue: the report table's task299 seed row-manifest SHA256 values do
  not match the assigned artifact root
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`
  or `manifests/source_provenance.json`.
- Required worker_1 follow-up: refresh the #396 report/provenance table to match
  the actual artifact evidence, or provide a new fully verified artifact root and
  report. No training/eval/export/endpoint/promotion/30B release is authorized.

## 2026-06-04 UTC - Report Hash Fix Submitted

- Worker_1 pushed #396 refreshed head
  `9a9471e35e3d80f6bf2995478ddf4bd1ef785a66`.
- Lead drift check confirmed changes from old head
  `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e` are limited to worker_1 status and
  `combined_packed_contract_report.md`.
- The report now uses the assigned `run_20260604T074500Z` task299 seed
  row-manifest SHA256 values. #396 is still HOLD pending refreshed task334
  independent review for the new exact head.
- Worker_1 subsequently pushed metadata-only head
  `6261daaa37172caa11929b0b88f685b63f987221`. Lead verified
  `9a9471e35e3d80f6bf2995478ddf4bd1ef785a66..6261daaa37172caa11929b0b88f685b63f987221`
  changes only worker_1 status plus task333 history/task_knowledge; the report
  remains unchanged from the hash fix. Refreshed task334 review must target
  exact head `6261daaa`.
