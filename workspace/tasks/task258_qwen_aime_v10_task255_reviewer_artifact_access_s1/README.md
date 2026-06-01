# task258_qwen_aime_v10_task255_reviewer_artifact_access_s1 - task255 reviewer artifact access

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=4 -->

## Lead Observation

worker_2 branch
`origin/intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1`
is visible at `d0a05c5e9ad37b831fd75bc9ae852cb121527f83` with
reviewer-readable artifact bundle evidence and PR #331 OPEN/CLEAN. worker_2
official mailbox reports `PASS_REVIEWER_ACCESS_READY` and recommends
`ready_for_task256_re_review`. worker_5/task259 approved the artifact access
evidence. Lead approved #331 for worker self-merge at exact head
`d0a05c5e9ad37b831fd75bc9ae852cb121527f83`.

#331 merged at `2026-06-01T21:34:07Z` with merge commit
`9c6cdb653c93f4bebc4c7bcfc47c7e28d7552d90`. #329 was closed unmerged as
superseded at `2026-06-01T21:34:54Z`.

## Background

task255 produced a Qwen3-4B one-iteration checkpoint and HF export, recorded in
PR #329 at head `d62036e405edc5daa322c09bb89da19b176bb7bf`.

task256 independently reviewed the task255 report and logs and found them
internally consistent, but returned `REQUEST_CHANGES/HOLD` because worker_5
could not read the checkpoint/export directories under `/root/task255_...` from
the review environment. #329 is therefore not approved.

Separately, lead read-only monitoring observed task257 FT AIME25 result
`0/30 = 0.0` against accepted base `11/30`, but worker_3 official closeout is
still pending and task256 artifact access blocks any final PASS.

## Goal

Provide reviewer-accessible task255 artifact evidence, or report the exact
blocker that prevents doing so, so lead can decide whether #329 can close as an
artifact/failure record or must remain blocked.

## Scope

- Start from current `origin/main`.
- Preserve task255 PR #329 head and evidence unless a docs/status refresh is
  needed.
- Make the task255 checkpoint and HF export independently reviewable by
  worker_5/lead without requiring worker_2-private `/root` access. Acceptable
  options include:
  - a copied artifact bundle or manifest in a reviewer-readable path;
  - a stable shared path with exact access instructions;
  - a signed inventory/checksum package sufficient for independent hash
    comparison if full 53G checkpoint copy is not practical;
  - an explicit resource/access blocker with remediation path.
- Record exact source paths, destination paths, file counts, sizes, hashes, and
  commands.

## Boundaries

- Do not train, export again, or run AIME/task243 evaluation.
- Do not modify model artifacts except copying or generating read-only
  manifests/checksum inventories for review.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not claim promotion, go/no-go PASS, or 30B/8-GPU clearance.
- Do not push `main`, self-merge, or merge #329.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1`.
- PR only if repo docs/status/report files change; artifact-only mailbox
  closeout is acceptable if no repo change is needed.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1/`.
- Mailbox report to `intern_nemotron_lead` with:
  - branch/head/PR or artifact-only status;
  - exact artifact source paths and reviewer-readable target paths;
  - commands/env/host used to copy or inventory artifacts;
  - checkpoint and HF export file counts, sizes, and hashes, or a clear reason
    if only partial manifests are possible;
  - whether worker_5 can now review the artifact directly;
  - boundary confirmation;
  - recommendation for #329: ready for task256 re-review, docs-only closeout,
    or blocked.

## Acceptance Criteria

- PASS: reviewer-accessible task255 checkpoint/export evidence exists and is
  sufficient for worker_5 to re-review artifact integrity.
- BLOCKED: access/copy/inventory cannot be provided, with exact commands,
  errors, resource constraints, and remediation path.
- This task does not change the global gate: Qwen AIME remains `NO-GO/HOLD`
  unless task257/task243 proves FT score is not below the accepted base. The
  current observed FT result is below base and cannot be promoted.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task255, task256, task257
- Related PR: #329
- First gate: reviewer-readable artifact evidence or precise blocker.
