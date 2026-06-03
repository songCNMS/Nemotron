# task317_qwen_all_sft_task311_closeout_review_s1 - Independent review of task311 closeout

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=79 -->

## Background

Task312 reviewed earlier all-SFT evidence before task311 Session 12 produced
the final corrected-Qwen/M1 closeout. #371 is now OPEN/CLEAN at
`9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`, with lead gate comments
`4615730412` and `4615769907`.

## Goal

Independently review current #371/task311 closeout evidence and determine
whether it is safe to merge as evidence/fail-closeout documentation only, while
preserving the no-promotion/no-self-merge boundaries.

## Scope

- Review #371 current head `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`.
- Confirm drift from `2e4482ea` is bookkeeping-only.
- Verify task311 reports, runner scope, artifact hashes, metrics, endpoint
  cleanup evidence, M1 launcher blocker matrix, and boundary confirmations.
- Confirm the lead disposition:
  `APPROVE_EVIDENCE_CLOSEOUT / PERFORMANCE_FAIL_MIXED`.
- Recommend merge-as-docs-closeout, request changes, or block.

## Boundaries

- Read-only review and docs/status only.
- Do not modify product code, train, eval, export, endpoint, promote, merge,
  push main, self-merge, rewrite worker branches, reuse task255, use AIME2025
  train data, or delete shared files.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task317_qwen_all_sft_task311_closeout_review_s1`.
- Report:
  `workspace/tasks/task317_qwen_all_sft_task311_closeout_review_s1/task311_closeout_independent_review_report.md`.
- Mailbox report with branch/head/PR or blocker, commands used, evidence
  checked, pass/fail for each claim, and recommendation.

## Acceptance Criteria

- `APPROVE_DOCS_CLOSEOUT`: #371 can be merged as evidence/fail-closeout docs
  only, with no promotion or further authorization.
- `REQUEST_CHANGES`: #371 has incomplete evidence, stale head handling, or
  wording that could imply promotion.
- `BLOCK`: evidence is unsafe, metrics contradict artifacts, or a boundary
  violation is found.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Review target: #371 current head `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`
- Gate state: review only; no merge by worker without coordinator/authorized
  non-author path.
