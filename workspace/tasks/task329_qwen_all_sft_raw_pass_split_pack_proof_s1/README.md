# task329_qwen_all_sft_raw_pass_split_pack_proof_s1 - Raw-pass split and Qwen30B packing proof

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Background

task328/#391 closed the post-task327 packed-contract conversion as
`PARTIAL_PASS_WITH_EXACT_BLOCKERS`: no new all-eligible `packed_qwen` root is
accepted. The prior constrained task299 seed remains the only safe carry-forward
packed root. Three raw pass sources are blocked before training data use:

- task322/#388 `instruction-following-structured`
- task322/#388 `agentic-interactive`
- task327/#390 `swe`

These sources have row/checksum/decontam pass evidence, but they lack accepted
split exposure/parity proof and Qwen3-30B supervised-token packing proof. The
nine task327 decontam-hit sources remain excluded fail-closed.

## Goal

Produce a no-training proof that the three raw pass sources can be safely
split, exposed, decontaminated, and packed for
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`, or return an
exact blocker. This task does not authorize task310 training or benchmark eval.

## Required Inputs

- Current `origin/main`: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`.
- task322/#388 current head `adf1a02f3cd5da11d04d2a4d167bdb8d1573e79f`
  and artifact root
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z`.
- task327/#390 current head `49c5d748c8c9ecc95d21c69a1bd16af0118cba3d`
  and artifact root
  `/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/run_20260603T211508Z`.
- task328/#391 refreshed gate head
  `7181289cca14af741e7f704b6f34219805822a3e`, gate comment
  `issuecomment-4619254901`, and output root
  `/work-agents/intern_nemotron_worker_2/outputs/task328_qwen_all_sft_post_task327_packed_contract_s1/run_20260604T051338Z`.
- Prior constrained task299 packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
- Heldout/decontam references used by task246/task276/task299/task322/task327,
  including AIME2025, HMMT, MATH, and MMLU-Pro heldouts as applicable.

## Scope

- Branch:
  `intern_nemotron_worker_2/task329_qwen_all_sft_raw_pass_split_pack_proof_s1`.
- Build a task-owned output root under
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/`.
- For each of the three raw pass sources:
  - pin source file path, source sha256, row-manifest sha256, and row count;
  - define deterministic split policy with source id and row id provenance;
  - produce intended-vs-exposed multiset parity for train/valid/test or return
    an exact sparse-valid/test blocker;
  - prove heldout/decontam exclusion, especially no AIME2025 prompt/label train
    rows;
  - pack with Qwen3-30B tokenizer/chat-template path and report row counts,
    shard counts, input-token counts, supervised-token counts, and shard
    checksums.
- If all three sources pass, produce an expanded candidate packed root that
  either combines the prior constrained task299 seed plus the three raw pass
  sources or emits a precise manifest explaining why combination must wait for a
  later task. Any produced root still requires independent review before task310.
- If any source cannot pass safely, fail closed with exact blockers and do not
  produce an accepted training contract.

## Exclusions

- Exclude all nine task327 `BLOCKED_DECONTAM_HIT` sources:
  `instruction-following-chat`, `competitive-cpp-00`, `competitive-cpp-01`,
  `competitive-python-00`, `competitive-python-01`, `math-proofs-lean`,
  `agentic-tool-calling`, `infinibyte-00`, and `infinibyte-01`.
- Exclude task255 artifacts and all heldout/eval/decontam rows.
- Do not use AIME2025 prompts or labels as training rows.

## Boundaries

- No optimizer steps, full training, nonzero-LR smoke, benchmark eval, export,
  endpoint, promotion, or 30B runtime training launch.
- No task255 reuse.
- No shared deletion or mutation, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- No product-code edits unless the task returns a blocker that explicitly
  requires later lead-approved implementation work.
- Do not silently downgrade to Qwen3-4B or another model family.
- Do not merge, self-merge, or push main.

## Expected Output

- Report:
  `workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/raw_pass_split_pack_proof_report.md`.
- Task-owned output root with source matrix, split manifests, intended-vs-exposed
  parity proof, decontam proof, Qwen3-30B tokenizer/chat-template packing proof,
  packed shard checksums if produced, commands/env, logs, and checksum manifest.
- PR to `main` for task docs/status/report/helper files only.
- Mailbox report with branch/head/PR, artifact paths, commands/env, source
  matrix, split and pack metrics, checksums, pass/block disposition, and
  task310 recommendation.

## Worker Closeout Summary

Worker output root:
`/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.

Disposition: `PARTIAL_PASS_WITH_EXACT_BLOCKERS`.

Produced task-owned Qwen3-30B packed artifacts and checksum-backed evidence for
the three allowed raw pass sources. Qwen packed-data contract validation passed,
and all nine task327 `BLOCKED_DECONTAM_HIT` sources remained excluded. The
artifact is not ready for task310 because `task327-swe` produced zero supervised
tokens, `instruction-following-structured` had 6 validation-filtered rows, and
valid/test split exposure is sparse.

## Acceptance Criteria

- `PASS_RAW_PASS_SPLIT_PACK_PROOF`: the three raw pass sources have accepted
  split exposure/parity, decontam, and Qwen3-30B packing proof with complete
  checksums and no heldout/AIME2025/task255 leakage. This is still not training
  release; it only enables an independent packed-contract review.
- `PARTIAL_PASS_WITH_EXACT_BLOCKERS`: at least one source or combination path is
  proven safe, but final expanded packed contract remains blocked by exact
  source/split/decontam/tokenizer/packing evidence gaps.
- `BLOCK_RAW_PASS_SPLIT_PACK_PROOF`: safe split/pack proof cannot be produced
  without violating source eligibility, decontam, AIME2025/task255, split
  exposure, tokenizer, or resource boundaries.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Upstream evidence: task299, task322/#388, task327/#390, task328/#391,
  task246/task276 decontam references
- Downstream tasks: independent packed-contract review, then task310 only if
  separately released
- Gate state: all training/eval/export/endpoint/promotion remain HOLD.
