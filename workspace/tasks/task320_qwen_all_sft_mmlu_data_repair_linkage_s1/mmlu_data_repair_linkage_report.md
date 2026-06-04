# task320 MMLU-Pro data repair linkage report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=93 -->

Generated: 2026-06-03T20:10:00Z

## Disposition

Recommendation: `APPROVE_LINKAGE`.

Task314's MMLU-Pro `-2` should be treated as a data-repair constraint for the
next all-SFT blend, not as an evaluator artifact. The accepted task314 finding
is that the regression is real answer-choice drift under aligned rows,
protocol, parser, and checksums. The repair implication is direct: preserve the
math improvement, but do not repeat or simply extend the current narrow
task299/V11 seed without adding broad, decontaminated retention coverage.

This task is docs/analysis only. It does not authorize data materialization,
packing, training, eval rerun, export, endpoint launch, promotion, task255
reuse, AIME2025 train rows, shared deletion, main push, merge, or self-merge.

## Reviewed evidence

| Area | Evidence | Result used by task320 |
|---|---|---|
| task314 forensics | PR #380, lead accepted `APPROVE_FORENSICS_DOCS / NO_ACTION_RELEASE` at `d3bd97331932ba4263a1516c8f93c599d860046d`; current #380 observed `OPEN`, base `main`, `CLEAN/MERGEABLE`, head `9e57390bb33365157b73a8c93264b9dd57a2d489`. | MMLU-Pro `-2` is real answer-choice drift, not parser/protocol artifact. |
| task314 outputs | `/work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z` | Row/category transition source for this linkage report. |
| task308 inventory | `all_sft_pipeline_inventory_audit_report.md`; inventory manifest sha256 `4f629e015d4e7a8965899f1fb6c1a5e22e4e666fff28c5bfa69d9d9b31f97a61`. | Only checksum-backed V11/task299 seed is task-ready; generic raw blend is excluded until materialized/count/decontam/Qwen-packed. |
| task309 packed contract | `PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS`; contract manifest sha256 `f33a14d05ab911779a8f43b5af138c6f4fa815191af3305820480a27fed47a14`. | Current accepted packed root is constrained task299 seed only, not full all-SFT. |
| task316 plan | PR #377 observed `OPEN`, base `main`, `CLEAN/MERGEABLE`, head `c1b053b518137769b9b423d08d9590d8ae481a2e`. | Repair direction is data-blend plus validation-exit repair before any new 30B training. |
| task319 feasibility | Task319 assignment docs visible; no task319 PR found during this review. | Final raw source/decontam feasibility remains a dependency. |

Key task314 output checksums:

| File | sha256 |
|---|---:|
| `mmlu_pro_forensics_summary.json` | `ad32029db43672fa96cbd722b6beeed4121ce1b8d4e94c0f2fb5d051b61a38c9` |
| `mmlu_pro_category_deltas.json` | `6bad651016a28ef7e1af6a50560108f93093144672f32beec3297062fe09c265` |
| `mmlu_pro_row_transitions.jsonl` | `ab338411b96010b3408679f56d42185d69907bfd4a6272c85b8481d3ef077760` |
| `output_checksum_manifest.json` | `10bd7713eb6bc82a8fc5b7421115356f93ac95c72f4dc675908c9d941722ba50` |

## Task314 category findings

Overall MMLU-Pro:

| Metric | Base | FT | Delta |
|---|---:|---:|---:|
| Correct rows | `6758/12032` | `6756/12032` | `-2` |
| Accuracy | `0.5616688829787234` | `0.5615026595744681` | `-0.0001662234042553168` |
| Row losses/gains | n/a | n/a | `92` losses, `90` gains |

Category deltas:

| Category | Rows | Delta | Losses | Gains | Repair priority |
|---|---:|---:|---:|---:|---|
| physics | `1299` | `-6` | `16` | `10` | High retention priority |
| health | `818` | `-4` | `6` | `2` | High retention priority |
| chemistry | `1132` | `-3` | `7` | `4` | High retention priority |
| history | `381` | `-2` | `5` | `3` | Retention priority |
| other | `924` | `-2` | `7` | `5` | Retention priority |
| biology | `717` | `-1` | `3` | `2` | Retention priority |
| business | `789` | `-1` | `6` | `5` | Retention priority |
| psychology | `798` | `-1` | `4` | `3` | Retention priority |
| computer science | `410` | `0` | `2` | `2` | Preserve |
| economics | `844` | `0` | `6` | `6` | Preserve |
| philosophy | `499` | `0` | `2` | `2` | Preserve |
| engineering | `969` | `+2` | `13` | `15` | Preserve, but monitor churn |
| law | `1101` | `+3` | `9` | `12` | Preserve, but monitor churn |
| math | `1351` | `+13` | `6` | `19` | Preserve gain; do not over-weight blindly |

