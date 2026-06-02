# task271_qwen_aime_v11_session40_bridge_proof_review_s1 - Session 40 Bridge proof review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=0 -->

## Background

Coordinator Session 40 installed `nemo-toolkit==2.7.3` on the NemTron user site
and reported a no-training Qwen3-4B Bridge import/fail-closed preflight pass.
This potentially clears the prior task270 runtime-route blocker for positive
Qwen3-4B Bridge import proof only.

Evidence root:

`/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`

Remote run:

`/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z`

## Goal

Independently review the Session 40 proof and report whether it satisfies the
task268/task270 no-training Bridge import/fail-closed preflight criteria.

## Scope

- Review local evidence logs, manifests, and checksums under the evidence root.
- Confirm the logs contain the required pass markers:
  - `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`;
  - `IMPORT_DONE`;
  - `BRIDGE_IMPORT_RC=0`;
  - `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`.
- Confirm reported checkpoint output exists in the manifest and is consistent
  with Qwen3-4B import proof.
- Note residual risks, including user-site NeMo install, `hydra` missing, and
  whether these matter for this import/preflight path.

## Boundaries

- No training, nonzero-LR smoke, export, endpoint, live AIME/task243 eval,
  promotion, task255 reuse, AIME2025 train data, 30B/8-GPU, merge, or main push.
- Do not delete or overwrite shared files.
- Read-only artifact inspection and checksum verification are acceptable.

## Expected Output

- Branch:
  `intern_nemotron_worker_4/task271_qwen_aime_v11_session40_bridge_proof_review_s1`.
- PR only if repo-visible docs/status change; mailbox-only review is acceptable.
- Mailbox report with approve/request-changes/block, commands run, artifact
  paths, checksum results, pass/fail markers, residual risks, and boundary
  confirmation.

## Acceptance Criteria

- APPROVE: Session 40 evidence proves no-training Qwen3-4B Bridge import and
  fail-closed preflight pass.
- REQUEST-CHANGES: evidence is promising but missing a required marker, path,
  checksum, or provenance detail that coordinator/lead can supply.
- BLOCK: evidence does not satisfy task268/task270 criteria or shows boundary
  violation.
