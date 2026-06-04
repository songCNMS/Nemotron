# task328_qwen_all_sft_post_task327_packed_contract_s1 - Post-task327 all-SFT packed contract

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_2,SESSION=80 -->

## Background

Task309/#372 merged as a packed-contract blocker before task322/task327 large
raw-source evidence existed. Task308/#374 is merged as the current all-SFT
inventory audit. Task322/#388 and task327/#390 now provide source-level raw
materialize/count/checksum/decontam evidence:

- task322/#388: partial raw evidence with two included/pass bounded sources and
  ten large-source exclusions.
- task327/#390 current head `49c5d748c8c9ecc95d21c69a1bd16af0118cba3d`:
  10/10 large excluded sources materialized; only `swe` is `INCLUDED_PASS`;
  the other nine are `BLOCKED_DECONTAM_HIT`.

The coordinator objective remains a full all-eligible-SFT data -> training ->
evaluation attempt, but training is still blocked until a fresh accepted
packed-data contract exists.

## Goal

Produce a successor all-eligible-SFT `packed_qwen` contract for
Qwen3-30B-A3B training from current accepted evidence, or fail closed with the
exact blocker. This task is the packing-contract step only; it does not
authorize training, benchmark eval, export, endpoint, or promotion.

## Required Inputs

- Current `origin/main`: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`.
- Product-code baseline from the all-SFT request: `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- task308/#374 merged inventory audit.
- task309/#372 merged blocker report.
- task322/#388 current evidence and artifacts for the two bounded
  `INCLUDED_PASS` sources.
- task327/#390 current evidence and artifacts for the large-source pass/block
  matrix, especially `swe` as the only task327 large-source `INCLUDED_PASS`.
- task324/#386 MMLU-aware blend design as design guidance only.
- task246 heldout/decontam corpus, task311/task314 MMLU-Pro heldout references,
  and any existing accepted V11/task276/task299 seed artifacts that remain
  eligible under current decontam and split rules.

## Scope

- Branch:
  `intern_nemotron_worker_2/task328_qwen_all_sft_post_task327_packed_contract_s1`.
- Build an explicit source-inclusion matrix before packing:
  - include only sources with accepted pass evidence;
  - carry task322 bounded pass sources only if row/checksum/decontam/split
    evidence is sufficient for packing;
  - carry task327 `swe` only if its split exposure and Qwen chat-template
    conversion are proven safe;
  - include V11/task276/task299 seed sources only if current provenance,
    decontam, split, tokenizer, and task255/AIME2025 exclusions are still
    proven;
  - exclude all nine task327 `BLOCKED_DECONTAM_HIT` sources unless a separate
    lead-approved false-positive/adjudication manifest exists.
- Produce a task-owned output root with either:
  - `packed_qwen` artifacts for
    `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`; or
  - an exact fail-closed blocker report.
- For any produced packed root, report split manifest, row counts, source
  counts, input-token counts, supervised-token counts, shard counts,
  intended-vs-exposed multiset parity, checksums, decontam proof, and Qwen
  chat-template/tokenizer proof.
- If open PR evidence (#388/#390) is consumed before merge, pin the exact PR
  head, lead gate comment, artifact root, and artifact sha; state whether the
  unmerged docs status is a blocker for final acceptance.
- If sparse valid/test or train-only assumptions remain, state exact impact and
  whether task310 must remain blocked.

## Boundaries

- No optimizer steps, full training, benchmark eval, export, endpoint,
  promotion, or 30B runtime launch.
- No task255 reuse.
- No AIME2025 prompts or labels as train rows.
- No heldout/eval/decontam rows as train rows.
- No shared deletion or mutation, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- No product-code edits unless the task returns a blocker that explicitly
  requires later lead-approved implementation work.
- Do not silently downgrade to Qwen3-4B or another model family.
- Do not merge, self-merge, or push main.

## Expected Output

- Report:
  `workspace/tasks/task328_qwen_all_sft_post_task327_packed_contract_s1/post_task327_packed_contract_report.md`.
- Task-owned output root under
  `/work-agents/intern_nemotron_worker_2/outputs/task328_qwen_all_sft_post_task327_packed_contract_s1/`
  containing packed artifacts or blocker evidence, source inclusion matrix,
  decontam proof, split/parity reports, commands/env, logs, and checksums.
- PR to `main` for task docs/status/report.
- Mailbox report with branch/head/PR, artifact paths, commands/env, exact
  source matrix, counts, checksums, decontam proof, Qwen tokenizer/chat-template
  proof, and task310 go/no-go recommendation.

## Acceptance Criteria

- `PASS_POST_TASK327_PACKED_CONTRACT`: packed root is complete, checksummed,
  decontaminated, Qwen3-30B-compatible, excludes all blocked/heldout/task255/
  AIME2025 train rows, and is ready for an independent review before task310.
- `PARTIAL_PASS_WITH_EXACT_BLOCKERS`: a safe subset is proven but final packed
  contract cannot be accepted because of exact source/split/decontam/tokenizer/
  merge-state blockers.
- `BLOCK_PACKED_CONTRACT`: packing cannot proceed safely without violating
  source eligibility, decontam, AIME2025/task255, split exposure, tokenizer, or
  resource boundaries.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Upstream evidence: task308/#374, task309/#372, task322/#388, task327/#390,
  task324/#386, task246, task311, task314, task276/task299 as applicable
- Downstream tasks: independent packed-contract review, task310 training,
  task311 benchmark eval
- Gate state: task310 and all eval/export/endpoint/promotion remain HOLD.

## Worker_2 result

See `post_task327_packed_contract_report.md`.

Disposition is `PARTIAL_PASS_WITH_EXACT_BLOCKERS`. Task328 did not produce a
new packed root: the prior constrained task299 packed seed remains the only
safe carry-forward packed evidence, while the task322/task327 raw pass sources
are excluded before packing due missing split exposure/parity and Qwen3-30B
supervised-token packing proof. All nine task327 `BLOCKED_DECONTAM_HIT` sources
remain excluded fail-closed.
