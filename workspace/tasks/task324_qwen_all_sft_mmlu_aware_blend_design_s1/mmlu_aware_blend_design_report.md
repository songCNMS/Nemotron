# task324 MMLU-aware all-SFT blend design report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=96 -->

Generated: 2026-06-03T20:36:54Z

## Disposition

Recommendation: `APPROVE_BLEND_DESIGN`.

Task324 defines a docs-only MMLU-aware all-SFT blend contract for a later
lead-gated packed-data task. The design consumes task314's row/category
forensics, task320's data-repair linkage, and task319's raw-source feasibility
matrix. It does not treat any raw source as packing-ready yet: task319 found
all 12 raw sources are feasible candidates, but `0/12` currently have exact
local rows, row manifests, decontam results, split exposure proof, Qwen
supervised-token counts, or packing proof.

The key design principle is fail-closed balance: keep the proven task299/V11
seed as a continuity component, but require materialized, decontaminated,
Qwen-rendered coverage for MMLU-Pro non-math retention buckets before any
future all-SFT repair training.

No data materialization, final packing, training, eval rerun, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, product-code
edit, main push, merge, or self-merge was performed.

## Reviewed evidence

| Evidence | State used by task324 |
|---|---|
| task314/#380 | `OPEN`, base `main`, `CLEAN/MERGEABLE`, head `8760ddb515324db6625d7f3a36069d6e0c064029`; task314 found MMLU-Pro `-2` is real answer-choice drift. |
| task314 outputs | `/work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z`; category deltas and row-transition tables. |
| task320/#381 | `OPEN`, base `main`, `CLEAN/MERGEABLE`, head `4131915f14acb4ff551ae6cf3f2325a67cf89945`; accepted as linkage docs/no-action-release. |
| task319/#383 | `OPEN`, base `main`, head `802a796d77144a7fdfc56477fdd001b574e90568`; task319 report recommends raw materialize/count/decontam before any pack contract. |
| task319 source matrix | `/work-agents/intern_nemotron_worker_2/outputs/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/run_20260603T194128Z/matrices/source_matrix.json`, sha256 `894b2d6821094530ecded233bf9e54567f120df4c3c1ac024c978f2678eebe79`. |
| task322 assignment/local probes | Task322 docs and HF metadata resolution artifacts exist locally, but no task322 PR/final materialization report was visible during this review. Treat as pending dependency. |
| task308/task309 | Current accepted training seed is constrained task299/V11 only; generic raw `stage1_sft/data_blend_raw` remains excluded until materialized/count/decontam/Qwen-packed. |

Task314 MMLU-Pro summary:

| Metric | Value |
|---|---:|
| Base | `6758/12032 = 0.5616688829787234` |
| FT | `6756/12032 = 0.5615026595744681` |
| Net delta | `-2` |
| Loss/gain rows | `92` base-correct to FT-wrong, `90` base-wrong to FT-correct |
| Non-math aggregate | `-15` |
| Math delta | `+13` |
| Loss rows outside math | `86/92` |

## MMLU retention buckets

Task320 defined six retention buckets. Task324 turns them into blend-contract
fields:

| Bucket | Protected MMLU-Pro categories | Task314 signal | Contract interpretation |
|---|---|---:|---|
| Physical sciences | physics, chemistry | `-9` combined | Highest-priority repair coverage. |
| Bio-health | biology, health, psychology | `-6` combined | High-priority retention coverage. |
| Humanities/social | history, philosophy, economics, business, law | mixed, net `0` but history/business down | Preserve breadth and prevent aggregate masking. |
| Technical/coding | computer science, engineering | `+2` engineering, CS flat, high churn | Preserve without letting code dominate the blend. |
| Math | math | `+13` | Preserve gain; cap math-only expansion unless non-math buckets are covered. |
| Broad instruction/other | other and general instruction coverage | `-2` | Broad retention coverage and cross-domain smoothing. |

Required later reporting fields for every source and split:

- `source_name`, `dataset_id`, `subset_or_file`, `revision`, `license`;
- `mmlu_bucket_primary` and optional `mmlu_bucket_secondary`;
- `materialized_path`, `file_sha256`, `row_manifest_sha256`;
- `rows`, `input_tokens`, `supervised_tokens`;
- `train_rows`, `valid_rows`, `test_rows`;
- `heldout_exact_prompt_overlaps`, `heldout_ngram_overlaps`;
- `aime2025_prompt_label_train_rows`, `task255_reuse`;
- `include_status` with `include`, `exclude`, or `blocked` and exact reason.

## Source-to-bucket mapping

The mappings below are design labels, not inclusion approval. A future task322
or successor materialization task must prove exact rows, checksums, decontam,
and Qwen supervised-token counts before a source may be packed.

### Raw task319 sources