Important aggregate:

- Math gained `+13`, but every non-math category together summed to `-15`.
- `86/92` base-correct to FT-wrong losses were outside math.
- The row churn is broad: `352` changed predictions, including `170`
  both-wrong swaps.

Data-repair implication: a future blend must be judged on broad retention
coverage, not only AIME/HMMT/math improvements.

## Current data seed linkage

Task308/task309 accepted the constrained task299 Qwen3-30B packed root:

`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Task299 manifest sha256:
`59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`.

Packed split:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | `46` | `279` | `1024646` | `228927` |
| valid | `1` | `1` | `1491` | `1428` |
| test | `1` | `0` | `0` | `0` |

Train source mix:

| Source | Rows | Supervised tokens | Linkage concern |
|---|---:|---:|---|
| `m1-agentic-sft-v11-from-m0` | `244` | `167555` | Broad M1 environments, but not labeled to MMLU-Pro domain retention. |
| `m1-agentic-sft-v11-math-final-answer` | `28` | `54821` | Math/final-answer retention useful for math gains. |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | `7` | `6551` | Very sparse hard-math sidecar. |

This seed is legitimate as a constrained V11/task299 contract, but it is too
narrow to serve as the data repair for task314's MMLU-Pro pattern. It contains
no accepted per-category source coverage for physics, health, chemistry,
history, biology, business, psychology, economics, philosophy, or broad "other"
retention. It also has a `1` row validation split and `0` test rows, which is
not enough for blend-balance validation.

## Data-repair constraints for the later blend task

### Source inventory constraints

A later lead-gated data repair task should not pack or train until it emits a
source inventory with:

- exact source path or dataset id;
- source revision and license;
- file sha256 or LFS sha256;
- exact row count;
- train/valid/test split assignment;
- per-source input-token and supervised-token counts after Qwen rendering;
- source family tag mapped to MMLU-Pro retention buckets;
- inclusion or exclusion decision with blocker text.

The task308 `stage1_sft/data_blend_raw` registry has 12 eligible-in-principle
sources, but task308/task309 correctly blocked them because row counts,
decontam proof, Qwen packing proof, and supervised-token counts were not
materialized. Task319 should supply or block that source matrix.

### MMLU-Pro retention bucket constraints

Future source manifests should map every included source to explicit retention
buckets. At minimum:

| Bucket | MMLU-Pro categories protected | Current task314 signal |
|---|---|---|
| Physical sciences | physics, chemistry | `-9` combined; highest priority |
| Bio-health | biology, health, psychology | `-6` combined |
| Humanities/social | history, philosophy, economics, business, law | mixed: history/business losses, law gain |
| Technical/coding | computer science, engineering | engineering gain but high churn |
| Math | math | `+13`, preserve gain |
| Broad instruction/other | other and uncategorized general knowledge | `-2`, retention priority |

Required balancing rule: the repaired blend must not be justified by aggregate
math performance alone. It must show nonzero materialized, decontaminated,
Qwen-rendered source coverage for every loss bucket above, or explicitly block
with source unavailability.

Practical guardrails for the next data task:

- keep task299/V11 math sources as a continuity seed, not as the full repair;
- avoid increasing the math-only/final-answer share unless physical-science,
  bio-health, humanities/social, and broad-instruction retention sources are
  also added and counted;
- report supervised-token percentages by bucket, not only row counts;
- include valid/test rows for every bucket with nonzero train coverage;
- fail closed if any high-priority loss bucket has unknown row count, unknown
  checksum, or no decontam proof.

### Contamination and heldout constraints

The next data repair must extend the existing AIME/HMMT/MATH heldout controls
with MMLU-Pro-specific protection:

- no AIME2025 prompts or labels in trainable outputs;
- no task255 reuse;
- no held-out HMMT/MATH prompt/label train rows;
- no MMLU-Pro test prompt/label train rows;
- include task311/task314 MMLU-Pro row-manifest prompt/problem hashes in the
  decontam corpus;
- run exact prompt-hash plus full token n-gram scans over trainable prompts and
  completions before packing;
- emit overlap counts by heldout family, all expected to be `0`.

The task314 MMLU-Pro row manifest sha256 is
`d6506bc08cb51f77ef1572a5546db0e19a146a49d936dcf07cf160e341fda985`; the
corrected-Qwen input sha256 was
`1c23fc1dae4745edcab672973ef66516cde6ff94f26e59be845a97c072caef36`. These
should be carried as heldout/decontam references, not as train data.

### Packing and split constraints

The later repair packed root should prove:

- Qwen3-30B-A3B tokenizer and chat-template equivalence;
- intended-vs-exposed shard parity;
- shard checksums;
- per-source and per-bucket row/token/supervised-token counts;
- train/valid/test counts that are not sparse like task299's `1` valid and `0`
  test rows;
- no hidden source category silently collapses into only math or agentic M1
  rows after packing.

Recommended fail-closed minimum for evidence, not as a command authorization:

- valid split has at least one row per included retention bucket;
- test or heldout-audit split is nonempty for pack integrity checks;
- bucket-level supervised-token percentages are emitted and reviewed before
  any training plan is proposed.

## Validation metrics for later lead-gated repair

### Pre-training data validation

Before training, require:

| Metric | Required result |
|---|---|
| Source row counts | exact for every included source |
| Source checksums | present for every included materialized file |
| Qwen-rendered token counts | per source and per retention bucket |
| Supervised-token counts | per source and per retention bucket |
| Heldout exact prompt overlaps | `0` for AIME2025, HMMT, MATH, MMLU-Pro |
| Heldout n-gram overlaps | `0` accepted overlaps, or reviewed false-positive manifest |
| Split parity | intended-vs-exposed multiset match |
| Valid/test sparsity | no all-zero test split; no single-row-only validation for a multi-bucket blend |
| Task255 reuse | `false` |
| AIME2025 train rows | `0` prompts, `0` labels |

### Post-training same-harness validation, if separately authorized

The next benchmark gate should use task311-style same-harness base-vs-FT rows
and must report category deltas, not only aggregate accuracy:

- aggregate MMLU-Pro FT must be at least base;
- non-math aggregate delta must be at least `0`;
- physical sciences and bio-health buckets must not repeat the task314 loss
  pattern;
- math gains should be preserved without allowing non-math regression;
- AIME2025 and HMMT must remain above or equal to base;
- parser, row manifest, endpoint, and cleanup evidence must match task311
  standards.

Stop condition for a later repair candidate: if MMLU-Pro remains below base,
or if the repaired blend improves math while non-math aggregate remains
negative, do not promote and do not proceed to broader release claims.

## Dependency on task319

Task319 is the blocking upstream for raw blend feasibility. Task320's linkage
requires task319 to provide:

- a final source matrix for the 12 `stage1_sft/data_blend_raw` entries;
- exact materialization feasibility for each source;
- row count and checksum availability;
- supervised-token counting feasibility under Qwen rendering;
- decontam plan against AIME2025/HMMT/MATH/MMLU-Pro heldouts;
- explicit source exclusions where counts or decontam cannot be proven.

Until task319 is accepted, the safe data-repair state is:
`BLOCK_PACK_OR_TRAIN_RAW_BLEND_PENDING_TASK319`.

If task319 blocks broad raw materialization, the next repair task should either
select a smaller lead-approved subset with full counts/decontam proof or stop
before packing. It should not fall back to "more task299-only training" as a
data repair for task314.

## Residual risks

1. Task320 does not inspect raw source contents and does not materialize data;
   all source feasibility depends on task319.
2. Task314's net regression is small, but row churn is broad enough that
   aggregate-only validation is unsafe.
3. Existing task299 seed is valid but sparse and narrow: `279` train rows, `1`
   valid row, and `0` test rows.
4. Generic raw sources are large and currently lack exact rows, decontam scans,
   supervised-token counts, and Qwen packing proof.
5. MMLU-Pro heldout protection must be added explicitly to the decontam corpus
   for future data repair; AIME/HMMT/MATH-only decontam is not sufficient for
   this regression.
6. Task316 remains planning/no-action-release and task319 has no final PR at
   this review, so task320 is linkage evidence only.

## Commands and environment

Local worktree:
`/work-agents/intern_nemotron_worker_1/Nemotron_task320`.

Base:
`origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`.

Lead docs:
`origin/intern_nemotron_lead/session1-recovery-task-docs`
`724ebecc971239f39daeb936bb48ec4bdc3aa52e`.

Read-only checks run:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git worktree add -b intern_nemotron_worker_1/task320_qwen_all_sft_mmlu_data_repair_linkage_s1 /work-agents/intern_nemotron_worker_1/Nemotron_task320 origin/main
git checkout 724ebecc971239f39daeb936bb48ec4bdc3aa52e -- workspace/tasks/task320_qwen_all_sft_mmlu_data_repair_linkage_s1
gh pr view 377 --json number,state,isDraft,baseRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 380 --json number,state,isDraft,baseRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr list --search "task319" --state all --json number,state,title,headRefName,headRefOid,baseRefName,mergeStateStatus,url --limit 20
python3 - <<'PY'
# Read task314 category deltas and row transitions from task-owned output.
PY
sed/rg over task308, task309, task316, and task319 docs/reports
```

No data materialization, packing, training, eval rerun, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, product-code
edit, main push, merge, or self-merge was performed.
