# task250_qwen_aime_v10_live_runbook_artifacts_s1 - Live runbook artifacts

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_5,SESSION=14 -->

## Background

task245 documented the static runbook and expected artifact paths. After PR
#317 through #321 landed, the next required lead evidence is a live artifact
registry for the first Qwen3-4B V10 go/no-go attempt.

## Goal

Maintain a live artifact/runbook report that tracks the real task246 corpus,
task247 base score, task248 candidate artifacts, task249 review disposition,
and final task243 base-vs-FT comparison status.

## Scope

- Read-only verification and runbook tracking unless lead explicitly requests a
  docs update.
- Verify artifact existence, path ownership, checksums where practical,
  commands, logs, and no-delete boundaries.
- Keep a single current go/no-go table with exact blocker status.
- Record the first measurable gate rule:
  `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`.

## Boundaries

- Do not train, run live eval, start endpoints, or launch 30B/8-GPU scale.
- Do not merge or push `main`.
- Do not delete files under `/mnt/cephfs/data/processing/lei.song`.
- Do not treat worker-reported artifacts as accepted until path/protocol
  evidence is inspected.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task250_qwen_aime_v10_live_runbook_artifacts_s1`.
- PR to `main` with runbook artifact if appropriate.
- Task report in this directory named `live_runbook_artifact_report.md`.
- Mailbox report with artifact table, current go/no-go, exact blockers, and any
  resource request needed from coordinator.

## Acceptance Criteria

- The runbook has concrete paths for real corpus/input, base output, candidate
  checkpoint/export, FT output, and comparison output, or exact blockers for
  each missing item.
- It verifies no shared processing files were deleted.
- It refuses promotion and 30B scale until task249 review and task243
  same-harness comparison pass.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Depends on: task245, task246, task247, task248, task249
- First gate: provide the lead's canonical live artifact table for the next
  coordinator report.