| Source | Weight | Primary bucket | Secondary bucket | Design status |
|---|---:|---|---|---|
| `instruction-following-chat` | `14.3` | Broad instruction/other | Humanities/social, bio-health, physical sciences if content classifier proves coverage | Candidate anchor for non-math breadth; must be bucket-classified after materialization. |
| `instruction-following-structured` | `14.3` | Broad instruction/other | Technical/coding | Candidate for structured-answer retention; not a substitute for science coverage. |
| `competitive-cpp-00` | `5.2` | Technical/coding | Math, engineering | Candidate for technical retention; high code dominance risk. |
| `competitive-cpp-01` | `5.2` | Technical/coding | Math, engineering | Same as above; combine with cpp-00 for caps. |
| `competitive-python-00` | `5.2` | Technical/coding | Math, engineering | Candidate for code/problem solving; cap if non-math knowledge buckets are under-covered. |
| `competitive-python-01` | `5.1` | Technical/coding | Math, engineering | Same as above; combine with python-00 for caps. |
| `swe` | `3.0` | Technical/coding | Broad instruction/other | Candidate for SWE/M1 retention; not direct MMLU factual coverage. |
| `math-proofs-lean` | `2.0` | Math | Technical/coding | Candidate to preserve math gain; highest math-heldout decontam risk. |
| `agentic-interactive` | `1.0` | Broad instruction/other | Technical/coding | Candidate for agentic breadth; not direct MMLU category coverage without labels. |
| `agentic-tool-calling` | `1.0` | Broad instruction/other | Technical/coding | Candidate for tool-use retention; not direct MMLU category coverage without labels. |
| `infinibyte-00` | `1.0` | Technical/coding | Broad instruction/other | Candidate for technical/general data; require bucket classification. |
| `infinibyte-01` | `1.0` | Technical/coding | Broad instruction/other | Same as above. |

### Missing/unpublished config categories

Task319 also recorded 13 configured categories without source contracts. They
must remain excluded until a separate source contract exists. The most relevant
gaps for task314 are:

| Missing category | Config weight | Bucket impact |
|---|---:|---|
| `science` | `12.8` | Directly maps to physical sciences and bio-health; this is the largest missing retention gap. |
| `math` | `9.9` | Math gain preservation, but must not crowd out non-math buckets. |
| `math-w-tools` | `4.9` | Math/tool blend; high decontam scrutiny. |
| `genselect-financial` | `3.0` | Humanities/social, economics, business. |
| `multilingual` | `7.4` | Broad instruction/other; only include if later source contract exists. |
| `long-context`, `low-effort-reasoning`, `terminal-use`, `agentic-programming`, `sql`, `cuda`, `search`, `safety` | `0.5` to `2.0` | Auxiliary breadth/technical coverage; blocked until source contracts exist. |

Design implication: if the future task322 path can only materialize the 12
task319 sources, the packed-contract task must explicitly report that the
`science` category remains absent. It may still proceed as a partial blend only
if lead accepts that physical-science retention is being approximated through
instruction-following and generic sources rather than direct science data.

### Task299/V11 seed sources

| Source | Current packed rows | Primary bucket | Role in MMLU-aware blend |
|---|---:|---|---|
| `m1-agentic-sft-v11-from-m0` | `244` | Broad instruction/other | Continuity seed; can also support technical/coding and math sub-environments, but not accepted as MMLU category retention proof. |
| `m1-agentic-sft-v11-math-final-answer` | `28` | Math | Preserve task314 math gain; cap unless non-math buckets have proven coverage. |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | `7` | Math | Preserve hard-math behavior; sparse and high-risk if over-weighted. |

The task299 seed should be included as a reviewed continuity component, but the
future blend must not be called MMLU-aware unless raw sources add non-math
bucket coverage with exact counts and decontam proof.

## Blend contract design

### Inclusion gates

A source may be included in a later packed contract only if all are true:

1. Local materialized file exists in a task-owned output root.
2. File sha256 matches the expected HF/LFS checksum or an explicit reviewed
   replacement checksum.
3. Exact JSONL row count and row-manifest sha256 are emitted.
4. Rows are mapped to one primary MMLU retention bucket.
5. Exact prompt-hash and n-gram decontam pass for AIME2025/HMMT/MATH/MMLU-Pro.
6. AIME2025 prompt/label train rows are `0`.
7. Task255 reuse is `false`.
8. Qwen tokenizer-native render succeeds with supervised-token counts.
9. Train/valid/test split exposure is declared and nonempty where required.
10. Any blocked source is excluded from the pack plan rather than silently
    replaced by math/task299 rows.

### Bucket balance requirements

For a later packed-contract report, require these fail-closed minimums:

| Requirement | Minimum evidence |
|---|---|
| Physical sciences | Nonzero rows and supervised tokens, or explicit lead-accepted blocker. |
| Bio-health | Nonzero rows and supervised tokens, or explicit lead-accepted blocker. |
| Humanities/social | Nonzero rows and supervised tokens, with business/economics/law/history coverage tagged where possible. |
| Technical/coding | Nonzero rows and supervised tokens, but capped if physical-science or bio-health coverage is missing. |
| Math | Keep task299 math seed and any clean raw math source, but report math percentage and cap if non-math aggregate coverage is deficient. |
| Broad instruction/other | Nonzero rows and supervised tokens from instruction-following and/or agentic sources. |

Concrete reporting ratios:

