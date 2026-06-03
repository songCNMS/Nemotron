# task326_qwen_all_sft_next_phase_safety_review_s1 - Next-phase safety review

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

Task321 accepted the current docs/evidence merge/runbook sequence. The next
phase now has task322 raw materialize/count/decontam, task323 validation-skip
preflight, task324 blend design, and task325 M1 launcher remediation route.
These tasks are prerequisites for any later all-SFT packed contract, training,
or eval task.

## Goal

Provide an independent safety/runbook review for the next phase so lead can
gate task322-task325 outputs consistently before any later packing/training/eval
assignment.

## Scope

- Review task318-task321 accepted gates and the new task322-task325 docs.
- Define exact evidence that must be present before:
  - raw sources can enter a packed contract;
  - a train-only validation-skip root can be used for optimizer launch;
  - MMLU-aware blend design can be converted into packed data;
  - M1 rows can be evaluated.
- Produce a fail-closed checklist, PR sequencing recommendation, and residual
  risk matrix.
- If task322-task325 reports appear before closeout, include their current
  branch/head/PR states; otherwise list them as pending.

## Boundaries

- Read-only docs/review only.
- No merge, self-merge, main push, data materialization, packing, training,
  eval, export, endpoint, promotion, task255 reuse, AIME2025 train data, or
  shared deletion.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task326_qwen_all_sft_next_phase_safety_review_s1`.
- Report:
  `workspace/tasks/task326_qwen_all_sft_next_phase_safety_review_s1/next_phase_safety_review_report.md`.
- Mailbox report with branch/head/PR or blocker, checklist, sequencing, and
  residual risk.

## Acceptance Criteria

- `APPROVE_SAFETY_REVIEW`: evidence gates and sequencing are concrete and
  preserve all boundaries.
- `REQUEST_CHANGES`: checklist misses task322-task325 risks or ordering.
- `BLOCK`: next-phase tasks conflict or cannot be safely sequenced.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task318-task321, task322-task325
- Gate state: no runtime action authorized.

## Worker Closeout Snapshot

- Report:
  `workspace/tasks/task326_qwen_all_sft_next_phase_safety_review_s1/next_phase_safety_review_report.md`.
- Worker PR: #389.
- Disposition: `APPROVE_SAFETY_REVIEW`.
- task322/#388, task323/#385, task324/#386, and task325/#387 are visible with
  lead gate comments at refreshed review time.
- task322/#388 is accepted only as partial evidence with exclusions: 2 included
  sources / 23,997 rows, while 10 large sources remain fail-closed blockers for
  full all-SFT packed/training handoff.
- Safety ordering: task322 materialize/count/decontam and task324 blend design
  before any packed repair contract; accepted packed data plus lead-gated
  task323 validation-skip/exit proof before optimizer launch; task325 route
  before any M1 row execution.
