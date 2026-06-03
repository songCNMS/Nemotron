# task312 Qwen all-SFT independent review runbook report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=82 -->

## Decision

Overall decision: `APPROVE_CONSTRAINED_TASK309_WITH_HOLD_FOR_DOWNSTREAM`.

Current upstream PR decisions:

| PR | Task | Exact reviewed head | Decision |
|---|---|---|---|
| #374 | task308 | `b798fdfcfc3144111dd0a6e0f80505df031bcc5e` | `APPROVE_PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS` |
| #372 | task309 | `fe1bb38c55545b54dc017647ae9f299ee1a5ac02` | `APPROVE_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS` |
| #373 | task310 | `7000f3714442c39fd78e40249d9d5ed69528d9eb` | `REQUEST_CHANGES_REFRESH_FOR_CONSTRAINED_TASK299_SEED_AFTER_TASK309_ACCEPTANCE` |
| #371 | task311 | `6981a654c1c72c72dfb57fd42aa60cc15b0a9f77` | `APPROVE_BLOCKER_CLOSEOUT_WITH_FRESHNESS_RESIDUAL` |

Gate conclusion:

- task310 may proceed only after lead accepts #372 and only on the constrained
  V11/task299 Qwen3-30B packed seed.
- Generic `stage1_sft/data_blend_raw` remains blocked from the training input
  unless it is separately materialized, counted, decontam-scanned, Qwen-packed,
  and reviewed.
- No benchmark/canary/AIME/task243 release follows from this review. task311
  remains blocked until task310 produces a usable checkpoint handoff.

This review does not authorize training, packing, eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, product-code
edits, main push, merge, or worker-branch rewrite.

## Reviewed Refs

- Current main / branch base:
  `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`.
- Product-code baseline:
  `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- #374/#372/#373/#371 were all OPEN, base `main`, CLEAN/MERGEABLE, and
  non-draft at review time.
- All four PR diffs are docs/status-only and pass `git diff --check`.
- Drift from previous task312 review:
  - #374 `f57384f6..b798fdfc`: worker_1 status/history/task_knowledge only.
  - #372 `998ebce4..fe1bb38c`: substantive task309 constrained-contract report
    refresh.
  - #373 `1cd3eb17..7000f371`: task310 HOLD/report/status refresh, but still
    stale relative to #372 `fe1bb38c`.
  - #371 `37a76cae..6981a654`: task311 HOLD/report/status refresh, but still no
    checkpoint handoff.

## Commands And Checks

Static review commands used:

- `gh pr view 371|372|373|374 --json ...`
- `git fetch origin main pull/371/head:refs/remotes/origin/pr/371 pull/372/head:refs/remotes/origin/pr/372 pull/373/head:refs/remotes/origin/pr/373 pull/374/head:refs/remotes/origin/pr/374`
- `git diff --name-status origin/main...origin/pr/<pr>`
- `git diff --check origin/main...origin/pr/<pr>`
- `git diff --name-status/check` for previous-head to current-head PR ranges.
- `git show origin/pr/<pr>:workspace/tasks/.../<report>.md`
- `sha256sum` and `sha256sum -c` over task308/task309/task311 artifacts.
- Python/JQ read-only inspection of task308/task309/task311 manifests.
- Read-only task310 output-root search under
  `/work-agents/intern_nemotron_worker_5/outputs`, `/root`, and `/work-agents`.

No implementation tests, training, packing, eval, export, endpoint launch, or
mutation of upstream artifacts/branches was performed.

## task308 / #374

Report:
`workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1/all_sft_pipeline_inventory_audit_report.md`

Artifact root:
`/work-agents/intern_nemotron_worker_1/outputs/task308_qwen_all_sft_pipeline_inventory_audit_s1/run_20260603T144136Z`

Inventory manifest sha256 verified:
`4f629e015d4e7a8965899f1fb6c1a5e22e4e666fff28c5bfa69d9d9b31f97a61`.

Decision: `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`.

Verified facts:

- current main: `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`;
- product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`;
- boundary flags are false for training, final packing, benchmark eval, export,
  endpoint, promotion claim, task255 reuse, AIME2025 train rows, shared
  deletion, product-code edits, and main push/merge.

