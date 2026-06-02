# task283 Bridge Runtime Remediation Preflight Report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Disposition

`CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`.

This is a no-training runtime remediation/config-import preflight PASS for
Qwen3-4B V11. It is not an `AutoBridge.import_ckpt` checkpoint-load proof, not
a training clearance, not a task243/AIME eval clearance, not promotion, and not
30B/8-GPU clearance.

## Artifact Roots

- Local output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`
- Remote run root:
  `/root/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`
- Remote repo sync:
  `/root/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z/Nemotron`
- Remote venv:
  `/root/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z/venv`
- Task276 input copy used on NemTron:
  `/root/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z/task276_input/packed_qwen`
- Qwen3-4B HF model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

## Runtime Reconciliation

Coordinator Session 40 positive evidence remains valid read-only context:

- Evidence root:
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`
- `bridge_import_probe.log` sha256:
  `170b51d0c846c374a82badf780d478d64a946d3131cdc7032808d7c53db21756`
- `fail_closed_preflight.log` sha256:
  `60db59059560304dc18a6e28498f6be1a08cbc24c26abd6e82241f6e1729c440`
- `symbol_preflight.log` sha256:
  `bfa15c5b26849ef2c802c03b0303d57ada11922c4872068bd17de2c7d0081534`
- `remote_checkpoint_manifest.txt` sha256:
  `51b4ab937a5be23f1391cddd5c5c1425a3f8860e84fe81827fc5ebdee2afb522`

Fresh task283 probing showed why task278 and Session 40 differed:

- CPU worker host still lacks the runtime route.
- `NemTron` host has `nemo`, `megatron.bridge`,
  `megatron.bridge.training.config`, and `AutoBridge.import_ckpt`.
- The fresh `NemTron` route initially failed importing
  `megatron.bridge.recipes.qwen.qwen3` because `megatron.energon` was
  missing.
- A task-owned venv with `--system-site-packages` plus targeted `--no-deps`
  support-package installs was enough for `QWEN_RECIPE_IMPORT=PASS`.

The remote `synced_head.txt` contains `fatal: not a git repository` because
the repo was copied by tar over SSH with `.git` excluded. The source branch head
before sync was recorded locally as
`c1d988e29abafa51a9c3f83a98e21b229135f97e`. The following PR/report commits are
docs/status only.

## Remediation Packages

Installed only into the task-owned venv, not system site packages:

- `megatron-energon==7.3.2`
- `multi-storage-client==0.49.0`
- `xattr==1.3.0`
- `bracex==2.6`
- `wcmatch==10.1`
- `braceexpand==0.1.7`
- `rapidyaml==0.13.0.post2`
- `deprecation==2.1.0`
- `filetype==1.2.0`
- `webdataset==1.0.2`

Base runtime packages observed:

- `nemo-toolkit==2.7.3`
- `megatron-bridge==0.3.0rc0`
- `torch==2.9.1+cu129`
- `transformers==4.57.1`
- `safetensors==0.7.0`
- `pyarrow==23.0.0`
- `omegaconf==2.3.0`

`venv_pip_check.log` returns rc `1`; residual missing packages include
`nvidia-resiliency-ext`, `hydra-core`, `lightning`, and other NeMo/Bridge
extras. The config/import preflight passed despite those missing packages, but
this remains a blocker for any future full training CLI import/launch unless a
separate lead-cleared task remediates it.

## Commands

Representative commands run:

```bash
tar --exclude .git -C /work-agents/intern_nemotron_worker_2/Nemotron -cf - . \
  | ssh NemTron "rm -rf '${REMOTE_RUN}/Nemotron' && mkdir -p '${REMOTE_RUN}/Nemotron' && tar -C '${REMOTE_RUN}/Nemotron' -xf -"
ssh NemTron "python3 -m venv --system-site-packages '${REMOTE_RUN}/venv'"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps megatron-energon==7.3.2"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps multi-storage-client==0.49.0"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps xattr==1.3.0"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps bracex==2.6 wcmatch==10.1"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps braceexpand==0.1.7"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps rapidyaml==0.13.0.post2"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps deprecation==2.1.0"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps filetype==1.2.0"
ssh NemTron "${REMOTE_RUN}/venv/bin/python -m pip install --no-deps webdataset==1.0.2"
tar -C /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z -cf - packed_qwen evidence \
  | ssh NemTron "mkdir -p '${REMOTE_RUN}/task276_input' && tar -C '${REMOTE_RUN}/task276_input' -xf -"
```

