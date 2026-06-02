# task297_qwen_aime_v11_current_main_equivalence_review_s1 - current-main equivalence review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=75 -->

## Background

task296 is assigned to worker_1 to determine whether the existing V11
task285/task293 artifacts are product-code-equivalent to current main
`2d84ec75960fb51ba9091427638b00083625e137` after coordinator PR #312 merged.

Lead needs an independent review before accepting path A and avoiding a fresh
current-main data/training/evaluation rerun.

## Goal

Independently review the exact task296 report/head and decide whether lead may
accept:

`APPROVE_A_PROVED_NO_RERUN_WITH_RESIDUALS`

or must request more evidence / launch path B:

`REQUEST_CHANGES` or `BLOCK_B_REQUIRED_RERUN`.

## Scope

- Wait for worker_1 task296 branch/report/mailbox. If no task296 report is
  visible, report `HOLD_WAITING_TASK296`.
- Review the exact task296 head and report.
- Reproduce the essential read-only git/GitHub checks:
  - `origin/main` equals `2d84ec75960fb51ba9091427638b00083625e137`;
  - #312 mergedAt/mergeCommit/head match coordinator report;
  - #312 changed-file list is coordinator docs only;
  - task285/task293 relevant code/script paths are unchanged or
    artifact-equivalent as claimed;
  - task285/task293 artifact roots/checksums and metrics are accurately carried.
- Confirm residuals and boundaries are preserved:
  task276 sparse valid/test, task285 post-train eval RC=1, task292 detokenized
  fallback residual, task293 `sampling_exact_parameter_match=false`, no
  export/endpoint/promotion/further training/eval/task255/AIME2025 train
  data/shared deletion/30B/8-GPU.

## Boundaries

- Read-only review only.
- Do not edit code or artifacts.
- Do not run training, canary, AIME/task243 eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, main push, merge, 30B, or
  8-GPU.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task297_qwen_aime_v11_current_main_equivalence_review_s1`
- Review report under this task directory.
- Mailbox report to lead with:
  - exact task296 head/report reviewed;
  - commands/checks run;
  - decision `APPROVE_A_PROVED_NO_RERUN_WITH_RESIDUALS`,
    `REQUEST_CHANGES`, `BLOCK_B_REQUIRED_RERUN`, or `HOLD_WAITING_TASK296`;
  - residual risks and boundary confirmation.

## Acceptance Criteria

- APPROVE: independent review confirms current main is product-code-equivalent
  for task285/task293 evidence and no rerun is needed.
- REQUEST-CHANGES: task296 evidence is incomplete or ambiguous but fixable.
- BLOCK: product-code equivalence is false or unprovable; lead should launch
  fresh current-main pipeline tasks.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related task: task296
- Related PRs: #312, #350, #351, #356, #357
