# task289_qwen_aime_v11_post_smoke_runbook_provenance_s1 - Post-smoke runbook provenance

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=4 -->

## Background

The V11 Qwen AIME pipeline has advanced past packed data, no-training
preflight, and bounded Qwen3-4B smoke. PR #350/task285 merged bounded smoke
evidence at merge commit `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`. PR
#352/task287 is merged at `ca1ab63588651351b3e669450659abd2ad2c73e8` from
head `52834d74c79ab98b5e125434160843752c34d47a` with official BLOCK evidence:
no retained completions and no accepted canary pass.

Runbook/provenance must reflect this state without implying AIME eval,
promotion, export, endpoint, 30B, or 8-GPU clearance.

## Goal

Update or report runbook/provenance state for the post-smoke V11 pipeline:
#350/task285 merged evidence, task286 approval, #352/task287 merged blocker
evidence, task288/#353-task290 blocker approvals, task291 route-unblock gate,
and the remaining corrected AIME2025 FT-vs-base requirement.

## Scope

- Start from current `origin/main` after #350 merge commit
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`.
- Reconcile these facts:
  - #344/task276 packed_qwen evidence merged, with sparse valid/test risk;
  - #349/task283 no-training preflight merged;
  - #350/task285 bounded smoke evidence merged;
  - task286 approved #350 as smoke evidence only;
  - #352/task287 is merged with BLOCK/no retained completions;
  - task288 approved task287 blocker closeout as evidence only;
  - #353/task290 is merged at
    `a372dcd7cd866dc02951f4f1c86eaf05a4c885b4` from exact head
    `daad63efe77f19b8d56c62eca9d9f9331efd6e22`;
  - task291 is assigned to worker_2 for bounded no-export/no-endpoint route
    unblock and remains pending official report/PR.
- Preserve accepted base comparator for future AIME comparison:
  Qwen3-4B base score `11/30 = 0.36666666666666664` under the corrected
  AIME2025 harness.
- Make clear that same-harness FT-vs-base AIME comparison remains blocked until
  task291 publishes an accepted route result or exact blocker and lead
  explicitly releases the AIME task.

## Boundaries

- Do not run training, canary, AIME/task243 eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, merge, push main, 30B, or
  8-GPU.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task289_qwen_aime_v11_post_smoke_runbook_provenance_s1`.
- PR to `main` if runbook/docs/status files change.
- Mailbox report with:
  - branch/head/PR or exact blocker;
  - changed files and summary;
  - provenance matrix of task276/task283/task285/task286/task287/task288/task290/task291;
  - artifact paths and metrics carried forward;
  - explicit no-clearance statement for AIME/task243, export, endpoint,
    promotion, 30B, and 8-GPU.

## Acceptance Criteria

- PASS: runbook/provenance accurately captures current V11 gate state and does
  not overstate clearance.
- REQUEST-CHANGES: stale head/PR/artifact metadata or ambiguous next gate.
- BLOCK: required provenance cannot be found from repo or lead docs.

## Session 1 Result

- Created `post_smoke_runbook_provenance_report.md`.
- Refreshed the shared task266 runbook matrix against current `origin/main`
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`.
- Recorded #349/task283 merged no-training preflight PASS, #350/task285 merged
  bounded Qwen3-4B smoke evidence, task286 smoke-only approval, task287 active
  non-AIME canary gate, and task288 independent HOLD gate.
- Preserved accepted Qwen3-4B base comparator `11/30 =
  0.36666666666666664` and kept corrected AIME2025 same-harness FT-vs-base
  comparison blocked until the task287 blocker is resolved and lead explicitly
  releases it.
- No training, canary, AIME/task243 eval, export, endpoint, promotion, task255
  reuse, AIME2025 train data, shared deletion, merge, main push, 30B, or 8-GPU
  action was performed.

## Session 2 Result

- Refreshed the task289 provenance report and carried task266 runbook matrix
  after lead REQUEST-CHANGES for #351.
- Recorded PR #352/task287 as OPEN/base main/CLEAN at exact head
  `52834d74c79ab98b5e125434160843752c34d47a` with disposition `BLOCK`, no
  retained completions, and no accepted canary pass.
- Recorded task288 branch
  `e62fad1da9a4279869e939a34604c4f1ce13827b` and task290 branch
  `dab9a8bb87315bed529af0f00e3c843b1f910d0e` as pending independent review
  inputs.
- Kept corrected AIME2025 same-harness FT-vs-base comparison, export, endpoint,
  promotion, 30B, and 8-GPU blocked.
- No runtime, training, canary, AIME/task243 eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, merge, main push, 30B, or
  8-GPU action was performed.

## Session 4 Result

- Refreshed PR #351 after lead request-changes comment `4600040776`.
- Recorded #353/task290 as MERGED at `2026-06-02T07:52:08Z` with merge commit
  `a372dcd7cd866dc02951f4f1c86eaf05a4c885b4` from exact head
  `daad63efe77f19b8d56c62eca9d9f9331efd6e22`.
- Recorded task291 lead-observed head
  `4dffb40caea801503b8c39241f9afbe321887760` with read-only observed
  no-export canary blockers/no retained completions, and current fetched task291
  branch `ec099d2e523064640c676e2f682e54f44ccd6098`.
- Explicitly held task291 pending worker_2's official task291 report/PR and
  lead processing; local task291 output probes are not treated as accepted
  closeout evidence by this runbook.
- Kept AIME/task243 eval, export, endpoint, promotion, task255 reuse,
  AIME2025 train data, shared deletion, 30B, and 8-GPU blocked.
- No runtime, training, canary, AIME/task243 eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, merge, main push, 30B, or
  8-GPU action was performed.

## Session 3 Result

- Refreshed PR #351 after lead HOLD for current task287/task290/task291 state.
- Recorded #352/task287 as MERGED at `2026-06-02T07:39:18Z` with merge commit
  `ca1ab63588651351b3e669450659abd2ad2c73e8` from head
  `52834d74c79ab98b5e125434160843752c34d47a`; disposition remains `BLOCK`,
  with no retained completions and no accepted canary pass.
- Recorded task288 branch
  `a4afc814554f92039d886548a8979cf847e6265e` as blocker-closeout approval
  evidence only.
- Recorded #353/task290 OPEN/base main/CLEAN/MERGEABLE at exact head
  `daad63efe77f19b8d56c62eca9d9f9331efd6e22` with lead approval comment
  `4599915303` and decision `APPROVE_BLOCKER_CLOSEOUT`.
- Recorded task291 branch
  `63c5715cefc7a19d7cfcc46fbfa9bcd767a113b0` as the active bounded
  no-export/no-endpoint route-unblock assignment.
- Kept AIME/task243 eval, export, endpoint, promotion, 30B, and 8-GPU blocked.
- No runtime, training, canary, AIME/task243 eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, merge, main push, 30B, or
  8-GPU action was performed.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related tasks: task276, task277, task283, task284, task285, task286, task287,
  task288, task290, task291
- Related PRs: #344, #349, #350, #351, #352, #353
