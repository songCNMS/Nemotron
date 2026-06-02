# task274_qwen_aime_v11_data_safety_ready_review_s1 - Data safety readiness review

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_1,SESSION=2 -->

## Background

V11 repaired data/packing issues through task262 and related reviews. Session 40
runtime proof makes pilot planning possible again, but the data gate still must
preserve decontamination and avoid AIME2025 train prompts/labels.

## Goal

Review whether the V11 data/split/sidecar state is still safe to use for a
future Qwen3-4B pilot after Session 40, and identify any data-side blockers
before training can be considered.

## Scope

- Review task246/task253/task254/task262/task265 evidence and the current
  decontamination rules.
- Confirm AIME2025 remains held out for eval/decontamination only.
- Identify which packed/data artifacts are acceptable, stale, or require
  rematerialization before a future pilot.
- Produce exact blocker/no-blocker disposition for data readiness only.

## Boundaries

- Do not create or modify training data, run training, live eval, export,
  endpoint, promotion, AIME2025 train data, 30B/8-GPU, merge, or main push.
- Do not delete or overwrite shared files.

## Expected Output

- Branch:
  `intern_nemotron_worker_1/task274_qwen_aime_v11_data_safety_ready_review_s1`.
- PR because docs/status changed; mailbox report required.
- Mailbox report with data readiness disposition, artifact paths/revisions,
  contamination/decontamination checks reviewed, and boundary confirmation.

## Acceptance Criteria

- PASS: data-side prerequisites for a future Qwen3-4B V11 pilot are exact and
  AIME2025 remains held out.
- BLOCK: data artifacts are stale, unsafe, or ambiguous and need a new worker
  implementation task.
- FAIL: any train-data mutation or AIME2025 train use occurs.

## Current Worker State

- Branch:
  `intern_nemotron_worker_1/task274_qwen_aime_v11_data_safety_ready_review_s1`.
- Base: current `origin/main` at
  `958c283813960d90749d51c8880354b89caa7ff8`.
- Task docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `b7e58017ce2324ef24bf130e7ad84082b5271d1f`.
- Status: completed; PR #342 merged at approved head
  `5e96158211a2bac010e9b65107152e2f5ad635a6`.
- Report:
  `workspace/tasks/task274_qwen_aime_v11_data_safety_ready_review_s1/data_safety_ready_review_report.md`.
- PR:
  https://github.com/songCNMS/Nemotron/pull/342
- Disposition: source/decontamination evidence is safe, but currently visible
  packed Qwen data remains blocked for direct pilot use until V11 data is
  rematerialized with task262 collision-safe split logic.
