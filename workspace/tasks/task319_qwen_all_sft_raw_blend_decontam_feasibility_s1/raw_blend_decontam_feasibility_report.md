# task319 Raw All-SFT Blend Decontam Feasibility Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Disposition

`PASS_FEASIBILITY_PLAN`.

The generic `stage1_sft/data_blend_raw` sources are feasible candidates for a
follow-up all-SFT repair path, but they are not packing-ready now. Current
task308/task309 evidence provides repo revisions and HF file checksums for all
12 raw source entries, while exact local row counts, row-level manifests,
decontam results, split exposure proof, Qwen chat-template packing proof, and
supervised-token counts remain missing for all 12.

Recommendation:
`LEAD_GATED_RAW_MATERIALIZE_COUNT_DECONTAM_THEN_SEPARATE_QWEN_PACKED_CONTRACT_TASK`.

Do not proceed directly to final packing or training. The follow-up task should
materialize the raw HF sources into a task-owned output root, count and hash the
exact rows/files, run fail-closed heldout/decontam scans, and only then hand off
to a separate Qwen packed-data contract task.

## Run Identity

- Worker branch:
  `intern_nemotron_worker_2/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1`
- PR: #383
  `https://github.com/songCNMS/Nemotron/pull/383`
- Branch base:
  `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Lead docs:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `724ebecc971239f39daeb936bb48ec4bdc3aa52e`
- Host:
  `lg-cmc-b7r201-n09u29-cpu-000191`
- Python:
  `/usr/bin/python3`
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/run_20260603T194128Z`
- Raw blend config:
  `src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json`
- Raw blend config sha256:
  `1c76013e66643972cfa1c96aca86571a666c81d7fd6cf95b024e081f0836503d`

## Evidence Reviewed

Task308:

- Report:
  `workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1/all_sft_pipeline_inventory_audit_report.md`
- Report sha256:
  `001154913dd28ffca20bdbe624ead7bf27c3bf4e27a95475e5f977db5cf97580`
- Decision:
  `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`
- Key finding: raw `stage1_sft/data_blend_raw` is eligible in principle, but
  exact row counts, decontam proof, Qwen packing proof, and supervised-token
  counts are not materialized.

Task309:

- Report:
  `workspace/tasks/task309_qwen_all_sft_packed_data_contract_s1/all_sft_packed_data_contract_report.md`
- Decision:
  `PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS`