Checksum-backed M1/V11 raw sources verified locally:

| Source | Rows | sha256 | Local check |
|---|---:|---|---|
| `m1-agentic-sft-v11-from-m0` | 1100 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` | rows/hash match |
| `m1-agentic-sft-v11-math-final-answer` | 200 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` | rows/hash match |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 8 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` | rows/hash match |

Generic `stage1_sft/data_blend_raw` remains constrained:

- 12 HF source files are inventoried with repo/file hashes and weights.
- Exact row counts, trainable prompt-hash/ngram decontam, Qwen chat-template
  packing, and supervised-token counts are not materialized.
- Those raw sources must remain excluded from task309/task310 unless a later
  task supplies the missing proof.

Decision for #374: approve as inventory audit. This does not approve packing,
training, eval, export, endpoint, promotion, or generic raw-stage1 inclusion.

## task309 / #372

Report:
`workspace/tasks/task309_qwen_all_sft_packed_data_contract_s1/all_sft_packed_data_contract_report.md`

Artifact root:
`/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T145300Z`

Constrained contract manifest:
`manifests/task309_constrained_packed_contract_manifest.json`

Manifest sha256 verified:
`f33a14d05ab911779a8f43b5af138c6f4fa815191af3305820480a27fed47a14`.

Full task309 artifact checksum manifest sha256 verified:
`b794bf3b96b6811d409b903b4b2ed2d95536b8ed655a4da44d9cf380143d6615`.

`sha256sum -c manifests/task309_artifact_checksums.sha256` passed.
Qwen3-30B model asset hashes passed for `config.json`, `tokenizer.json`,
`tokenizer_config.json`, `vocab.json`, and `merges.txt`.

Disposition:
`PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS`.

The constrained contract identifies the previously reviewed task299 Qwen3-30B
packed root as the training seed:

`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Referenced original task299 artifacts were rehashed from their original paths
and matched the manifest:

- `manifest.json`:
  `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`;
- `contract_validation.json`:
  `75265f68621676c846551ba12022cb3d6f383b4f65e3bc7fb9773a197434d0b2`;
- `split_counts_parity.json`:
  `f4c335e651cc7777ecf326ed2fa3e46791c3de7286d7dee86042d941db2be70d`;
- `decontam_proof.json`:
  `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc`;
- `tokenizer_chat_template_equivalence_probe.json`:
  `f31d5229da06ef1ff7c5457acfd66a7b4b4c91e92c61d7ae00f4492b476000ec`;
- `packed_qwen_30b_shard_checksums.json`:
  `444aef9230129d689c27be295ff054fc1dc4800fae52827280a5c289408fed11`.

Constrained packed split counts:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

Train source counts:

| Source | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942062 | 167555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75305 | 54821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 7 | 7279 | 6551 |

Contract results:

- Qwen packed/training contract validation: PASS.
- Intended-vs-exposed multiset parity: PASS.
- Decontam/no-AIME2025-train proof: PASS.
- Tokenizer-native Qwen chat-template/API equivalence: PASS.
- Task255 reuse: false.
- No new task309 packing run was executed; #372 identifies and checksums the
  existing reviewed task299 root as the constrained seed.

Decision for #372: approve for constrained V11/task299 seed only. Generic
stage1 raw SFT remains excluded. This approval does not approve promotion,
export, endpoint, benchmark comparison, or generic all-raw-SFT inclusion.

## task310 / #373

Report:
`workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md`

Disposition:
`BLOCK_PRETRAINING_GATE`.

Review finding:
`REQUEST_CHANGES_REFRESH_FOR_CONSTRAINED_TASK299_SEED_AFTER_TASK309_ACCEPTANCE`.