- `math_supervised_token_pct`;
- `non_math_supervised_token_pct`;
- `physical_science_supervised_token_pct`;
- `bio_health_supervised_token_pct`;
- `technical_coding_supervised_token_pct`;
- `broad_instruction_other_supervised_token_pct`;
- `task299_seed_supervised_token_pct`.

Fail condition: if `math_supervised_token_pct` increases versus task299 while
physical-science or bio-health coverage remains zero/blocked, the design is
not a valid repair for task314's MMLU-Pro regression.

### Split requirements

The current task299 seed has `279` train rows, `1` valid row, and `0` test rows.
The MMLU-aware blend must improve split evidence:

- train split reports rows/tokens by source and bucket;
- valid split has at least one row per included bucket;
- test or heldout-audit split is nonempty for pack integrity checks;
- intended-vs-exposed source multiset parity passes;
- no valid/test row is counted as trainable output;
- split assignment is deterministic and included in the checksum manifest.

## How to consume task322 outputs

Task324 expects task322 or a successor task to produce:

- `source_inventory.json`;
- `source_resolution.tsv`;
- one local materialized file per included source;
- `row_manifest.jsonl` or per-source row manifests;
- `decontam_manifest.json`;
- `heldout_overlap_summary.json`;
- `qwen_render_token_counts.json`;
- `split_plan.json`;
- checksum manifest covering all files above.

The later packed-contract task should consume task322 outputs as follows:

1. Load task322's accepted source inventory.
2. Drop every source with `include_status != include`.
3. Drop every source missing exact rows, local sha256, row manifest, decontam
   pass, or Qwen supervised-token counts.
4. Build `clean_blend.json` only from included sources and task299 continuity
   seed.
5. Emit the MMLU bucket balance table before packing.
6. Run Qwen packing and then re-emit the same bucket table from exposed packed
   shards.
7. Fail if intended-vs-exposed bucket counts differ.

If task322 remains metadata-only or partial, the later packed-contract task
must either run on a fully proven subset with explicit exclusions or stop. It
must not infer row counts from HF metadata size and must not use raw sources
without decontam proof.

## Later same-harness evaluation constraints

No evaluation is authorized here. If a later training task is separately
authorized, the evaluation gate must use task311/task314 same-harness standards:

| Metric | Required result |
|---|---|
| MMLU-Pro aggregate | FT `>=` base on the same row set and parser. |
| MMLU-Pro non-math aggregate | FT `>=` base; no repeat of task314 non-math `-15`. |
| Physical sciences | Must not repeat physics/chemistry combined `-9`. |
| Bio-health | Must not repeat biology/health/psychology combined `-6`. |
| Math | Preserve or exceed prior math gain without masking non-math losses. |
| AIME2025 | FT `>=` base; prompts/labels remain heldout only. |
| HMMT | FT `>=` base; prompts/labels remain heldout/decontam only. |
| Parser/protocol | Same prompt variant, parser, endpoint manifests, row manifests, completion logs, cleanup proof. |

Promotion stop condition: if MMLU-Pro aggregate is below base, or if MMLU-Pro
non-math aggregate is below base despite math gains, do not promote and do not
claim a repaired all-SFT blend.

## Residual risks

1. Task319 proves feasibility only; none of the 12 raw sources is packing-ready.
2. Task322 final materialization/decontam evidence was not visible as an
   accepted PR during this review; local metadata resolution artifacts are not
   enough for packing.
3. The highest-priority missing category is `science`, which maps directly to
   task314's physical-science and bio-health losses but has no contracted raw
   source in the 12 task319 entries.
4. Task299/V11 seed is valid but narrow and math/agentic-heavy; it should not
   be expanded as a substitute for non-math retention coverage.
5. Any future classifier-based bucket mapping can misclassify examples unless
   reviewed with source samples and bucket-level manifests.
6. All future decontam must include MMLU-Pro row-manifest prompt/problem hashes
   in addition to AIME2025/HMMT/MATH heldouts.

## Commands and environment

Worktree:
`/work-agents/intern_nemotron_worker_1/Nemotron_task324`.

Base:
`origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`.

Lead docs:
`origin/intern_nemotron_lead/session1-recovery-task-docs`
`7055dac63c772ac8a317454bffead4a469a0112f`.

Read-only commands:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git worktree add -b intern_nemotron_worker_1/task324_qwen_all_sft_mmlu_aware_blend_design_s1 /work-agents/intern_nemotron_worker_1/Nemotron_task324 origin/main
git checkout 7055dac63c772ac8a317454bffead4a469a0112f -- workspace/tasks/task324_qwen_all_sft_mmlu_aware_blend_design_s1
gh pr view 380 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 381 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 383 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git fetch origin intern_nemotron_worker_2/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1
git show origin/intern_nemotron_worker_2/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1:workspace/tasks/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/raw_blend_decontam_feasibility_report.md
python3 - <<'PY'
# Read task319 source matrix, task314 category deltas, and task322 local metadata resolution artifacts.
PY
sed/rg over task308, task309, task320, task322 docs and reports
```

No data materialization, final packing, training, eval rerun, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, product-code
edit, main push, merge, or self-merge was performed.
