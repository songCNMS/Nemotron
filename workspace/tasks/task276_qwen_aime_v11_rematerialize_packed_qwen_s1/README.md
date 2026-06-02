# task276_qwen_aime_v11_rematerialize_packed_qwen_s1 - V11 packed Qwen rematerialization

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Background

Coordinator Session 42 confirmed that task271-task275 closeouts are merged and
that the next allowed action is not training or evaluation. The data gate now
needs a fresh collision-safe `packed_qwen` train/valid root produced from the
task262 V11 blend plan under the merged task262 split materialization logic.

The old task253 packed root must not be used for training readiness because its
train split exposed 8 shards / 79 rows while task262 expected 15 shards / 113
rows. task274 preserved this as `BLOCK_PACKED_ARTIFACT_READY`.

## Goal

Produce a task-owned, no-training V11 `packed_qwen` train/valid root that is
collision-safe, reviewer-readable, and ready for independent review before any
later no-training config/import preflight task.

## Scope

- Start from current `origin/main` after #340/#341/#342/#343 merge, expected at
  `fd4f3b2b60cab7340a1a187e011af79ea1cb76ce`.
- Use the merged task262 split logic and Qwen chat contract code from `main`.
- Use task262 V11 blend plan evidence:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/v11_qwen_agentic_sft_blend_plan.json`
  with sha256 `2b3f0942eb04e077c5025c60be87355bf233b33085660a0b85a0b8b03b569e2a`.
- Preserve task262 decontamination and source evidence, including:
  - task262 manifest sha256
    `4c9874c9341b1e286533bd67eafa6a922567e905c9d3bb7bd78e8970eb777383`;
  - split audit sha256
    `b2009b2c509620c5dde2412ee4dedf4efb8995431ef4bec4d353ba14dc3787b3`;
  - final-answer n-gram scan sha256
    `feffa6c677b1bc86b5f2f9ad8a8c3506582844cdb5b6a25bd8741322a9298370`.
- Materialize train and valid splits under a task-owned output root without
  overwriting existing shared or historical artifacts.
- Run only local data-prep/packing and data-contract checks required to prove
  the artifact. No model training, model eval, export, or endpoint action is in
  scope.

## Required Evidence

The worker report must include:

- branch/head/PR or exact blocker;
- task-owned output root and final `packed_qwen` root;
- exact commands, environment, code revision, and whether code was synced or run
  locally only;
- input source paths and checksums, especially task262 V11 blend plan and
  task246 heldout/decontam evidence;
- split manifest path and checksum;
- row, input-token, supervised-token, shard, and source counts for train and
  valid;
- intended-vs-exposed multiset parity for train and valid split entries, not
  only count parity;
- Qwen packed-data contract PASS evidence using the Qwen3-4B tokenizer path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
- proof Qwen packing remains tokenizer-native with `enable_thinking=false` and
  `truncate_history_thinking=false`;
- checksums for manifest/report/shards or a deterministic shard checksum list;
- proof no AIME2025 prompt or label rows are trainable data, including heldout
  prompt-hash/decontam corpus checks and label-like key scan;
- explicit statement that no training, nonzero-LR smoke, live canary,
  AIME/task243 eval, export, endpoint, promotion, task255 reuse, AIME2025 train
  data, 30B/8-GPU, shared deletion, or main push was performed.

## Boundaries

- Do not run SFT training, nonzero-LR smoke, live canary, AIME/task243 eval,
  export, endpoint, promotion, or 30B/8-GPU.
- Do not use AIME2025 prompts or labels as trainable data. AIME2025 may only be
  used as held-out eval/decontamination material.
- Do not reuse task255 checkpoint/export as a candidate or training source.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song` or prior task output roots.
- If the intended task-owned output root already exists, create a new
  timestamped subdirectory or fail closed and report the exact blocker.
- Do not self-merge before lead review. If a PR is approved, merge only after
  lead releases an exact-head self-merge instruction.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task276_qwen_aime_v11_rematerialize_packed_qwen_s1`.
- PR to `main` if repo docs/status/scripts change. If only artifacts are
  produced, still push task/status docs and send a mailbox report with exact
  artifact paths and checksums.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/`.
- Suggested final packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/packed_qwen/`.
- Report:
  `workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/v11_rematerialized_packed_qwen_report.md`.

## Acceptance Criteria

- PASS: a fresh V11 `packed_qwen` root exists under the task-owned output root,
  intended-vs-exposed train/valid entries match as multisets, Qwen packed-data
  contract passes, counts/checksums are complete, and no AIME2025 prompt/label
  train leakage is found.
- REQUEST-CHANGES: artifact exists but evidence is incomplete, stale,
  non-reviewable, or missing a required count/checksum/contract proof.
- BLOCK: exact missing input, dependency, permission, data-integrity issue, or
  output-root safety issue prevents rematerialization.
- This task can only unblock a later no-training config/import preflight review
  after independent review. It does not authorize training/eval/promotion.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task246, task251, task253, task254, task262, task271, task272,
  task273, task274, task275
- Related PRs: #328, #336, #340, #341, #342, #343
- First gate: fresh collision-safe V11 packed Qwen root or exact blocker.
