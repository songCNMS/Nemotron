# task329 raw-pass split and Qwen30B packing proof report

<!-- METADATA:STATUS=Working,DISPOSITION=PARTIAL_PASS_WITH_EXACT_BLOCKERS,SESSION=3 -->

## Disposition

`PARTIAL_PASS_WITH_EXACT_BLOCKERS`.

Task-owned Qwen3-30B packing artifacts were produced for the three allowed raw
pass sources, and the Qwen packed-data contract check passed. The artifact is
not ready for task310 training release because the proof surfaced exact
supervised-token and split-policy blockers:

- `task327-swe` packed 51,029 rows but has `supervised_tokens=0` under the
  tokenizer-native Qwen data-prep config. This source needs lead-approved
  source/config formatter remediation before it can count as supervised SFT.
- `task322 instruction-following-structured` had 6 validation-filtered rows in
  packing receipts. The packed artifact excludes those rows.
- Valid/test exposure is shard-ratio sparse: train exposes all three sources,
  but valid/test expose only `task322-agentic-interactive`.

## Artifact Root

- Run root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`
- Packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/packed_qwen_raw_pass_materialized`
- Splits root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/packed_qwen_raw_pass_materialized/splits`
- Final summary:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/final_summary.json`
  sha256 `3ac480ba65626882ca6233f60e7f55a3fc0f9e440aecece9daccdb2d57f8dbd6`
- Artifact checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/artifact_checksums.sha256`
  sha256 `953c3073c8aa3510289e05a4edc5e771b740a69702194b05b0c5285aeddd2bf5`;
  `sha256sum -c` passed for 22 entries.
- Packed shard checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/packed_shard_checksums.sha256`
  with 48 shard checksums.

## Source Matrix

Included sources only:

| Source | Prior task | Raw rows | Source sha256 | Row manifest sha256 | Decontam |
|---|---:|---:|---|---|---|
| `instruction-following-structured` | task322 | 4,969 | `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77` | `206e27cb006fce1321115dd68732531cf46f6d3eb7e2d385f0eb3a2e7bb4c7a7` | pass, 0 prompt/normalized/ngram hits |
| `agentic-interactive` | task322 | 19,028 | `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd` | `81f558b6cd08b9159402aab073283d9cee2898d0b83b23efd71a3a49e6160fbc` | pass, 0 prompt/normalized/ngram hits |
| `swe` | task327 | 51,029 | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` | `998a95f209d2863de50b115704493bc7406ce5f37046732f75ab737bc9fa7ab2` | pass, 0 prompt/normalized/ngram hits |

Excluded sources: all nine task327 `BLOCKED_DECONTAM_HIT` sources remained
excluded: `instruction-following-chat`, `competitive-cpp-00`,
`competitive-cpp-01`, `competitive-python-00`, `competitive-python-01`,
`math-proofs-lean`, `agentic-tool-calling`, `infinibyte-00`, `infinibyte-01`.

Source matrix artifact:
`/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/source_matrix.json`.

## Split And Packing Metrics

Qwen3-30B tokenizer/model path:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

Qwen contract validation:

- Command log:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/logs/qwen30b_contract_validate.log`
- Result: `QWEN30B_PACKED_CONTRACT=PASS`

Packed Parquet metrics:

| Split | Shards | Packed rows | Input tokens | Supervised tokens | Source exposure |
|---|---:|---:|---:|---:|---|
| train | 46 | 84,696 | 326,797,059 | 8,555,986 | all three sources |
| valid | 1 | 2,155 | 7,436,038 | 459,524 | agentic only |
| test | 1 | 2,194 | 7,616,762 | 475,355 | agentic only |
| total | 48 | 89,045 | 341,849,859 | 9,490,865 | three sources in train |

By source:

| Source | Shards | Packed rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `agentic-interactive` | 16 | 35,323 | 122,527,221 | 7,568,103 |
| `instruction-following-structured` | 16 | 2,693 | 10,307,854 | 1,922,762 |
| `swe` | 16 | 51,029 | 209,014,784 | 0 |

Receipt-level metrics distinguish pre-packing output sequences from final
Parquet rows:

- Total input rows: 75,026.
- Receipt output sequences: 91,315.
- Final packed Parquet rows: 89,045.
- `instruction-following-structured`: 4,969 input rows, 4,963 output sequences,
  2,693 packed rows, 6 validation-filtered rows.
