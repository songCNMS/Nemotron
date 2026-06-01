# task238_task203_206_209_coverage_audit_s1 - Task203/206/209 coverage audit

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_3,SESSION=2 -->

## Background

Coordinator instructed that task203/task206/task209 must only be restored after confirming they were not covered by task216+ live evidence. These old branches are not merged into current `origin/main`, and their old assignees are no longer current team members.

## Goal

Determine whether task203, task206, and task209 represent real unfinished work or are superseded by later task216+ live validation and closeout evidence.

## Scope

- Read old branches for task203, task206, and task209.
- Compare them against later branch evidence for task216, task217, task218, task219, task220, task221, task222, task223, task224, task225, task227, task230, task231, task233, and task234 as needed.
- Produce `workspace/tasks/task238_task203_206_209_coverage_audit_s1/coverage_matrix.md`.
- Recommend one of: `covered/no recovery`, `recover docs only`, or `create new implementation task`.

## Boundaries

- Read-only branch, PR, and artifact inspection only.
- Do not run implementation tests, launches, endpoints, package installs, Docker, downloads, model copies, artifact uploads, direct `main`/`master` pushes, self-merge, or product code edits.

## Expected Output

- A coverage matrix mapping task203/task206/task209 to later evidence or gaps.
- A concrete recovery recommendation for each of the three tasks.
- PR decision: no PR unless persistent audit docs are needed; if needed, use a new worker-owned docs PR from current `origin/main`.

## Acceptance Criteria

- Each old task is classified with evidence, not assumption.
- Any proposed restoration includes exact task_id, owner, scope, and reason it was not covered by task216+ evidence.
- Worker reports through mailbox with branch, commit, PR if any, files changed, and residual risk.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Source branches: `origin/intern_nem_dev_2/task203_qwen_live_sft_train_smoke_s1`, `origin/intern_nem_dev_2/task206_qwen_sft_train_stack_unblock_probe_s1`, `origin/intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`
- Old tasks: `task203_qwen_live_sft_train_smoke_s1`, `task206_qwen_sft_train_stack_unblock_probe_s1`, `task209_nemtron_h200_sft_live_s1`
- Old assignee family: `intern_nem_dev_2`
