# task245_qwen_aime_v10_artifact_runbook_verify_s1 - Artifact, repro, and runbook verification

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Background

The supervisor requires concrete metrics, artifact paths, and resource blockers. Project rules require remote debug on `NemTron`, code synced to `/root`, CPU-local downloads before copy to NemTron, and no deletion of existing files under `/mnt/cephfs/data/processing/lei.song`.

## Goal

Verify that the V10 pilot can be reproduced safely from documented artifacts and that the first go/no-go gate is measurable before any 30B/8-GPU spend.

## Scope

- Own artifact and runbook verification for the Qwen3-4B pilot and corrected AIME25 base-vs-FT gate.
- Review generated scripts from worker_2 and eval protocol from worker_3.
- Confirm artifact paths for base model, prepared data, packed shards, train manifest, FT checkpoint/export, eval outputs, and logs.
- Verify runbook steps for local CPU prep, sync to `/root` on NemTron, remote launch, endpoint serving, corrected eval, result collection, and cleanup limits.
- Act as the first independent tester/repro owner when lead assigns a concrete PR or pilot artifact to verify.

## Boundaries

- Do not modify product code unless lead explicitly changes this task.
- Do not merge PRs or push `main`.
- Do not delete existing shared files.
- Do not start 30B/8-GPU scale. Any 30B plan must be reported as held until the 4B non-regression gate is satisfied.

## Expected Output

- Worker branch: `intern_nemotron_worker_5/task245_qwen_aime_v10_artifact_runbook_verify_s1`.
- PR is expected for persistent runbook docs if new docs are added; otherwise report through mailbox with artifact paths and verification notes.
- A runbook verification report in this task directory with pass/block status for each artifact and command.
- Mailbox report with verified paths, missing artifacts, resource blockers, and first go/no-go evidence readiness.

## Session 1 Report

- Runbook verification report:
  `workspace/tasks/task245_qwen_aime_v10_artifact_runbook_verify_s1/runbook_verification_report.md`.
- Gate state: blocked for first Qwen3-4B AIME go/no-go until V10 data/planner
  artifacts, corrected base-score artifacts, candidate FT checkpoint/export,
  and same-harness comparison outputs exist.

## Acceptance Criteria

- Runbook identifies exact base Qwen3-4B checkpoint path and candidate FT artifact path.
- Same-harness base-vs-FT AIME25 smoke can be reproduced from documented commands, or blockers are exact and actionable.
- No step deletes existing shared data.
- First measurable gate is documented: pilot FT AIME25 corrected smoke score must be at least base score under identical settings, with parsed/finish diagnostics included.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Verification inputs: task241 data artifacts, task242 planner/scripts, task243 eval gate, task244 independent review
