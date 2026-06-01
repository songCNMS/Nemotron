# task240_task217_independent_followup_audit_s1 - Independent task217 follow-up audit

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=0 -->

## Background

Worker 2 owns recovery review for old task217 ReadyForPMReview. The old task217 branch says task218 owns the contained `causal-conv1d` build/probe follow-up, so the team lead needs an independent audit of whether later evidence covers that follow-up.

## Goal

Independently audit task217's follow-up chain and report whether task217 can be accepted as complete no-launch diagnosis, or whether task218/task216+ still leaves a recovery gap.

## Scope

- Read `origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`.
- Read later relevant branches, especially task218 and task216+ live evidence, only as needed to verify follow-up coverage.
- Report findings through mailbox; only create a docs PR if team lead explicitly requests after the report.

## Boundaries

- Do not build/install packages, run training, run benchmarks/evals/endpoints, copy models, upload artifacts, direct-push main/master, self-merge, mutate old branches, or modify product code.

## Expected Output

- Mailbox report naming branches/commits inspected, whether task218 covered the task217 unblock request, and any residual gap.
- Verification arrangement: this is the independent tester/auditor for worker 2's task217 PM-review recovery.
- PR decision: no PR expected unless the audit finds docs that must be persisted.

## Acceptance Criteria

- The report states whether task217's causal-conv root cause is supported by the cited evidence.
- The report states whether task218 and task216+ evidence close the unblock loop.
- The report identifies any missing artifacts or unverifiable claims.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Source branch: `origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`
- Paired recovery task: `task217_mamba_causal_conv_train_stack_unblock_probe_s1`
