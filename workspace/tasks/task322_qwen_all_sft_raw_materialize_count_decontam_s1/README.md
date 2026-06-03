# task322_qwen_all_sft_raw_materialize_count_decontam_s1 - Raw all-SFT materialize/count/decontam

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_2,SESSION=4 -->

## Background

Task319 accepted the broader `stage1_sft/data_blend_raw` sources as feasible
candidates, but not packing-ready. It found 12 raw HF source entries with
task308 repo revisions and HF file sha256 coverage, while exact local row
counts, row-level manifests, decontam results, split exposure proof, Qwen
chat-template packing proof, and supervised-token counts remain missing.

## Goal

Materialize the 12 task319 raw source candidates into a task-owned output root
or fail closed with exact source-specific blockers, then count rows, checksum
materialized files/rows, and run heldout/decontam checks. This is a prerequisite
for any later all-SFT packed-data repair contract.

## Scope

- Use task319 source matrix as the source-of-truth candidate list.
- Materialize sources only into a task-owned output root under
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/`.
- For each source, report dataset id/path, subset/file, revision, selected HF
  file path or split, local materialized path, bytes, exact row count, parse
  status, file sha256, row-manifest sha256, and inclusion/blocker status.
- Run fail-closed heldout/decontam checks against AIME2025/HMMT/MATH heldouts
  from task246 and include the task314/task311 MMLU-Pro row manifest/input
  hashes as heldout references. Report exact prompt-hash, normalized text, and
  n-gram overlap counts.
- Report proof that AIME2025 prompts/labels are not train rows and task255 is
  not reused.
- If a source requires network, credentials, trust flags, or too-large
  downloads, record the exact blocker and stop or exclude that source. Do not
  mutate shared roots.

## Boundaries

- No final packing, training, optimizer steps, benchmark eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
  main push, merge, or self-merge.
- No product-code edits. Lightweight helper scripts may be task-owned only if
  kept under this task directory or output root.
- Do not delete or overwrite files under `/mnt/cephfs/data/processing/lei.song`
  or any shared dataset/cache root.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task322_qwen_all_sft_raw_materialize_count_decontam_s1`.
- Report:
  `workspace/tasks/task322_qwen_all_sft_raw_materialize_count_decontam_s1/raw_materialize_count_decontam_report.md`.
- Task-owned output root with source manifests, row manifests, decontam outputs,
  command logs, and checksum manifests.
- Mailbox report with branch/head/PR or blocker, commands/env, artifact root,
  source-by-source pass/block matrix, row/checksum/decontam results, and exact
  recommendation for or against a later packed-data contract task.

## Acceptance Criteria

- `PASS_MATERIALIZE_DECONTAM_READY_FOR_PACK_CONTRACT`: every included source has
  exact row counts, local checksums, row manifests, decontam pass, split
  exposure proof, and no forbidden train data; blocked sources are explicitly
  excluded.
- `PARTIAL_PASS_WITH_EXCLUSIONS`: a safe subset is fully proven and remaining
  sources are blocked/excluded with exact reasons.
- `BLOCK`: materialization/decontam cannot safely proceed without forbidden
  data use, shared mutation, missing credentials, unbounded downloads, or
  unknown counts/checksums.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task319, task308, task309, task246, task314/task320
- Gate state: no final packing or training authorized.
