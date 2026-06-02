# task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1 - post-AIME runbook refresh

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Background

#351/task289 was open and clean, but it predated the final task293 AIME evidence
and remained stale/HOLD. task293 read-only artifacts now show a corrected
AIME2025 metric pass for task285 Qwen3-4B iter2:

- FT `12/30 = 0.4`
- accepted base `11/30 = 0.36666666666666664`
- delta `+1/30`
- artifact run:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`

The pass does not authorize export, endpoint, promotion, 30B, or 8-GPU.
Worker_3 official closeout is PR #356, currently OPEN/CLEAN/MERGEABLE at exact
head `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`. No task294 independent review
branch or PR is visible in this refresh.

## Goal

Refresh the V11 runbook/provenance/status docs so they accurately reflect the
current post-AIME state, including the remaining gate holds and residual risks.

## Scope

- Start from current `origin/main`.
- Preferred PR plan: refresh existing #351 / branch
  `intern_nemotron_worker_5/task289_qwen_aime_v11_post_smoke_runbook_provenance_s1`
  if it can be updated cleanly with no unrelated changes.
- Alternative PR plan: create a new branch
  `intern_nemotron_worker_5/task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1`
  and report that #351 should be closed or superseded.
- Update only runbook/provenance/task docs/status/report surfaces.
- Include task293 score, artifact roots, checksums, same-harness proof summary,
  task294 review status if available, and unresolved risks.

## Session 1 Result

- Chose the preferred plan and refreshed existing #351 because #351 was
  OPEN/base main/MERGEABLE at head `ac85acace556f3861576314fc2684733498074f2`.
- Updated task289 runbook/provenance report and carried task266 runbook matrix
  against current `origin/main`
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a`.
- Recorded #354/task291 MERGED at `2026-06-02T08:30:04Z` with merge commit
  `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf`.
- Recorded #355/task292 MERGED at `2026-06-02T08:37:35Z` with merge commit
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a` and decision
  `APPROVE_CANARY_ROUTE_PASS`.
- Recorded #356/task293 OPEN/base main/CLEAN/MERGEABLE at exact head
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`.
- Recorded task293 corrected AIME2025 FT `12/30 = 0.4` versus accepted base
  `11/30 = 0.36666666666666664`, with artifact roots and checksum values.
- Recorded task294 independent review as pending/not visible after remote PR and
  branch checks.
- Kept export, endpoint, promotion, task255 reuse, AIME2025 train data, shared
  deletion, 30B, and 8-GPU blocked.
- No runtime, training, canary, AIME re-eval, task243 eval, export, endpoint,
  promotion, merge, main push, or artifact mutation action was performed.

## Required Content

- Current V11 sequence state through task293.
- Accepted base comparator: task247 Qwen3-4B corrected AIME2025 `11/30`.
- Candidate FT metric: task285 iter2 task293 `12/30 = 0.4`.
- Explicit note that AIME2025 prompts/labels were held out for eval/decontam
  only and are not trainable data.
- Explicit note that task255 remains discarded and must not be reused.
- Explicit note that no export, endpoint, promotion, 30B, or 8-GPU is authorized.
- Residual risks:
  - task293 `sampling_exact_parameter_match=false` semantic greedy-match review;
  - task292 synthetic canary detokenized fallback residual;
  - worker_3 official closeout/PR and task294 review status, if still pending.
- Artifact/provenance paths and checksums sufficient for reproduction.

## Boundaries

- Do not run training, live eval, AIME re-eval, export, endpoint launch,
  promotion, task255 reuse, AIME2025 train data, shared deletion, 30B, or 8-GPU.
- Do not merge, self-merge, or push main.
- Do not edit model code or training/eval code for this task.

## Expected Output

- Updated #351 or a new task295 PR.
- Official mailbox report with:
  - branch/head/PR;
  - whether #351 was refreshed or superseded;
  - files changed;
  - exact task293 metrics and artifact paths recorded;
  - task294/worker_3 dependency status;
  - boundary confirmation.

## Acceptance Criteria

- APPROVE: runbook/provenance accurately reflects current task293 evidence and
  gate holds, with no stale task289-only wording and no promotion/scale claim.
- REQUEST_CHANGES: docs omit critical artifacts, metrics, residual risks, or
  dependency status.
- BLOCK: update would require forbidden training/eval/export/endpoint/promotion,
  AIME2025 train data, task255 reuse, shared deletion, 30B, or 8-GPU.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related tasks: task247, task285, task289, task291, task292, task293, task294
- Gate: documentation/provenance only. No release, promotion, endpoint, export,
  or scale-up authorization.
