# task330_qwen_all_sft_task329_independent_review_s1 - Independent review of task329 raw-pass evidence

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

task329/#392 produced task-owned Qwen3-30B raw-pass packing evidence for three
allowed raw pass sources:

- task322 `instruction-following-structured`
- task322 `agentic-interactive`
- task327 `swe`

Lead gate comment `issuecomment-4619497556` places current #392 head
`d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf` on
`HOLD_FOR_INDEPENDENT_REVIEW`: Qwen contract and checksums pass, but the task329
report is `PARTIAL_PASS_WITH_EXACT_BLOCKERS` and does not release task310
training. Earlier gate comments `issuecomment-4619456297` and
`issuecomment-4619471068` are superseded by this current-head gate after
metadata-only PR head drift.

## Goal

Independently review #392 exact head
`d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf` and task329 artifacts. Decide
whether task329 can be accepted as a docs/evidence closeout, whether changes are
needed, and what exact remediation task is required before any expanded
all-SFT training contract can be considered.

## Required Inputs

- PR #392:
  `https://github.com/songCNMS/Nemotron/pull/392`
- Exact head:
  `d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf`
- Base:
  `origin/main` at `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`
- Packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/packed_qwen_raw_pass_materialized`
- Lead gate comment:
  `issuecomment-4619497556`

## Review Scope

- Review #392 diff scope and confirm it is docs/status/helper/report only.
- Verify `git diff --check` for #392.
- Verify task329 helper compiles or explain exact failure.
- Verify from the artifact root:
  - `sha256sum -c manifests/artifact_checksums.sha256`
  - `sha256sum -c manifests/packed_shard_checksums.sha256`
  - `logs/qwen30b_contract_validate.rc`
  - `logs/qwen30b_contract_validate.log`
  - `manifests/final_summary.json`
  - `manifests/qwen30b_packing_metrics.json`
  - `manifests/packing_receipt_metrics.json`
  - `manifests/intended_vs_exposed_parity.json`
  - `manifests/decontam_no_aime2025_train_proof.json`
  - `manifests/combination_decision.json`
- Independently inspect whether the three blockers are correctly stated:
  - `task327-swe` packed rows but `supervised_tokens=0`;
  - `instruction-following-structured` has 6 validation-filtered rows;
  - valid/test split exposure is sparse and agentic-only.
- Confirm all nine task327 `BLOCKED_DECONTAM_HIT` sources remain excluded.
- Confirm no AIME2025 prompts/labels, heldout rows, task255 artifacts, shared
  deletion, training, eval, export, endpoint, promotion, merge, or main push
  occurred.

## Expected Output

- Review report:
  `workspace/tasks/task330_qwen_all_sft_task329_independent_review_s1/task329_independent_review_report.md`
- Worker branch:
  `intern_nemotron_worker_4/task330_qwen_all_sft_task329_independent_review_s1`
- PR to `main` for review docs/status only, or branch-only report if lead
  explicitly accepts branch-only review.
- Mailbox closeout with:
  - branch/head/PR,
  - commands run,
  - artifact paths and checksum results,
  - approve/request-changes/block decision for #392,
  - exact remediation recommendation for the all-SFT pipeline.

## Boundaries

- Read-only review only.
- No product-code edits.
- No training, optimizer steps, nonzero-LR smoke, benchmark eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
  merge, self-merge, or main push.
- Do not modify worker_2 branch or task329 artifacts.

## Acceptance Criteria

- `APPROVE_DOCS_CLOSEOUT_HOLD_TRAINING`: #392 is accepted as accurate partial
  evidence/docs closeout, with training still blocked and exact remediation
  stated.
- `REQUEST_CHANGES`: #392 report or artifacts are materially incomplete,
  inconsistent, or need correction before docs closeout.
- `BLOCK`: evidence is unsafe, unverifiable, contaminated, out of scope, or
  otherwise cannot be accepted even as partial closeout.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Downstream: possible remediation task for SWE supervised-token mapping,
  structured filtered rows, split policy, and later combined contract review.
- Gate state: task310 training/eval/export/endpoint/promotion remain HOLD.
