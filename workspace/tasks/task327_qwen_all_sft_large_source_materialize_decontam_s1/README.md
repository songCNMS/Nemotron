# task327_qwen_all_sft_large_source_materialize_decontam_s1 - Large-source raw materialize/decontam

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Background

Task322/#388 resolved all 12 task319 raw all-SFT candidates to exact HF files
and accepted two bounded sources as `INCLUDED_PASS`, but it fail-closed excluded
10 selected files because each was larger than the task322 1GB materialization
threshold. Those 10 files represent 242,773,079,314 selected bytes and block a
full all-eligible-SFT packed-data contract.

This task is the successor raw-data task for those 10 excluded files only.

## Goal

Materialize, count, checksum, row-manifest, and decontam-check the 10 task322
`EXCLUDED_SIZE_GT_1GB` sources in a task-owned output root, or fail closed with
exact source-specific resource/runtime blockers. This is still no-training and
no-packing evidence only.

## Required Sources

Use task322/#388 as source of truth for selected files, revisions, sizes, and
task308 sha references. Process these 10 excluded entries:

| Source | Selected file | Bytes |
| --- | --- | ---: |
| `instruction-following-chat` | `data/chat_if.jsonl` | 7,000,317,929 |
| `competitive-cpp-00` | `data/competitive_coding_cpp.part_00.jsonl` | 25,608,786,180 |
| `competitive-cpp-01` | `data/competitive_coding_cpp.part_01.jsonl` | 25,921,457,397 |
| `competitive-python-00` | `data/competitive_coding_python.part_00.jsonl` | 44,531,003,881 |
| `competitive-python-01` | `data/competitive_coding_python.part_01.jsonl` | 44,260,933,400 |
| `swe` | `data/r2e_gym.jsonl` | 11,141,242,062 |
| `math-proofs-lean` | `data/lean.jsonl` | 29,525,155,225 |
| `agentic-tool-calling` | `data/tool_calling.jsonl` | 5,338,348,607 |
| `infinibyte-00` | `data/infinibyte.part_00.jsonl` | 24,706,580,148 |
| `infinibyte-01` | `data/infinibyte.part_01.jsonl` | 24,739,254,485 |

Carry forward task322 included-source evidence by reference only; do not redo it
unless needed for parity checks.

## Scope

- Use a task-owned output root under
  `/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/`.
- Download/cache locally in the worker CPU environment first. If a later copy to
  NemTron is needed, report the planned destination; do not copy until lead
  authorizes.
- For each source, report dataset id, repo revision, selected file, source
  sha256, local materialized path or exact blocker, bytes, row count, parse
  errors, row-manifest sha256, and inclusion/blocker status.
- Run heldout/decontam checks against task246 AIME2025/HMMT/MATH heldout
  corpus and prompt hashes. Carry task311/task314 MMLU-Pro heldout references
  as decontam inputs or documented references, not train rows.
- Report prompt-hash, normalized-prompt, and n-gram hit counts. Any hit must
  fail closed unless a false-positive manifest is produced for lead review.
- Report split exposure status for each source. Unknown train/valid/test
  semantics must be marked as a blocker or explicit train-only assumption for
  later lead review.
- Report disk/network/resource evidence before and after the run: `df -h`,
  output size, HF cache size, commands/env, process exit codes, and checksum
  verification.

## Boundaries

- No final packing, Qwen chat-template packing, tokenizer-heavy training
  preparation, optimizer steps, benchmark eval, export, endpoint, promotion,
  task255 reuse, AIME2025 prompt/label train rows, shared deletion/mutation,
  main push, merge, or self-merge.
- No product-code edits. Task-owned helper scripts may be recorded only under
  this task directory or the task-owned output root.
- Do not delete or overwrite any existing files under
  `/mnt/cephfs/data/processing/lei.song` or any shared cache/root. If shared
  scratch is unavoidable, stop and request lead approval with an exact path
  plan first.
- Do not silently reduce the source list. If a source cannot be processed,
  record `BLOCKED_<reason>` with command/log/resource evidence.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task327_qwen_all_sft_large_source_materialize_decontam_s1`.
- PR because workspace task docs/status should change.
- Report:
  `workspace/tasks/task327_qwen_all_sft_large_source_materialize_decontam_s1/large_source_materialize_decontam_report.md`.
- Task-owned output root with logs, source manifests, row manifests, decontam
  outputs, source-by-source matrix, resource evidence, and checksum manifests.
- Mailbox report with branch/head/PR or exact blocker, commands/env, artifact
  root, source matrix, row/checksum/decontam results, and recommendation for
  or against a later packed-data contract.

## Acceptance Criteria

- `PASS_LARGE_SOURCE_MATERIALIZE_DECONTAM`: all 10 large sources have exact
  local materialization or verified cache path, row counts, parse status,
  checksums, row manifests, decontam pass, split exposure status, and no
  forbidden train data.
- `PARTIAL_PASS_WITH_EXACT_BLOCKERS`: at least one large source is fully proven,
  and every unprocessed source has an exact resource/runtime/credential/blocker
  record.
- `BLOCK_RESOURCE_OR_SAFETY`: no large source can proceed safely, or proceeding
  would require forbidden AIME2025 train data, task255 reuse, shared mutation,
  unapproved shared scratch, or unbounded resource use.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task322/#388, task319, task308, task246, task311, task314
- Gate state: global all-SFT pack/train/eval remains HOLD.
