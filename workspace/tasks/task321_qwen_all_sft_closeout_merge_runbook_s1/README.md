# task321_qwen_all_sft_closeout_merge_runbook_s1 - All-SFT closeout merge/runbook sequencing

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

The all-SFT evidence/follow-up PR set is open and clean:

- #371 task311 evidence/fail-closeout docs;
- #377 task316 repair plan docs;
- #378 task317 independent #371 closeout review;
- #379 task315 M1 runtime blocker docs;
- #380 task314 MMLU-Pro forensics docs.

The current boundary requires coordinator/authorized non-author merge. No
worker self-merge is allowed.

## Goal

Produce a merge/runbook sequencing recommendation for the documentation PR set
and the next lead-gated repair tasks, without merging or changing PR branches.

## Scope

- Review current PR heads and dependencies.
- Recommend merge ordering or hold conditions for #371/#377/#378/#379/#380.
- Confirm which PRs are evidence/fail-closeout docs, blocker docs, or planning
  docs.
- Update the runbook state for what is allowed next:
  validation/termination preflight, raw blend/decontam feasibility, and
  data-repair linkage analysis only.
- Identify any PR that should stay hold due stale head, wording, or dependency.

## Boundaries

- Read-only review/docs only.
- Do not merge, self-merge, push main, train, eval, pack, export, endpoint,
  promote, reuse task255, use AIME2025 train data, or delete shared files.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task321_qwen_all_sft_closeout_merge_runbook_s1`.
- Report:
  `workspace/tasks/task321_qwen_all_sft_closeout_merge_runbook_s1/closeout_merge_runbook_report.md`.
- Mailbox report with branch/head/PR or blocker, PR ordering, hold conditions,
  and next-task runbook.

## Acceptance Criteria

- `APPROVE_RUNBOOK`: sequencing is concrete and preserves all no-promotion and
  no-self-merge boundaries.
- `REQUEST_CHANGES`: dependency/order or residual risk is incomplete.
- `BLOCK`: PR state is stale/conflicting or merge sequencing cannot be safely
  recommended.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: #371, #377, #378, #379, #380, task318-task320
- Gate state: no merge by worker; no runtime action.

## Worker Closeout Snapshot

- Report: `workspace/tasks/task321_qwen_all_sft_closeout_merge_runbook_s1/closeout_merge_runbook_report.md`.
- Disposition: `APPROVE_RUNBOOK`.
- Current PR sequencing recommendation: support docs #378/#380/#379, then #371
  evidence/fail-closeout docs, then #377 repair plan docs, all through
  coordinator/authorized non-author merge only and only while exact heads remain
  clean/mergeable.
- Next repair work remains limited to task318 validation/exit preflight,
  task319 raw blend/decontam feasibility, and task320 MMLU data-repair linkage;
  no runtime or promotion action is released.