The final preflight ran a remote inline Python script with:

```bash
PYTHONPATH=${REMOTE_RUN}/Nemotron/src
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
SUPER3_M1_AGENTIC_PACKED_DIR=${REMOTE_RUN}/task276_input/packed_qwen/splits
SUPER3_M1_TRAINING_PROFILE=qwen
SUPER3_M1_PRETRAINED_CHECKPOINT=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
```

It imported runtime symbols, loaded Qwen HF config/tokenizer, read the task276
packed shards, validated Qwen packed/training contracts, and called
`_qwen_local_recipe_builder` to build a `ConfigContainer`. It did not call
`qwen_local_train.py`, `run_finetune`, `AutoBridge.import_ckpt`, or any export
or eval entrypoint.

## Preflight Results

Final manifest:

`/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z/manifests/task283_no_training_config_import_manifest.json`

Final manifest sha256:

`eaf06f61daa5c24e55d94f307abdc02f7870b3ea65d0edfa497625e58bc95ffd`

Final log:

`/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z/logs/no_training_config_import_preflight.log`

Final log sha256:

`e62a06d815cc0a5f6fbdffd71f6e32668cb02c35b532718eeda2cb5329e790e4`

Result summary:

- Disposition: `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`
- Fail-closed preflight: `PASS`
- Qwen HF config/tokenizer import: `PASS`
- Qwen packed chat contract: `PASS`
- Qwen training pipeline contract: `PASS`
- Qwen recipe config build: `PASS`, `ConfigContainer`
- Config values built but not executed: `train_iters=1`,
  `global_batch_size=1`, `tensor_model_parallel_size=2`,
  `pipeline_model_parallel_size=1`, `seq_length=4096`

Runtime imports:

- `nemo`: `PASS`
- `megatron.bridge`: `PASS`
- `megatron.bridge.training.config`: `PASS`
- `megatron.bridge.recipes.qwen.qwen3`: `PASS`
- `megatron.energon`: `PASS`
- `nemotron.recipes.super3.stage1_sft.qwen_local_train`: `PASS`
- `nemo.collections.llm`: `FAIL`, `ModuleNotFoundError: No module named 'lightning'`
- `nemotron.recipes.super3.stage1_sft.train`: `FAIL`,
  `ModuleNotFoundError: No module named 'nvidia_resiliency_ext'`

Task276 packed data counts observed on `NemTron`:

| Split | Parquet entries | Rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

Task276 input checksums:

- split manifest:
  `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5`
- metadata:
  `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9`
- evidence manifest:
  `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee`
- shard checksum list:
  `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312`

Artifact inventory sha256:

`c524c25f91ca0e417b7e84e62ca890b4069d6957f066990799d51ba477a6c9b1`

## Boundary Confirmation

No training loop, optimizer step, checkpoint save, `AutoBridge.import_ckpt`,
export, endpoint, live canary, AIME/task243 eval, promotion, task255 reuse,
AIME2025 train data, shared deletion, main push, merge, or 30B/8-GPU action was
performed.

The no-side-effect probe confirmed these paths were absent:

- `${REMOTE_RUN}/guard_no_training_checkpoints_not_created`
- `${REMOTE_RUN}/qwen3_4b_bridge_import_iter0`
- `${REMOTE_RUN}/hf_export`
- `${REMOTE_RUN}/endpoint`

No file under `/mnt/cephfs/data/processing/lei.song` was deleted or overwritten.

## Residual Risk

- No `AutoBridge.import_ckpt` or checkpoint-load/save proof was run because the
  current task lead request required proof that no checkpoint save occurred.
- The task-owned venv is a minimal remediation for config/import preflight, not
  a complete training environment. `pip check` remains rc `1`.
- Full stage1 training module import still fails on missing
  `nvidia_resiliency_ext`; `nemo.collections.llm` still fails on missing
  `lightning`.
- Task276 remains sparse for validation/test: valid has one packed row and test
  has zero rows.
- Any future training, checkpoint import/load proof, live eval, export,
  endpoint, promotion, task243 comparison, AIME train-data use, or 30B/8-GPU
  action requires a separate lead-cleared task.