- `agentic-interactive`: 19,028 input rows, 35,323 output sequences, 35,323
  packed rows, 0 filtered rows.
- `swe`: 51,029 input rows, 51,029 output sequences, 51,029 packed rows, 0
  filtered rows, 0 supervised tokens.

Metric artifacts:

- `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/qwen30b_packing_metrics.json`
  sha256 `f5f6674cc9617c85cd4b72ef9c827f2dfc8286be1e756974cfe8214ed14f210a`
- `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/packing_receipt_metrics.json`
  sha256 `f51befbb8d9ea28ecf1a8aaf2d25bde0525443abaaeeec7e4e10d4c4eecbfea7`

## Parity And Decontam

Intended-vs-exposed parity: `PASS` for shard target materialization. Expected
targets from `packed_qwen_raw_pass_materialized/blend.json` match exposed split
manifest target paths for train/valid/test with no missing or unexpected shards.

Split exposure note:

- `agentic-interactive`: train/valid/test exposed.
- `instruction-following-structured`: train exposed, valid/test absent.
- `swe`: train exposed, valid/test absent.

Decontam/no-AIME2025-train status:
`PASS_NO_AIME2025_TRAIN_ROWS_BY_PRIOR_DECONTAM_AND_SOURCE_EXCLUSION`.
All included sources have zero prompt-hash, normalized-prompt, and n-gram hits
against the heldout decontam corpus recorded by task322/task327. All nine
task327 decontam-hit sources are excluded.

Artifacts:

- `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/intended_vs_exposed_parity.json`
  sha256 `fe08a2b6c6f7db83fd9949b7333988418772fd8d56c75e2ef254d5d5ca0fc79d`
- `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/decontam_no_aime2025_train_proof.json`
  sha256 `b852dd99770c8df15911ed3528e724016187a45c267da9c5b0d37266ec427ebc`

## Commands And Environment

Environment:

- Branch:
  `intern_nemotron_worker_2/task329_qwen_all_sft_raw_pass_split_pack_proof_s1`
- Data-prep source base:
  `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Host: recorded in
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/manifests/command_env_manifest.json`
- Dependencies observed: `cosmos_xenna` import OK, `pyarrow 24.0.0`,
  `transformers 4.52.4`, `datasets 4.8.5`.

Initial attempt failed closed on the SWE HF-cache symlink target lacking a
`.jsonl` extension:

```bash
PYTHONPATH=src \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
WANDB_MODE=offline WANDB_DISABLED=true TOKENIZERS_PARALLELISM=false \
python3 src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml \
  blend_path="$RUN_ROOT/input/raw_pass_sources_blend.json" \
  output_dir="$RUN_ROOT/packed_qwen_raw_pass" \
  tokenizer.model=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  num_shards=16 pack_size=4096 train_ratio=0.98 valid_ratio=0.01 test_ratio=0.01 \
  used_in_filter=null force=true execution_mode=streaming sample=null seed=42 sample_seed=42
```

Retry succeeded after task-owned materialization/hardlinking of the three input
files:

```bash
PYTHONPATH=src \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
WANDB_MODE=offline WANDB_DISABLED=true TOKENIZERS_PARALLELISM=false \
python3 src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml \
  blend_path="$RUN_ROOT/input/raw_pass_sources_blend_materialized.json" \
  output_dir="$RUN_ROOT/packed_qwen_raw_pass_materialized" \
  tokenizer.model=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  num_shards=16 pack_size=4096 train_ratio=0.98 valid_ratio=0.01 test_ratio=0.01 \
  used_in_filter=null force=true execution_mode=streaming sample=null seed=42 sample_seed=42
```

Result: `rc=0`, 16 configured shards per source, `elapsed_sec=734`.

Evidence builder:

```bash
PYTHONPATH=src python3 \
  workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/build_task329_raw_pass_split_pack_proof.py
```

## Recommendation

Do not release task310 training from this artifact. Request independent review
of the partial raw-pass evidence, then a follow-up lead-gated remediation for:

1. SWE supervised-token mapping under tokenizer-native Qwen packing.
2. Six structured rows filtered by validation.
3. Per-source valid/test split policy if lead requires all-source validation
   exposure before a combined packed contract.

The produced raw-pass packed root is useful evidence, but it is not an accepted
expanded all-SFT training contract.

## Boundary Confirmation

No training, optimizer steps, nonzero-LR smoke, benchmark eval, export,
endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
shared mutation, main push, merge, or self-merge was performed.
