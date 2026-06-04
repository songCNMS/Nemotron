# task334_qwen_all_sft_task333_independent_review_s1 - Review task333 combined packed contract

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

PR #396/task333 produced a no-training combined all-SFT packed-contract
candidate. It must receive independent review before any task310 training,
nonzero-LR smoke, canary, benchmark eval, export, endpoint, promotion, or 30B
release can be considered.

Review target:

- PR: #396 `https://github.com/songCNMS/Nemotron/pull/396`
- Exact head: `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`
- Base: `main`
- Current observed PR state: `OPEN`, non-draft, `CLEAN`/`MERGEABLE`
- Artifact root:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`
- Packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`
- Report:
  `workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/combined_packed_contract_report.md`

## Goal

Perform an independent read-only gate review of #396/task333 and return one of:

- `APPROVE_COMBINED_PACKED_CONTRACT_FOR_DOCS_CLOSEOUT`: evidence supports
  accepting #396 as a no-training packed-contract candidate and moving to a
  separate lead-gated training preflight task.
- `REQUEST_CHANGES`: report, helper, PR scope, artifact checks, decontam,
  split policy, source metrics, or residuals are incomplete or inconsistent.
- `BLOCK_COMBINED_PACKED_CONTRACT`: the candidate is unsafe or cannot be used
  under the current no-AIME/task255/no-shared-mutation constraints.

Approval does not release task310 or any training/eval. It only allows lead to
close #396 and decide the next gate.

## Required Review Checks

Review exact PR head `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`.

Check all of the following:

- PR metadata: base `main`, exact head, non-draft, clean/mergeable, no material
  head drift.
- Diff scope: worker_1 status plus task333 README/history/task_knowledge,
  task-local helper, and task333 report only.
- `git diff --check origin/main...origin/intern_nemotron_worker_1/task333_qwen_all_sft_combined_packed_contract_s1`.
- Helper compile from the PR head.
- Report consistency with artifact root `run_20260604T074500Z`.
- Manifest disposition:
  `PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW`.
- Metrics: 96 shards, 89,325 rows, 342,875,996 input tokens,
  38,245,535 supervised tokens; split train 84 shards/78,168 rows, valid 6
  shards/5,561 rows, test 6 shards/5,596 rows.
- Source inclusion/exclusion:
  task299 seed, task329 `agentic-interactive`,
  task329 `instruction-following-structured`, task331 SWE no-tools-header
  included; task255 excluded; nine task327 `BLOCKED_DECONTAM_HIT` sources
  excluded; task329 zero-supervised SWE excluded/replaced; six structured rows
  fail-closed excluded.
- task332 split policy is represented clearly: source-local shard 14 valid,
  shard 15 test, all others train. Note any evidence gap if task333 uses
  already-packed shard links rather than fresh raw row-level repacking.
- Qwen3-30B packed/training contract validation rc/log and marker:
  `TASK333_QWEN30B_PACKED_CONTRACT=PASS`.
- `sha256sum -c manifests/artifact_checksums.sha256` and
  `sha256sum -c manifests/packed_shard_checksums.sha256` from the task333 run
  root.
- Broken symlink check for the packed split root.
- Decontam/no-AIME/task255 proof: AIME2025 prompt/label train rows 0,
  task255 not used, task329/task331 zero-hit fields carried, task299 seed
  accepted prompt-hash/final-answer n-gram proof carried.
- Residuals: no fresh task333 decontam scan; task299 seed lacks
  normalized-prompt field; hard-math task299 source has valid/test shard files
  with zero rows; SWE rows still truncate to 4096 but have nonzero supervised
  tokens.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task334_qwen_all_sft_task333_independent_review_s1`.
- Report:
  `workspace/tasks/task334_qwen_all_sft_task333_independent_review_s1/task333_independent_review_report.md`.
- Mailbox closeout with branch/head/PR, commands run, artifact paths,
  pass/fail findings, residuals, and exact decision for #396.

## Boundaries

- Read-only review of #396 and task333 artifacts.
- Do not modify task333 artifacts or worker_1 branch.
- No training, optimizer steps, nonzero-LR smoke, benchmark eval, export,
  endpoint, promotion, task310 release, 30B release, task255 reuse, AIME2025
  train rows, shared deletion/mutation, main push, merge, or self-merge.
- Do not run implementation tests beyond focused read-only compile/checksum/
  manifest/Qwen contract verification needed for the review.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Base: current `origin/main` `ad0c5a7d758d44370695b94c83385591f100c714`
- Lead branch docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
- Gate state: #396 and task310 remain HOLD pending this review.

## Worker_4 Review Result

- Report:
  `workspace/tasks/task334_qwen_all_sft_task333_independent_review_s1/task333_independent_review_report.md`
- Reviewed #396 exact head:
  `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`
- Disposition: `REQUEST_CHANGES_REPORT_ARTIFACT_MISMATCH`
- Summary: assigned `run_20260604T074500Z` artifacts passed checksum,
  Qwen30B contract, split parity, symlink, decontam/no-task255, and boundary
  checks, but the committed #396 report's Source Provenance table contains
  three task299 row-manifest SHA256 values from a different local
  `run_20260604T083000Z` root while naming the assigned `074500Z` root.
