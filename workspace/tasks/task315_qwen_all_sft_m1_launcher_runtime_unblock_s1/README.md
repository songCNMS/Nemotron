# task315_qwen_all_sft_m1_launcher_runtime_unblock_s1 - Qwen all-SFT M1 launcher runtime unblock

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Background

Task311 could not run M1 launcher basket rows. Worker_3's report says local and
NemTron environments lack `nemo-evaluator-launcher`, `nemo-evaluator`, Docker,
Slurm, and benchmark modules such as `nemo_evaluator`, `lm_eval`,
`simple_evals`, `nemo_skills`, `bfcl_eval`, and `tau2_bench`.

Corrected-Qwen AIME2025/HMMT/MMLU-Pro endpoint evidence exists, but it is not
the M1 launcher harness.

## Goal

Determine a safe, task-owned route to make M1 launcher rows runnable, or return
an exact fail-closed blocker with required dependencies, credentials, container
runtime, and command plan.

## Scope

- Inspect current repo launcher/eval docs and task071/task311 mapping.
- Recheck local worker, NemTron, and any documented LTP route for:
  - `nemo-evaluator-launcher`;
  - `nemo-evaluator`;
  - Docker or equivalent container runtime;
  - Slurm or equivalent scheduler;
  - benchmark modules and datasets;
  - credentials/API needs for rows such as BFCL.
- Produce an exact row-by-row M1 feasibility matrix:
  - runnable now;
  - runnable after task-owned dependency/env setup;
  - blocked by credentials/runtime/data/context;
  - exact task missing/unavailable.
- If a safe setup route exists, provide dry-run/preflight commands and a
  resource plan. Do not run full benchmark rows without lead release.

## Boundaries

- Read-only runtime/provenance audit and dry-run/import probes only.
- Do not run benchmark rows, train, pack, export, endpoint, promote, merge, push
  main, reuse task255, use AIME2025 train data, or delete shared files.
- Do not install/uninstall system packages or mutate shared runtime state.
- If a local user/task-owned env is needed, report the proposed commands and
  wait for lead release before performing heavyweight setup.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1`.
- Report:
  `workspace/tasks/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1/m1_launcher_runtime_unblock_report.md`.
- Optional task-owned output root with probe logs, command/env manifests, and
  dependency matrix.
- Mailbox report with branch/head/PR or blocker, probes run, exact missing
  components, row feasibility matrix, and recommended next gate.

## Acceptance Criteria

- `PASS_ROUTE_PLAN`: a safe, bounded route exists to run at least one M1 row
  later, with exact dependencies and commands, without violating boundaries.
- `BLOCK_RUNTIME`: no safe launcher route exists in current local/NemTron/LTP
  state, with exact missing dependency/resource/credential evidence.
- `REQUEST_CHANGES`: probe evidence, row mapping, or command plan is incomplete.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Review target: task311 M1 availability report at #371 head
  `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`
- Gate state: no M1 benchmark execution authorized.