- Immediate packed seed:
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`
- Task299 packed split manifest sha256:
  `3fd3fa7314d1e397bbff98cc9f5cb77e9973925e6d5914e410f14c42dc2f091b`
- Task299 packed metadata sha256:
  `e6aedb275e3505521ef5878647883bfb46aa8462830fdd742cefa3d59a6c0733`
- Key finding: constrained V11/task299 seed remains the only current
  packing-ready path; generic raw SFT remains excluded.

Task316 context from lead docs branch:

- Task316 planning direction records that after task310/task311, the next safe
  direction is data-blend plus validation/termination repair before any
  additional 30B training.
- Lead task316 context is docs/planning only and does not authorize action in
  task319.

## Source Matrix Summary

Task-owned source matrix:

- JSON:
  `/work-agents/intern_nemotron_worker_2/outputs/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/run_20260603T194128Z/matrices/source_matrix.json`
- JSON sha256:
  `894b2d6821094530ecded233bf9e54567f120df4c3c1ac024c978f2678eebe79`
- TSV:
  `/work-agents/intern_nemotron_worker_2/outputs/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/run_20260603T194128Z/matrices/source_matrix.tsv`
- TSV sha256:
  `9bf2ff2bf0821330659f89c9f7d08854e9d76b30f12ca1c507325a3756964dc1`

Summary counts:

| Item | Count |
|---|---:|
| Raw blend source entries | 12 |
| Sources with task308 repo revision | 12 |
| Sources with task308 HF file sha256 | 12 |
| Sources with exact local row count now | 0 |
| Sources with supervised-token count now | 0 |
| Missing/unpublished blend categories documented in config | 13 |
| Sources packing-ready now | 0 |

Important split note: `data_blend_raw.json` uses single-blend `datasets`
entries. The entries pin HF repo and optional subset/file stem, but do not pin
an explicit train/valid/test split in the registry. Before any future packing,
the materialization task must record the exact HF file path(s), split/config
selected by the downloader, row count, and checksum for each source.

## Source Matrix

| Source | Dataset | Subset | Weight | Revision | File sha256 | Current status |
|---|---|---|---:|---|---|---|
| `instruction-following-chat` | `nvidia/Nemotron-Instruction-Following-Chat-v1` | `chat_if` | 14.3 | `83dcd3aded0d289b0bbc018d3f9af4c5dd4005df` | `37f9ecc3c41dc5e97cfd6fca962a94afbc8713349900ea6f413c040df549ddb8` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `instruction-following-structured` | `nvidia/Nemotron-Instruction-Following-Chat-v1` | `structured_outputs` | 14.3 | `83dcd3aded0d289b0bbc018d3f9af4c5dd4005df` | `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `competitive-cpp-00` | `nvidia/Nemotron-Competitive-Programming-v1` | `competitive_coding_cpp.part_00` | 5.2 | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `1081e0a650ecdc02df1b4b8b4fecf4b3d39828908874b4bf1a4015e638005c62` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `competitive-cpp-01` | `nvidia/Nemotron-Competitive-Programming-v1` | `competitive_coding_cpp.part_01` | 5.2 | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `4500b6db059765aa6146d3c3247fdde1ce8b5cc762a7687ff4355b45e1701afa` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `competitive-python-00` | `nvidia/Nemotron-Competitive-Programming-v1` | `competitive_coding_python.part_00` | 5.2 | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `8314b37b7d42b32fb658c3be1fb974eb0814f44a856ccf2d90ec2d38856a7f5d` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `competitive-python-01` | `nvidia/Nemotron-Competitive-Programming-v1` | `competitive_coding_python.part_01` | 5.1 | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `988cc7a00686d6212b3f8fbef95919c8e72bbda81c9f859dd556df789bf44b30` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `swe` | `nvidia/Nemotron-SWE-v1` | none | 3.0 | `0fe17a965b297a9c943a59050a14c42d5f0083ce` | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `math-proofs-lean` | `nvidia/Nemotron-Math-Proofs-v1` | `lean` | 2.0 | `97229c590831adfe96202f5cd071d444d535bf91` | `b423525d35ad16c791863670cbad76b27d8463e2574770732e2cf5bf70661a2e` | Higher math heldout risk; block until materialized and stricter decontam passes. |
| `agentic-interactive` | `nvidia/Nemotron-Agentic-v1` | `interactive_agent` | 1.0 | `650d590978ca35c8f1ecea2faf136e5fac421b62` | `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `agentic-tool-calling` | `nvidia/Nemotron-Agentic-v1` | `tool_calling` | 1.0 | `650d590978ca35c8f1ecea2faf136e5fac421b62` | `f537a901d38a999627b8fe59e77a1007af0d79d71a892ad9a4a3d80456e5601b` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `infinibyte-00` | `nvidia/Nemotron-Competitive-Programming-v1` | `infinibyte.part_00` | 1.0 | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `7d6cc0943a9264696ba177f152fd12c60cc2e1b042787a205221abcd4059c9e7` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |
| `infinibyte-01` | `nvidia/Nemotron-Competitive-Programming-v1` | `infinibyte.part_01` | 1.0 | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `0124e374453dce8fa7a6e7ecd75356160f2bde525ba97b246d2b39e8479c4ef3` | Block until materialized, counted, decontam scanned, Qwen supervised-token counted. |

## Row, Checksum, And Supervised-Token Feasibility

Row-count feasibility:

- Current exact local row counts: `0/12`.
- Feasible in a follow-up by materializing each pinned HF file into a task-owned output
  root and writing a per-source manifest with exact file path, byte size,
  `wc -l`/JSONL parse count, first/last record IDs where available, and
  row-level content hashes.
- The future materialization task must not infer rows from HF file size alone.

Checksum feasibility:

- Current task308 HF file sha256 coverage: `12/12`.
- Required before packing: local materialized file sha256, row manifest sha256,
  source matrix sha256, and intended-vs-exposed split manifest sha256.
- Shared source locations must not be overwritten or deleted.

Supervised-token feasibility:

- Current supervised-token counts: `0/12`.
- Feasible in a follow-up only after Qwen tokenizer-native rendering with
  `chat_template: tokenizer`, `enable_thinking: false`, and the Qwen3-30B model
  tokenizer path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Future proof must count input tokens and supervised/loss-mask tokens by
  source and split before any training task.

## Decontam Corpus And Check Plan

Required heldout/decontam inputs:

| Input | Rows | sha256 |
|---|---:|---|
| `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl` | 560 | `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9` |
| `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256` | 560 | `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d` |

Minimum checks before any future raw blend packing:

1. Exact heldout prompt-hash exclusion against all trainable raw rows.
2. Normalized prompt and answer/label text exclusion for AIME2025/HMMT/MATH
   heldouts.
3. Token or word n-gram scan over prompt and assistant content, with a stricter
   threshold for `math-proofs-lean` and instruction-following rows.
4. Proof that AIME2025 prompts and labels appear only in heldout eval/decontam,
   never in trainable rows.
5. Proof that task255 artifacts are not reused.
6. Source-specific residual risk notes for SWE/code/tool datasets before any M1
   benchmark interpretation.

Fail-closed rule: any source with unresolved heldout hit, missing row count,
missing checksum, or missing supervised-token count must be excluded from the
future packed contract.

## Later Lead-Gated Command Plan

This task did not run the commands below. They are the smallest safe route for
a follow-up assignment.

```bash
# 1. Materialize raw sources into a task-owned output root.
export TASK_RAW_ROOT=/work-agents/intern_nemotron_worker_2/outputs/<future_task>/raw_materialized
export HF_HOME=/work-agents/intern_nemotron_worker_2/outputs/<future_task>/hf_cache
python <future_helper>.py materialize \
  --blend src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json \
  --output-root "$TASK_RAW_ROOT" \
  --expected-source-matrix <task319 source_matrix.json>

