# task333_qwen_all_sft_combined_packed_contract_s1 - Combined all-SFT packed contract

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_1,SESSION=84 -->

## Background

The all-SFT 30B workstream is still blocked before task310 training. The latest
accepted state on `origin/main` is `ad0c5a7d758d44370695b94c83385591f100c714`.

Merged evidence to carry forward:

- #392/task329: `PARTIAL_PASS_WITH_EXACT_BLOCKERS`; raw-pass packing proved
  source/decontam basics but exposed SWE zero supervised tokens, six structured
  validation-filtered rows, sparse valid/test exposure, and deferred task299
  combination.
- #394/task332: `PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING`; exact six
  structured rows are fail-closed excluded, and deterministic split policy
  `task332_per_source_shard_holdout_v1` is accepted for later materialization.
- #395/task331: `PASS_SWE_SUPERVISED_UNBLOCK`; SWE can produce nonzero
  supervised tokens under Qwen3-30B packing with task-local
  `tools_field=task331_missing_tools_header`, preserving messages and avoiding
  the root-level tools header.

This task converts those accepted pieces into a fresh task-owned combined
all-SFT packed-data contract candidate. It is still no-training evidence only.

## Goal

Produce a fresh combined packed root and contract report that safely combines:

- the prior constrained task299 30B seed packed root,
- accepted task322/task329 raw-pass sources `agentic-interactive` and
  `instruction-following-structured`,
- accepted task327/task331 `swe` with the no-tools-header formatter config,
- task332 deterministic split policy and fail-closed structured row exclusions.

If the combined contract cannot be produced safely, fail closed with exact
source/config/split/packing/resource blockers.

## Required Inputs

- Current `origin/main`:
  `ad0c5a7d758d44370695b94c83385591f100c714`.
- Qwen3-30B tokenizer/model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Prior constrained task299 packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
- task329 raw-pass evidence root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.
- task332 split-policy evidence root:
  `/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z`.
- task331 SWE no-tools-header evidence root:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z`.
- Heldout/decontam references already used by task246/task276/task299/task322,
  task327, task329, task331, and task332.

## Required Contract

- Build a task-owned output root under
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/`.
- Do not mutate task299/task329/task331/task332 artifacts in place.
- Materialize a combined candidate packed root only if all included sources have
  source provenance, deterministic split assignment, checksums, decontam proof,
  and Qwen3-30B packed-data contract pass.
- Apply task332 policy `task332_per_source_shard_holdout_v1`: source-local
  `row_index % 16`, remainder 14 valid, remainder 15 test, all others train.
- Exclude exactly the six task332 structured rows fail-closed unless the task
  produces a separate source-remediation proof and reruns the validator. The
  default expected path is exclusion, not repair.
- For SWE, use task331 formatter/config provenance:
  `tools_field=task331_missing_tools_header`. Preserve `messages`; do not use
  the root-level tools schema in the Qwen chat template.
- Exclude all nine task327 `BLOCKED_DECONTAM_HIT` sources:
  `instruction-following-chat`, `competitive-cpp-00`, `competitive-cpp-01`,
  `competitive-python-00`, `competitive-python-01`, `math-proofs-lean`,
  `agentic-tool-calling`, `infinibyte-00`, and `infinibyte-01`.
- Exclude heldout/eval/decontam rows. AIME2025 prompts and labels must remain
  held out for eval/decontam only and must not enter training splits.
- Exclude task255 artifacts entirely.

## Required Evidence

Report all of the following, or fail closed:

- combined output root, packed root, split manifest, metadata, and blend paths;
- source-by-source row counts, source file sha256, row-manifest sha256, and
  inclusion/exclusion status;
- split counts by source and by train/valid/test;
- intended-vs-exposed multiset parity for every split and source;
- row/token/supervised-token/shard counts by source and split;
- validation-filtered row counts and exact exclusion manifest;
- decontam/no-AIME2025-train proof with prompt-hash, normalized-prompt, and
  n-gram counts;
- Qwen3-30B packed-data contract validation command, rc, and log path;
- artifact and packed shard checksum manifests with `sha256sum -c` proof;
- commands, environment, host, code revisions, and runtime/resource notes;
- explicit statement that no training/eval/export/endpoint/promotion/30B
  release/task255/shared deletion was performed.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task333_qwen_all_sft_combined_packed_contract_s1`.
- Report:
  `workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/combined_packed_contract_report.md`.
- Task-owned output root with manifests, logs, helper/config files, packed root
  or exact blocker, and checksum manifests.
- PR to `main` for task docs/status/report/helper/config files only.
- Mailbox closeout with branch/head/PR or exact blocker, commands/env, artifact
  paths, metrics, checksums, decontam result, and final disposition.

## Boundaries

- No training, optimizer steps, nonzero-LR smoke, benchmark eval, export,
  endpoint, promotion, 30B release, task310 release, merge, self-merge, or main
  push.
- No task255 reuse.
- No AIME2025 prompts or labels as training rows.
- No shared deletion or mutation, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not silently downgrade to Qwen3-4B or another model family.
- Do not include the nine task327 decontam-hit sources.

## Acceptance Criteria

- `PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW`: combined candidate root is
  produced with all required provenance, split/decontam/parity/checksum/Qwen
  contract evidence. This only enables independent review; it does not release
  task310.
- `PARTIAL_PASS_WITH_EXACT_BLOCKERS`: a safe subset or manifest is produced,
  but training contract remains blocked by explicit residuals.
- `BLOCK_COMBINED_PACKED_CONTRACT`: safe combination cannot proceed under the
  current data, split policy, tokenizer config, resource limits, or boundaries.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Base: current `origin/main` `ad0c5a7d758d44370695b94c83385591f100c714`
- Downstream: independent review task after PR/artifacts exist; task310 remains
  HOLD until the combined contract and review are accepted.
