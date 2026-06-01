# task217_mamba_causal_conv_train_stack_unblock_probe_s1 - Mamba causal-conv PM review recovery

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Background

The old branch `origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1` contains a ReadyForPMReview diagnosis for the task216 runtime blocker `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`. The old assignee `intern_nem_dev_3` no longer belongs to the current team.

The branch reports that `mamba_ssm==2.3.2.post1` and `selective_scan_cuda` load from task209's contained target, but `causal-conv1d` / `causal_conv1d_cuda` are absent, causing `causal_conv1d_fwd_function=None`. The old PM assigned the contained build/probe follow-up to task218.

## Goal

Recover the ReadyForPMReview state into a current-team gate recommendation: accept/close task217 as a no-launch root-cause diagnosis, request changes, or route a precise follow-up if task218 did not cover the unblock.

## Scope

- Read `origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`.
- Inspect old task217 docs, validation report, branch diff, and referenced task216/task218/task209 evidence as read-only inputs.
- Produce `workspace/tasks/task217_mamba_causal_conv_train_stack_unblock_probe_s1/pm_review_recovery.md` in your worker branch.
- Prepare a new worker-owned documentation PR only if persistent current-team closeout docs are needed.

## Boundaries

- Do not push to `origin/intern_nem_dev_3/*`.
- Do not build/install packages, launch training, run benchmarks/evals/endpoints, copy models, upload artifacts, push to `main`/`master`, self-merge, or modify product code.
- This is PM-review recovery and evidence audit, not implementation.

## Expected Output

- A PM-review recovery report with approve/request-changes/block recommendation.
- A statement on whether task218 and later live evidence cover the task217 unblock request.
- PR decision: prefer a new worker-owned docs/closeout PR if state must be persisted; old branch is read-only input.

## Acceptance Criteria

- The report states the exact source branch, old assignee, current worker, and source blocker.
- The report validates whether the task217 diagnosis is internally consistent with task216 failure evidence.
- The report does not rely on newly run implementation tests by the team lead.
- Worker reports through mailbox with branch, commit, PR if any, files changed, and residual risk.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Source branch: `origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`
- Old task: `task217_mamba_causal_conv_train_stack_unblock_probe_s1`
- Old assignee: `intern_nem_dev_3`
