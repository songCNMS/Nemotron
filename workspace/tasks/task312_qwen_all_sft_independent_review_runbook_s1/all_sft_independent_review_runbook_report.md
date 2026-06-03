# task312 Qwen all-SFT independent review runbook report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=81 -->

## Decision

Overall decision: `REQUEST_CHANGES_HOLD`.

Current upstream PR decisions:

| PR | Task | Current reviewed head | Decision |
|---|---|---|---|
| #374 | task308 | `f57384f6a298500f240a9367c3598cd5f9a59638` | `APPROVE_PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS` |
| #372 | task309 | `998ebce439164af2cc0e026575de32cd356acaa0` | `REQUEST_CHANGES_REFRESH_FROM_TASK308_374` |
| #373 | task310 | `1cd3eb17fc686b281da7a9a0791ea09fbe614664` | `APPROVE_BLOCKER_CLOSEOUT_WITH_FRESHNESS_RESIDUAL` |
| #371 | task311 | `37a76caea59a2ca27c5d4cbc5d2e98d46d100420` | `APPROVE_BLOCKER_CLOSEOUT_WITH_FRESHNESS_RESIDUAL` |

Combined all-SFT gate remains HOLD/NO-GO. task308 now supplies an approvable
inventory audit, but task309 has not refreshed from that audit into a current
packed-data contract, task310 has no usable checkpoint, and task311 has no
canary or benchmark artifacts.

This review does not authorize training, packing, eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, product-code
edits, main push, merge, or worker-branch rewrite.

## Reviewed Refs

- Current main / branch base:
  `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`.
- Product-code baseline:
  `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- Lead docs branch was fetched during this task at `9f838e94`; task312
  baseline reconciliation was recorded by lead commit `5f4167dc`.
- #374/task308 requested head was
  `4a46c9b5995d5cebe6624a5241d5543d48bee93c`; current GitHub head at review
  time was `f57384f6a298500f240a9367c3598cd5f9a59638`.
- #372/#373/#371 matched the requested exact heads.

PR state at review time:

- #374: OPEN, base `main`, CLEAN/MERGEABLE, non-draft.
- #372: OPEN, base `main`, CLEAN/MERGEABLE, non-draft.
- #373: OPEN, base `main`, CLEAN/MERGEABLE, non-draft.
- #371: OPEN, base `main`, CLEAN/MERGEABLE, non-draft.

Diff scope:

- All four PR diffs are docs/status-only and pass `git diff --check`.
- `4a46c9b..f57384f6` for #374 changes only worker_1 status and task308
  history. The task308 report and artifact manifest are unchanged.

## Commands And Checks

Static review commands used:

- `gh pr view 371|372|373|374 --json ...`
- `git fetch origin main pull/371/head:refs/remotes/origin/pr/371 pull/372/head:refs/remotes/origin/pr/372 pull/373/head:refs/remotes/origin/pr/373 pull/374/head:refs/remotes/origin/pr/374`
- `git diff --name-status origin/main...origin/pr/<pr>`
- `git diff --check origin/main...origin/pr/<pr>`
- `git diff --name-status 4a46c9b5995d5cebe6624a5241d5543d48bee93c..origin/pr/374`
- `git show origin/pr/<pr>:workspace/tasks/.../<report>.md`
- `sha256sum` and `sha256sum -c` over named task308/task309/task311 artifacts.
- Python/JQ read-only inspection of task308/task309/task311 manifests.
- Read-only task310 output-root search under
  `/work-agents/intern_nemotron_worker_5/outputs`, `/root`, and `/work-agents`.

No implementation tests, training, packing, eval, export, endpoint launch, or
mutation of upstream artifacts/branches was performed.

## task308 / #374

Report:
`workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1/all_sft_pipeline_inventory_audit_report.md`

Task-owned artifact root:
`/work-agents/intern_nemotron_worker_1/outputs/task308_qwen_all_sft_pipeline_inventory_audit_s1/run_20260603T144136Z`

Inventory manifest:
`all_sft_inventory_manifest.json`

Manifest sha256 verified:
`4f629e015d4e7a8965899f1fb6c1a5e22e4e666fff28c5bfa69d9d9b31f97a61`.

Verified manifest fields:

- decision: `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`;
- current main: `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`;
- product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`;
- boundary flags are false for training, final packing, benchmark eval, export,
  endpoint, promotion claim, task255 reuse, AIME2025 train rows, shared
  deletion, product-code edits, and main push/merge.

Checksum-backed M1/V11 source checks:

| Source | Rows | sha256 | Local check |
|---|---:|---|---|
| `m1-agentic-sft-v11-from-m0` | 1100 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` | rows/hash match |
| `m1-agentic-sft-v11-math-final-answer` | 200 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` | rows/hash match |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 8 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` | rows/hash match |

Task299 packed Qwen3-30B seed evidence carried by task308:

- packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`;
- top manifest sha:
  `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`;
- train rows/input tokens/supervised tokens: `279` / `1024646` / `228927`;
- valid rows: `1`; test rows: `0`;
- tokenizer equivalence and decontam status carried as PASS.

Generic `stage1_sft/data_blend_raw` coverage:

- 12 HF source files are inventoried with repo/file hashes and weights.
- Every generic entry is explicitly
  `BLOCKED_FOR_TASK309_UNTIL_MATERIALIZED_COUNTED_DECONTAM_SCANNED`.
- Missing for those generic sources: exact row counts, trainable prompt-hash or
  n-gram decontam, Qwen chat-template packing, and supervised-token counts.

