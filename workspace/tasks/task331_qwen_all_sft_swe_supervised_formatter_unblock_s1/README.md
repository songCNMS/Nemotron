# task331_qwen_all_sft_swe_supervised_formatter_unblock_s1 - SWE supervised-token formatter unblock

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=83 -->

## Background

task329/#392 and task330/#393 are merged as partial evidence closeout. The
current expanded all-SFT data path remains blocked because `task327-swe`
packed 51,029 rows under the Qwen3-30B path but produced
`supervised_tokens=0`. This source cannot count as supervised SFT until a
lead-approved source/config formatter remediation proves nonzero supervised
tokens with tokenizer-native Qwen packing.

## Goal

Produce a no-training, task-owned proof that the accepted task327 `swe` raw
source can be formatted or configured for Qwen3-30B SFT packing with nonzero
supervised tokens, or fail closed with an exact blocker.

## Required Inputs

- Current `origin/main`: `410c2247fc5e09e6ad831bdee1628830b97fbd89`.
- task327/#390 large-source evidence root:
  `/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/run_20260603T211508Z`.
- task329/#392 raw-pass packing evidence root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.
- Qwen3-30B model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Merged task330/#393 review report:
  `workspace/tasks/task330_qwen_all_sft_task329_independent_review_s1/task329_independent_review_report.md`.

## Scope

- Branch:
  `intern_nemotron_worker_2/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1`.
- Build a task-owned output root under
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/`.
- Inspect the task327 `swe` source schema, task329 packing receipt, and Qwen
  data-prep config path to identify why supervised labels are masked out.
- Create only task-local helper/config/proof artifacts unless a minimal
  product-code change is genuinely required; if product-code change is needed,
  isolate it and explain why.
- Produce source provenance, row counts, source checksums, row-manifest
  checksums, filtered-row counts, supervised-token counts, shard counts, and
  packed shard checksums.
- Prove no AIME2025 prompt/label train rows, no task255 reuse, and no inclusion
  of task327 decontam-hit sources.
- Run Qwen packed-data contract validation for the produced SWE candidate root,
  or explain the exact fail-closed blocker.

## Expected Output

- Report:
  `workspace/tasks/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/swe_supervised_formatter_unblock_report.md`
- Worker branch and PR to `main` for docs/status plus any scoped helper/config
  changes.
- Mailbox closeout with:
  - branch/head/PR,
  - commands and environment,
  - output root and checksums,
  - pass/fail disposition,
  - exact recommendation for whether SWE can enter a later combined packed
    contract.

## Boundaries

- No training, optimizer steps, benchmark eval, export, endpoint, promotion,
  merge, self-merge, or main push.
- No task255 reuse.
- No AIME2025 prompts or labels as training rows.
- No shared deletion or mutation, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not modify task329 artifacts in place; write task331-owned outputs.

## Acceptance Criteria

- `PASS_SWE_SUPERVISED_UNBLOCK`: Qwen3-30B packing for task327 `swe` produces
  nonzero supervised tokens with checksums, Qwen contract pass, decontam proof,
  and clear formatter/config provenance.
- `REQUEST_CHANGES`: evidence is incomplete, inconsistent, or missing required
  checks.
- `BLOCK_SWE_UNSUPERVISED`: SWE cannot safely be made supervised under current
  data/config without a larger lead-approved source or recipe change.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Gate state: task310 training/eval/export/endpoint/promotion remain HOLD.
