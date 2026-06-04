# task325_qwen_all_sft_m1_launcher_remediation_route_s1 - M1 launcher remediation route

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_3,SESSION=78 -->

## Background

Task315 concluded the M1 launcher basket is blocked under current runtime
evidence: launcher packages/modules or container routes are unavailable, and
0/19 rows are runnable now. The active all-SFT objective still requires
available benchmarks and unavailable-row documentation, so M1 cannot be ignored.

## Goal

Find a safe remediation route or exact blocker for making M1 launcher rows
runnable in a later eval-only task, without running benchmark rows now.

## Scope

- Re-review task315 findings and current repo/host/NemTron/LTP evidence.
- Identify exact package/module/container/runtime requirements for each M1
  launcher-available row group and the 5 exact-task unavailable rows.
- Check only safe import/version/config probes in task-owned environments if
  needed; do not execute benchmark rows.
- Propose a later eval-only launch route, or confirm `BLOCK_RUNTIME` with exact
  missing packages, credentials, containers, modules, or permissions.
- Preserve documentation of unavailable rows and why they remain unavailable.

## Boundaries

- No benchmark row execution, model eval, training, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, shared deletion, main push,
  merge, or self-merge.
- No system package installs or shared environment mutation without later lead
  release. Task-owned local venv/import probes are allowed only if documented
  and non-destructive.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task325_qwen_all_sft_m1_launcher_remediation_route_s1`.
- Report:
  `workspace/tasks/task325_qwen_all_sft_m1_launcher_remediation_route_s1/m1_launcher_remediation_route_report.md`.
- Optional task-owned output root with import probes/logs.
- Mailbox report with branch/head/PR or blocker, runnable-row route, unavailable
  row matrix, commands/env, and exact recommendation.

## Acceptance Criteria

- `PASS_REMEDIATION_ROUTE`: a concrete later eval-only M1 launcher route is
  available with required env/container/commands and no benchmark rows run now.
- `BLOCK_RUNTIME_CONFIRMED`: no safe route exists; missing runtime pieces and
  unavailable rows are fully documented.
- `REQUEST_CHANGES`: route or blocker matrix is incomplete.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task315, task311, task321
- Gate state: no benchmark/eval authorized.