No training launch, optimizer step, GPU allocation, loss/validation, checkpoint,
or checksum artifact was produced. Read-only output search found no task310
training artifact root under `/work-agents/intern_nemotron_worker_5/outputs`,
`/root`, or `/work-agents`.

The no-training HOLD was correct before #372 refreshed. However #373 at
`7000f371` still says task309 #372 must refresh from #374 and still refers to
old #372 head `998ebce4`. Because current #372 at `fe1bb38c` is approvable as
a constrained packed contract, task310 should now refresh its gate after lead
accepts #372.

Task310 may proceed only under these constraints:

- Lead accepts #374 and #372.
- The input packed root is exactly the constrained task299 root carried by
  #372.
- Generic `stage1_sft/data_blend_raw` remains excluded.
- Runtime/resource assumptions are refreshed against current main and exact
  packed root before launch.
- No promotion/export/endpoint/AIME or benchmark claim is made by launch.

Current #373 should not be treated as a launch plan or as generic all-SFT
clearance.

## task311 / #371

Reports:

- `all_sft_non_aime_canary_report.md`
- `all_sft_corrected_qwen_benchmark_report.md`
- `all_sft_m1_benchmark_availability_report.md`

Artifact root:
`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T143618Z`

Blocker manifest:
`manifests/blocker_manifest.json`

Blocker manifest sha256 verified:
`7b90155bc4f31bea4ccb5a67472d0c5d703c5607b0ec0a20d0523bdadc179ed8`.

Disposition:
`BLOCK_UPSTREAM_TASK310_HANDOFF_MISSING`.

Review finding:
`APPROVE_BLOCKER_CLOSEOUT_WITH_FRESHNESS_RESIDUAL`.

No checkpoint-load canary, non-AIME generation, corrected Qwen benchmark, AIME,
HMMT, MMLU-Pro, or M1 benchmark command was launched. No completions, parser
diagnostics, benchmark summaries, or benchmark checksum manifests were
produced.

Unavailable benchmark rows:

| Benchmark group | Status | Exact blocker |
|---|---|---|
| MMLU-Pro | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed |
| AIME2025 | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; canary not passed; AIME2025 remains held-out eval/decontam only |
| HMMT | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed |
| M1 basket | `BLOCKED_NOT_ENUMERATED` | checkpoint path/run root/artifact manifest missing; canary not passed |

Freshness residual: #371 still claims no task310 PR/branch was visible at probe
time, but #373 now exists as a HOLD/blocker PR and still provides no usable
checkpoint. Therefore the task311 blocker remains true.

## Boundary Review

Across the reviewed evidence, I found no indication that any upstream task ran
forbidden work:

- no training or optimizer steps;
- no new task309 packing run;
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

`APPROVE #374 at b798fdfc as PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS. APPROVE #372 at fe1bb38c as PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS: task310 may proceed only after lead acceptance and only using the constrained task299 packed root; generic stage1_sft/data_blend_raw remains excluded unless separately materialized, decontam-scanned, Qwen-packed, and reviewed. REQUEST_CHANGES/REFRESH #373 at 7000f371 before any launch because it still reflects the pre-fe1bb38 #372 state; it may refresh to a constrained-seed launch gate after #372 is accepted. APPROVE #371 at 6981a654 as BLOCK_UPSTREAM_TASK310_HANDOFF_MISSING/HOLD because no task310 checkpoint exists. No promotion, export, endpoint, benchmark comparison, generic raw-SFT inclusion, task255 reuse, or AIME2025 train-data use is authorized.`

Residual risks:

- The constrained packed root has sparse valid/test splits: valid `1`, test `0`.
- #372 did not run new packing; it identifies and checksums the existing
  reviewed task299 root as the constrained seed.
- task310 runtime/resource assumptions still need refresh before any launch.
- task311 has no benchmark row-level evidence because no checkpoint handoff
  exists.
