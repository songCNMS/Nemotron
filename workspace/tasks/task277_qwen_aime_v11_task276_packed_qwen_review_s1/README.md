# task277_qwen_aime_v11_task276_packed_qwen_review_s1 - task276 packed Qwen review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=0 -->

## Background

task276 produced PR #344 with a fresh no-training V11 `packed_qwen` artifact
report. Lead observed #344 open/clean at exact head
`07efab4fa0d8367e96f54af3d2cdc70768d73595` and a task-owned run root under
worker_2 outputs. This needs independent review before any later no-training
config/import preflight task can be considered.

## Goal

Independently review task276/#344 exact head
`07efab4fa0d8367e96f54af3d2cdc70768d73595` and the referenced artifact paths to
decide whether the fresh V11 packed Qwen root is acceptable as
reviewed data/packing evidence only.

## Scope

- Review PR #344 at exact head
  `07efab4fa0d8367e96f54af3d2cdc70768d73595`; if the head changes, stop and
  report.
- Review the report:
  `workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/v11_rematerialized_packed_qwen_report.md`.
- Review task-owned run root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z`.
- Verify, using read-only checks, the required evidence:
  - task-owned output root and fresh `packed_qwen` root exist;
  - split manifest exists and checksums match;
  - train/valid/test row, input-token, supervised-token, shard, and source
    counts match the report;
  - intended-vs-exposed multiset parity passes for train/valid/test;
  - Qwen packed-data contract pass evidence is present and scoped to
    `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
  - Qwen chat metadata records tokenizer-native template with
    `enable_thinking=false` and `truncate_history_thinking=false`;
  - shard checksum list covers the actual parquet shards;
  - no AIME2025 prompt/label train leakage evidence is credible;
  - residual valid-split sparsity risk is clearly documented.

## Boundaries

- Do not edit code, docs, artifacts, branches, or PRs.
- Do not train, run nonzero-LR smoke, live canary, AIME/task243 eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
  main push, merge, or 30B/8-GPU.
- Do not approve promotion or pilot launch. This review is only for whether
  task276 can count as packed data/packing evidence.

## Expected Output

- Worker branch is optional only if status/task docs are committed:
  `intern_nemotron_worker_4/task277_qwen_aime_v11_task276_packed_qwen_review_s1`.
- Mailbox report to lead with:
  - exact PR/head reviewed;
  - commands/checks run and environment;
  - pass/fail for artifact existence, checksums, split counts, parity, Qwen
    contract, no-AIME train leakage, and boundary preservation;
  - approve/request-changes/block decision for #344 as data/packing evidence;
  - residual risks and unverified surfaces.

## Acceptance Criteria

- APPROVE: #344 exact head and task276 artifacts satisfy all required
  data/packing evidence for a future no-training config/import preflight review.
- REQUEST-CHANGES: evidence exists but is incomplete, stale, inconsistent, or
  missing required proof.
- BLOCK: artifact is unsafe, non-reviewable, leaks AIME2025 train data, fails
  Qwen contract/parity/checksum checks, or cannot be inspected.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related task: task276
- Related PR: #344
- First gate: independent approve/request-changes/block for task276 packed Qwen
  evidence only.