# 2. Count and checksum every materialized source.
python <future_helper>.py count-checksum \
  --input-root "$TASK_RAW_ROOT" \
  --emit-row-manifest \
  --fail-on-invalid-json

# 3. Run heldout/decontam checks.
python <future_helper>.py decontam \
  --input-root "$TASK_RAW_ROOT" \
  --heldout-corpus /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl \
  --heldout-prompt-hashes /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256 \
  --fail-on-hit

# 4. Only after decontam pass, run a separate Qwen packed-contract task.
python src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml \
  blend_path=<future_clean_blend.json> \
  output_dir=<future_packed_qwen_30b> \
  tokenizer.model=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  target_model_family=qwen \
  chat_template=tokenizer \
  'chat_template_kwargs={enable_thinking:false,truncate_history_thinking:false}'
```

Stop conditions for the follow-up task:

- Any source cannot be materialized into a task-owned root without shared
  mutation.
- Any source lacks exact row count or local checksum.
- Any heldout/decontam hit is unresolved.
- Any Qwen tokenizer/chat-template contract check fails.
- Any source lacks supervised-token counts by source and split.

## Commands Run For Task319

Read-only commands and task-owned artifact writes only:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout -B intern_nemotron_worker_2/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1 origin/main
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1
python3 task319 local source-matrix writer
sha256sum existing task246 heldout files and task299 packed manifest/metadata
sed/rg over task308/task309/task316 docs and stage1_sft data-prep code/configs
```

Artifact checksums:

| Artifact | sha256 |
|---|---|
| `manifests/artifact_checksums.sha256` | `1186ba59164480c2ce07a608441e9072e1efe06ee5f45e27819f78a19150c9cd` |
| `manifests/run_manifest.json` | `bf2a9e7354c2eca69ee03a713769b26de632dc4ef5a6915a12c2c02ee87f1bb1` |
| `manifests/missing_categories.json` | `7ba40ee1aab8d51cd06c3e340b5986d7ae54df45c65b3fc330628533c847ad6d` |
| `matrices/source_matrix.json` | `894b2d6821094530ecded233bf9e54567f120df4c3c1ac024c978f2678eebe79` |
| `matrices/source_matrix.tsv` | `9bf2ff2bf0821330659f89c9f7d08854e9d76b30f12ca1c507325a3756964dc1` |
| `logs/commands.log` | `4affc6b72a545702219c57cd36c34db701c43d3c974cd4dd04acf335a3035ffa` |

## Exact Blockers

- No exact local row counts for any of the 12 raw sources.
- No local materialized source file manifest for any of the 12 raw sources.
- No row-level checksums for any of the 12 raw sources.
- No decontam scan output for any of the 12 raw sources.
- No Qwen tokenizer-native supervised-token count for any of the 12 raw sources.
- No explicit train/valid/test split exposure manifest for the raw blend.
- Config documents 13 missing/unpublished blend categories; these cannot be
  included in any follow-up packing task without separate source contracts.

## Boundary Confirmation

Confirmed:

- No training or optimizer steps.
- No final packing.
- No benchmark eval.
- No export.
- No endpoint.
- No promotion or go/no-go claim for a model.
- No task255 reuse.
- No AIME2025 prompts or labels used as train data.
- No large/shared dataset mutation.
- No shared deletion, including under `/mnt/cephfs/data/processing/lei.song`.
- No main push.
- No merge or self-merge.