Decision for #374: approve as inventory audit with task309 fail-closed
constraints. This approval does not approve packing, training, eval, export,
endpoint, promotion, or use of generic stage1 sources without the missing
materialization/decontam/packing proof.

## task309 / #372

Report:
`workspace/tasks/task309_qwen_all_sft_packed_data_contract_s1/all_sft_packed_data_contract_report.md`

Task-owned artifact root:
`/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T143700Z`

Disposition in #372:
`BLOCK_DEPENDENCY_TASK308_INVENTORY_MISSING`.

Review finding: request changes / refresh required.

Reasons:

- #372 predates current task308/#374 and says task308 inventory was missing.
  That is stale now that #374 provides a pass audit with explicit constraints.
- #372 produced no new packed root and cannot serve as the current
  all-eligible-SFT packed contract.
- Named key hashes for the blocker artifacts match local files, but replaying
  `manifests/task309_artifact_checksums.sha256` from the artifact root fails for
  three generated files:
  - `manifests/task309_artifact_checksums.sha256`;
  - `manifests/task309_file_inventory.txt`;
  - `manifests/task309_file_inventory.txt.sha256`.

Required refresh:

1. Consume #374 as the upstream task308 inventory.
2. Decide fail-closed whether to pack only checksum-backed V11/M1 sources or to
   first materialize/count/decontam generic stage1 SFT sources.
3. If packing, publish a fresh packed root, split/source manifests,
   row/token/supervised-token/shard counts, intended-vs-exposed parity,
   Qwen3-30B tokenizer/chat-template proof, checksum manifest, and no-AIME2025
   train proof.
4. If blocking, publish a current blocker tied to #374, not the old
   task308-missing state.

Task310 remains `NO_GO_HOLD` until this is fixed.

## task310 / #373

Report:
`workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md`

Disposition in #373:
`BLOCK_PRETRAINING_GATE`.

Review finding: approve blocker closeout with freshness residual.

Evidence:

- No training launch, optimizer step, GPU allocation, loss/validation,
  checkpoint, or checksum artifact was produced.
- Read-only output search found no task310 training artifact root under
  `/work-agents/intern_nemotron_worker_5/outputs`, `/root`, or `/work-agents`.
- The blocker remains valid because there is still no accepted current
  `PASS_PACKED_CONTRACT` from task309 and no all-SFT checkpoint handoff.

Freshness residual:

- #373 predates #374/#372 and says task308/task309 had no visible PR/report.
  That upstream visibility is stale, but the no-training blocker remains
  correct because #372 still does not provide a current packed contract.

## task311 / #371

Reports:

- `all_sft_non_aime_canary_report.md`
- `all_sft_corrected_qwen_benchmark_report.md`
- `all_sft_m1_benchmark_availability_report.md`

Task-owned artifact root:
`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T143618Z`

Blocker manifest:
`manifests/blocker_manifest.json`

Blocker manifest sha256 verified:
`7b90155bc4f31bea4ccb5a67472d0c5d703c5607b0ec0a20d0523bdadc179ed8`.

Disposition:
`BLOCK_UPSTREAM_TASK310_HANDOFF_MISSING`.

Review finding: approve blocker closeout with freshness residual.

Evidence:

- No checkpoint-load canary, non-AIME generation, corrected Qwen benchmark,
  AIME, HMMT, MMLU-Pro, or M1 benchmark command was launched.
- No completions, parser diagnostics, benchmark summaries, or benchmark
  checksum manifests were produced.
- The blocker remains valid because #373 has no usable checkpoint handoff.

Unavailable benchmark rows:

| Benchmark group | Status | Exact blocker |
|---|---|---|
| MMLU-Pro | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed |
| AIME2025 | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; canary not passed; AIME2025 remains held-out eval/decontam only |
| HMMT | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed |
| M1 basket | `BLOCKED_NOT_ENUMERATED` | checkpoint path/run root/artifact manifest missing; canary not passed |

Freshness residual:

- #371 predates #373 and says no task310 PR exists. #373 now exists, but it is
  itself a pretraining-gate blocker and provides no checkpoint, so the task311
  no-canary/no-eval blocker remains correct.

## Boundary Review

Across the reviewed evidence, I found no indication that any upstream task ran
forbidden work:

- no training or optimizer steps;
- no packing run by task309;
- no benchmark eval or canary run;
- no export or endpoint;
- no promotion claim;
- no task255 reuse;
- no AIME2025 train prompts or labels;
- no shared deletion;
- no product-code edits;
- no direct main push or merge.

These are static review findings from reports/manifests/diffs; I did not run
implementation tests or live workloads.

## Runbook Recommendation

Recommended lead wording:

`APPROVE #374 as PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS at current head f57384f6, noting requested 4a46c9b advanced by status/history-only drift. REQUEST_CHANGES for #372: refresh/rerun task309 from #374 and do not treat the old task308-missing blocker as current. APPROVE #373 and #371 as blocker closeouts with freshness residuals: #373 correctly did not train because no current packed contract/checkpoint exists, and #371 correctly did not canary/eval because no task310 checkpoint handoff exists. Combined all-SFT gate remains HOLD/NO-GO: no promotion, export, endpoint, benchmark comparison, further scale decision, training continuation, or merge authorization until task309 produces current accepted packed-contract evidence and downstream task310/task311 refresh from it.`

Residual risks:

- #374 current head differs from the originally requested `4a46c9b`; I verified
  the drift to `f57384f6` is worker_1 status/history-only.
- #372 checksum-manifest replay has self/inventory mismatches and is stale
  relative to #374.
- #371/#373 blocker reports have stale upstream visibility, but their core
  blockers remain true because no current task309 packed contract or task310
  checkpoint handoff exists.
