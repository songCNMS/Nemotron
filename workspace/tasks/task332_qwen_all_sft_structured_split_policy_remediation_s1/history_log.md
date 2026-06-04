# task332_qwen_all_sft_structured_split_policy_remediation_s1 - history log

<!-- METADATA:SESSION=83 -->

## Session 83 - 2026-06-04 UTC - Assigned by lead

- Created after merged task329/#392 and task330/#393 accepted raw-pass evidence
  only as `APPROVE_DOCS_CLOSEOUT_HOLD_TRAINING`.
- Scope targets the two non-SWE blockers: 6 structured validation-filtered rows
  and sparse valid/test exposure.
- This task is no-training remediation/planning evidence only and does not
  authorize task310 training, benchmark eval, export, endpoint, or promotion.

## Session 1 - 2026-06-04 UTC - Accepted by worker_4

- Created branch
  `intern_nemotron_worker_4/task332_qwen_all_sft_structured_split_policy_remediation_s1`
  from required `origin/main`
  `410c2247fc5e09e6ad831bdee1628830b97fbd89`.
- Imported task332 docs from lead branch commit
  `bbbf19df7ea7dad3fc644588f1e84240c464febe`.
- Scope remains no-training remediation evidence only: exact structured
  filtered-row disposition, deterministic split policy or fail-closed blocker,
  task-owned checksums, decontam/no-AIME proof, and dependency on task331.
- Boundaries: no training, eval, export, endpoint, promotion, task255 reuse,
  shared deletion, merge, self-merge, direct main push, or mutation of task329
  artifacts.

## Session 1 - 2026-06-04 UTC - Remediation evidence produced

- Added task-local helper
  `build_task332_structured_split_policy_evidence.py`.
- Wrote task-owned output root
  `/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z`.
- Identified exactly six `instruction-following-structured` invalid rows via
  `nemotron.data_prep.core.chat_template.validate_conversation`; the row
  hashes and shard indices match task329 receipt validation-error counts.
- Recorded fail-closed exclusion policy for those exact row hashes unless a
  later source-remediation task repairs missing tool context and revalidates.
- Proposed deterministic source-local split policy
  `task332_per_source_shard_holdout_v1`: row remainder `14` valid,
  remainder `15` test, all other remainders train for each included raw-pass
  source.
- Confirmed task331 is still acceptance/status/docs only at
  `63b4b992d534bd16120f31345d57d105890d8d55` with no PR visible, so final
  disposition is `PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING`.
- Verified `python -m py_compile` for the helper and
  `sha256sum -c manifests/artifact_checksums.sha256` for task332 outputs.
- Boundaries maintained: no training, eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train rows, shared deletion, task329 artifact
  mutation, merge, self-merge, or main push.
