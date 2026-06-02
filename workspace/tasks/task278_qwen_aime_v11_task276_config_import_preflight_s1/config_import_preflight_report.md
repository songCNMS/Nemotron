# task278 Config/Import Preflight Report

Generated: 2026-06-02T04:49:41.546401Z

Disposition: `CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE`.

This is a no-training config/import preflight artifact. It does not
authorize training, nonzero-LR smoke, live canary, AIME/task243 eval,
export, endpoint, promotion, task255 reuse, AIME2025 train data, shared
deletion, main push, merge, or 30B/8-GPU.

## Result

- Local packed-data readability: PASS.
- Qwen packed/training contract checks: PASS.
- Qwen HF config/tokenizer import: PASS.
- Full Megatron-Bridge training-stack import: BLOCKED.
- Blocker: `ModuleNotFoundError: No module named 'megatron'`.

## Artifact Paths

- Output root: `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1`.
- Run root: `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T044941Z`.
- Manifest: `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T044941Z/evidence/task278_config_import_preflight_manifest.json`.
- Report: `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T044941Z/evidence/task278_config_import_preflight_report.md`.
- Task276 packed root: `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
- Task276 splits root: `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits`.

## Config Payload

- Train entrypoint checked but not executed: `/work-agents/intern_nemotron_worker_2/Nemotron/src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py`.
- Config path: `/work-agents/intern_nemotron_worker_2/Nemotron/src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`.
- Packed data env: `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits`.
- Qwen model/tokenizer env: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Training profile: `qwen`.
- Train settings if launched: `{'train_iters': 1700, 'global_batch_size': 4, 'micro_batch_size': 1}`.
- Scheduler settings if launched: `{'lr_warmup_iters': 4}`.
- Checkpoint settings if launched: `{'save': '../output/super3/m1_agentic_sft_v0/checkpoints', 'load': None, 'save_interval': 20, 'pretrained_checkpoint': '/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507', 'finetune': True}`.
- Guard: training command was not executed because it would enter the
  Megatron-Bridge finetune path.

## Packed Data Readability

| Split | Shards | Rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

Sparse valid/test disposition: accepted for preflight only. Valid has
one packed row; test has one exposed shard and zero rows. This does not
authorize training or evaluation.

## Qwen Import

- HF import status: `PASS`.
- Model type: `qwen3`.
- Config class: `Qwen3Config`.
- Tokenizer class: `Qwen2TokenizerFast`.
- Safetensor index shards exist: `True`.

## Runtime Import Probes

- `nemo`: FAIL `ModuleNotFoundError: No module named 'nemo'`.
- `nemo.collections.llm`: FAIL `ModuleNotFoundError: No module named 'nemo'`.
- `megatron`: FAIL `ModuleNotFoundError: No module named 'megatron'`.
- `megatron.bridge`: FAIL `ModuleNotFoundError: No module named 'megatron'`.
- `megatron.bridge.training.config`: FAIL `ModuleNotFoundError: No module named 'megatron'`.
- `megatron.bridge.recipes.qwen.qwen3`: FAIL `ModuleNotFoundError: No module named 'megatron'`.
- `nemotron.recipes.super3.stage1_sft.train`: FAIL `ModuleNotFoundError: No module named 'megatron'`.

## Checksums

- Evidence manifest sha256: `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee`.
- Shard checksum list sha256: `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312`.
- Split manifest sha256: `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5`.
- Metadata sha256: `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9`.
- Qwen config.json sha256: `5beea1a4a34c62782bfb2f911c606741a3bab8f92d80a118fa053c28af12e8ba`.
- Qwen tokenizer.json sha256: `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`.
- Qwen model.safetensors.index.json sha256: `d6c42883a895dfef5b0080ed2116a1bcd764f558406b98923d675978a1abf29c`.

The manifest contains full safetensors shard sizes and sha256 values.

## Next Remediation

Run the same no-training helper or an equivalent Bridge import preflight
inside a task-owned NemTron/NeMo/Megatron-Bridge runtime where
`megatron.bridge.training.config` and the Qwen Bridge recipe import.
Do not run `qwen_local_train.py` or `run_finetune`; the next proof should
stop after config/dataset/checkpoint import and fail-closed guards.

## Boundary Confirmation

No training loop, optimizer step, checkpoint save from training, export,
endpoint, live canary, AIME/task243 eval, promotion, task255 reuse,
AIME2025 train data, shared deletion, main push, merge, or 30B/8-GPU
action was performed.
