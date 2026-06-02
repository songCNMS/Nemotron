# task286_qwen_aime_v11_task285_smoke_gate_review_s1 - task285 smoke gate review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=74 -->

## Background

task285 is the first permitted bounded Qwen3-4B nonzero-LR SFT smoke attempt
after the task283/task284 no-training preflight gate. It may produce either a
small task-owned smoke checkpoint/artifact or an exact blocker.

## Goal

Independently review task285 exact branch/head/artifacts and return
approve/request-changes/block for whether any produced smoke artifact is
eligible for the next non-AIME canary/completion-retention gate.

## Scope

- Wait for task285 official worker report, PR, branch head, and artifact root.
- Review only exact task285 evidence. If the task285 PR head changes after
  review, require refreshed evidence before approval.
- Verify Qwen3-4B base-load/import proof, packed-data references, command/config
  bounds, first-step nonzero LR, finite loss, checkpoint/artifact paths,
  checksums, and fail-closed blockers.
- Verify task276 valid/test sparsity is not treated as quality evidence.
- Verify AIME2025 prompts/labels remain held out and task255 is not reused.

## Boundaries

- Do not edit files, train, run live canary, run AIME/task243 eval, export,
  endpoint, promote, reuse task255, use AIME2025 train data, delete shared
  files, merge, push main, or use 30B/8-GPU.

## Expected Output

- Mailbox report with exact task285 head/artifact reviewed, read-only commands,
  pass/fail for every acceptance criterion, and approve/request-changes/block
  decision.
- If task285 blocks, identify whether the blocker is dependency/runtime,
  base-load/import, data-contract, zero-LR, random-init signal, resource, or
  artifact evidence.

## Acceptance Criteria

- APPROVE: task285 evidence proves a bounded Qwen3-4B smoke from verified base
  load/import with nonzero first-step LR, finite loss, reviewable task-owned
  checkpoint/artifacts, and no boundary violation.
- REQUEST-CHANGES: task285 evidence is incomplete, stale, ambiguous, or not
  tied to exact artifacts.
- BLOCK: the smoke is invalid, boundary-violating, random-init/zero-LR, missing
  base-load proof, or blocked by runtime/resource/dependency.

This review can only release a later non-AIME canary/completion-retention task.
It does not authorize corrected AIME2025/task243 eval, export, endpoint,
promotion, 30B, or 8-GPU scale.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related task: task285
- Current gate: independent review of bounded smoke evidence only.
