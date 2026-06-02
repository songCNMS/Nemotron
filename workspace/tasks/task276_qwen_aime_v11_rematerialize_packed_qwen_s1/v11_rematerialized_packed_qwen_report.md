# task276 V11 Rematerialized Packed Qwen Report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

Generated: 2026-06-02T03:54:00Z

Disposition: `PACKED_QWEN_READY_FOR_REVIEW`.

This is a no-training data/packing artifact report only. It does not authorize
SFT training, nonzero-LR smoke, live canary, AIME/task243 eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, main push, or
30B/8-GPU.

## Artifact Paths

- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/`.
- Run root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z`.
- Fresh packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
- Splits root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits`.
- Split manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits/manifest.json`.
- Packed metadata:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits/metadata.json`.
- Evidence manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_evidence_manifest.json`.
- Shard checksum list:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_shard_checksums.sha256`.

## Inputs

| Input | Path | sha256 |
| --- | --- | --- |
| task262 V11 blend plan | `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/v11_qwen_agentic_sft_blend_plan.json` | `2b3f0942eb04e077c5025c60be87355bf233b33085660a0b85a0b8b03b569e2a` |
| task262 manifest | `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/manifest.json` | `4c9874c9341b1e286533bd67eafa6a922567e905c9d3bb7bd78e8970eb777383` |
| task262 split audit | `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/split_materialization_audit.json` | `b2009b2c509620c5dde2412ee4dedf4efb8995431ef4bec4d353ba14dc3787b3` |
| task262 final-answer n-gram scan | `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/final_answer_ngram_decontam_scan.json` | `feffa6c677b1bc86b5f2f9ad8a8c3506582844cdb5b6a25bd8741322a9298370` |
| task246 heldout prompt hashes | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256` | `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d` |
| task246 heldout corpus | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl` | `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9` |

Task-owned DataBlend input:
`/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/input/v11_data_blend_agentic_sft_v0.json`
sha256 `859da9fb9d12c03d184152da12a9978072902f1390399d67391e885dabc47893`.

## Commands And Environment

Code revision used for artifact generation:
`745f78b9f1b6b42bb4018c3cf1544663f0e9f579`.

Execution was local only. No code was synced to `/root` or NemTron for this
task.

```bash
PYTHONPATH=src \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
WANDB_MODE=offline \
WANDB_DISABLED=true \
TOKENIZERS_PARALLELISM=false \
python3 src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml \
  blend_path=<run_root>/input/v11_data_blend_agentic_sft_v0.json \
  output_dir=<run_root>/packed_qwen \
  tokenizer.model=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  num_shards=16 \
  pack_size=4096 \
  train_ratio=0.98 \
  valid_ratio=0.01 \
  test_ratio=0.01 \
  force=true \
  execution_mode=streaming
```

Result: `DATA_PREP_RC=0`.

Qwen contract:

```bash
PYTHONPATH=src python3 - <<'PY'
from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract
validate_qwen_packed_sft_chat_contract(
    "<run_root>/packed_qwen/splits",
    tokenizer_model="/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507",
)
print("QWEN_PACKED_DATA_CONTRACT=PASS")
PY
```

Result: `QWEN_CONTRACT_RC=0`.

Targeted checks:

```bash
python3 -m py_compile src/nemotron/data_prep/utils/splits.py src/nemotron/recipes/super3/stage1_sft/qwen_chat_contract.py
PYTHONPATH=src pytest -q tests/data_prep/test_split_utils.py tests/recipes/super3/test_qwen_chat_contract.py
```

Results: `PY_COMPILE_RC=0`; `TARGETED_PYTEST_RC=0`, 26 passed.

## Split Counts

| Split | Exposed shards | Packed rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| train | 46 | 279 | 1,024,646 | 228,927 |
| valid | 1 | 1 | 1,491 | 1,428 |
| test | 1 | 0 | 0 | 0 |

Train source counts:

| Source | Shards | Packed rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942,062 | 167,555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75,305 | 54,821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 7 | 7,279 | 6,551 |

Valid source counts:

| Source | Shards | Packed rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 1 | 1 | 1,491 | 1,428 |

## Split Parity

Intended-vs-exposed multiset parity uses exact parquet target paths from
`blend.json` against resolved split symlink targets.

| Split | Expected shards | Actual exposed shards | Multiset parity |
| --- | ---: | ---: | --- |
| train | 46 | 46 | PASS |
| valid | 1 | 1 | PASS |
| test | 1 | 1 | PASS |

The Qwen packed-data contract also validated split materialization and passed.

## Qwen Chat Contract

Packed metadata records:

- tokenizer URI:
  `file:///mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
- `chat_template`: `tokenizer`;
- `chat_template_kwargs.enable_thinking`: `false`;
- `chat_template_kwargs.truncate_history_thinking`: `false`.

This confirms tokenizer-native Qwen chat-template packing with thinking
disabled.

## AIME Leakage Check

Fresh source scan over the three trainable JSONL inputs:

- AIME pattern mentions: 0;
- top-level label-like keys: 0;
- task246 user prompt-hash overlaps: 0;
- task246 system+user prompt-hash overlaps: 0.

Task262 final-answer scan evidence remains:

- final-answer n-gram blocker pairs: 0;
- final-answer blocked rows: 0;
- heldout prompt hash count: 560;
- task251 heldout eval rows: 0.

Decision: PASS for no AIME2025 prompt/label train leakage evidence.

## Checksums

| Artifact | sha256 |
| --- | --- |
| evidence manifest | `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee` |
| shard checksum list | `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312` |
| data prep log | `f6ffe9d392b87f54a8d8f1beb5a9b914df4eed6e3eca86c13c79d641910c1b49` |
| Qwen contract log | `0a65f9d6303f1042fdefc696d5d1ff760393e36f8b70caff6c3a63fe3be5d76b` |
| targeted pytest log | `8be8534a577f516df4925a1cbca172c35db69a04caf7a6670d4608af13933736` |
| packed `blend.json` | `6e64fdaf30582d5d0f6ed78f93759b86148ef21263e2a5d931dad62575234eef` |
| split `manifest.json` | `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5` |
| packed `metadata.json` | `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9` |

The shard checksum list contains all 48 actual parquet shard files.

## Residual Risk

The valid split is sparse: one hard-math packed row. This is a direct result of
the current shard-ratio split over sparse hard-math rows. It is reviewable and
passes parity/contract checks, but a later gate should decide whether a broader
validation distribution is needed before any no-training config/import preflight
or pilot launch.

## Boundary Confirmation

No SFT training, nonzero-LR smoke, live canary, AIME/task243 eval, export,
endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion, main
push, or 30B/8-GPU action was performed.
