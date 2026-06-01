# task262 V11 Data Split And Sidecar Repair Report

<!-- METADATA:SESSION=1 -->

## Scope Boundary

No training, export, endpoint launch, AIME/task243 eval, promotion, 30B/8-GPU
work, task255 checkpoint/export reuse, AIME2025 train data use, or shared
deletion was performed.

## Code Repair

- `src/nemotron/data_prep/utils/splits.py`: split materialization now preserves
  unique shard identity. Old basename links are kept only when basenames are
  unique; colliding basenames receive dataset-qualified parquet link names.
  Missing requested shards fail closed for every split, and
  `splits/manifest.json` records intended and created split entries.
- `src/nemotron/recipes/super3/stage1_sft/qwen_chat_contract.py`: the Qwen
  packed-data contract now resolves `blend.json` and compares intended parquet
  targets against exposed split directory targets as multisets before training
  can start.
- Tests cover colliding basename materialization and a pre-task262 incomplete
  split that must be rejected.

## Inspected Inputs

- task253 packed Qwen root:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen`
- task253 `blend.json`:
  `963ad31c2265eaf9f10fdd261eb73705e72b83fbc0fff2b00f49891bfcbb0520`
- task253 `splits/metadata.json`:
  `18a83f43bdecaed886bd115945e3b767c99479bf6dafae20be544e21b36afac3`
- task253 shard summary:
  `03d1e72da96c6c10528f8a218cca3e20b461268daae35b4388d566249705f040`
- task253 packing config:
  `e4d6edbb8fb9d10353c1abdd6162b4ddd4b1e68aae9aeac6569a0f3cd2a5f43f`
- task251 M1 manifest:
  `3f367930cd9ddbb568f6ff75bebe3aa2b339332b1e56bd2533ce315cfbbf53ba`
- task246 heldout prompt hashes:
  `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`

## Split Audit

| Split | Intended shards | Exposed shards | Intended rows | Exposed rows | Intended input tokens | Exposed input tokens | Intended supervised tokens | Exposed supervised tokens | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| train | 15 | 8 | 113 | 79 | 835223 | 596944 | 156569 | 110945 | MISMATCH |
| valid | 1 | 1 | 15 | 15 | 115993 | 115993 | 18998 | 18998 | MATCH |

The task253 train split is missing 7 intended target shards: 2 M0/general shards
and 5 hard-math sidecar shards. V11 must repack or rematerialize with the
task262 collision-safe split logic before any training.

## V11 Sidecar Plan

Task-owned plan artifact:
`/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/v11_qwen_agentic_sft_blend_plan.json`

| Dataset | Rows | Weight | SHA256 |
|---|---:|---:|---|
| base M0 agentic train | 1100 | 1.0 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` |
| hard-math verified full solution | 8 | 1.0 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` |
| math final-answer | 200 | 1.0 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` |

The V11 plan includes all reviewed hard-math rows and makes final-answer
supervision explicit instead of preserving task251's `sidecar_in_blend=false`
state. The plan is not a training run and needs a later V11 pilot gate before
packing/training.

## Decontamination Status

- Heldout corpus rows: 560; heldout prompt hashes: 560.
- task251 `agentic_sft_v0_math_heldout_eval.jsonl` rows: 0.
- Exact task246-style heldout prompt-hash overlaps:
  base train 0, hard-math 0, final-answer 0.
- No top-level label-like keys were found in reviewed trainable JSONL rows.
- Residual evidence gap: task262 did not rerun a full n-gram contamination
  scanner for final-answer rows; the next data-prep gate should either accept
  task251 row metadata plus exact-overlap evidence or rerun that scanner before
  training.

## Output Artifacts

- `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/split_materialization_audit.json`
- `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/v11_qwen_agentic_sft_blend_plan.json`
- `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/task251_source_summaries.json`
- `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/task262_v11_data_split_sidecar_report.md`
- `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/manifest.json`

## Checks

- `python -m py_compile src/nemotron/data_prep/utils/splits.py src/nemotron/recipes/super3/stage1_sft/qwen_chat_contract.py`
- `PYTHONPATH=src pytest -q tests/data_prep/test_split_utils.py tests/recipes/super3/test_qwen_chat_contract.py`
- `git diff --check`

Global Qwen AIME gate remains NO-GO/HOLD.
