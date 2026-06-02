# task298 30B Runtime/Resource/Base-Load Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Disposition

`PASS_RUNTIME_RESOURCE_BASE_LOAD_GATE_WITH_TRAINING_LAUNCH_RESIDUALS`.

The current 30B route is proven enough for lead review of later 30B data,
base-test planning, and training-task planning: the exact Qwen3-30B-A3B-Instruct
HF path exists, current-main 30B Qwen3-MoE config/import preflight passed on a
NemTron H200 host, and a task-owned Bridge import wrote an iteration-0 Megatron
checkpoint from the 30B HF model with `BRIDGE_IMPORT_RC=0`.

This is not training, testing, promotion, export clearance, endpoint clearance,
or 30B task launch clearance.

## Run Identity

- Task: `task298_qwen_aime_v11_30b_runtime_resource_base_load_s1`
- Worker branch:
  `intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1`
- PR: #364
  `https://github.com/songCNMS/Nemotron/pull/364`
- Evidence source head synced to NemTron:
  `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`
- Local output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z`
- Remote run root:
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z`
- Remote repo sync:
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/Nemotron`
- Remote venv:
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/venv`
- Host:
  `lg-cmc-b7r201-f08u26-h200-000126`

## Model Path

Exact model path used:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

Nearby 30B-A3B directories observed but not substituted:

- `Qwen3-30B-A3B`
- `Qwen3-30B-A3B-Base`
- `Qwen3-30B-A3B-Instruct-2507`
- `Qwen3-30B-A3B-Instruct-2507-FP8`
- `Qwen3-30B-A3B-Thinking-2507`

Candidate inventory:

- `du -sh`: `57G`
- Safetensor shards: `16`
- Safetensor total bytes from metadata probe: `61066575656`
- Non-safetensor hash rows: `12`
- HF config: `Qwen3MoeConfig`, architecture `Qwen3MoeForCausalLM`
- Tokenizer: `Qwen2TokenizerFast`, vocab size `151669`, chat template present
- Key config values: 48 layers, hidden size 2048, 32 attention heads, 4 KV
  heads, 128 experts, 8 experts per token, MoE intermediate size 768,
  max positions 262144, dtype bfloat16.

## Commands And Environment

Repo sync to task-owned `/root` run path:

```bash
tar --exclude .git -C /work-agents/intern_nemotron_worker_2/Nemotron -cf - . \
  | ssh NemTron "rm -rf '${REMOTE_RUN}/Nemotron' && mkdir -p '${REMOTE_RUN}/Nemotron' && tar -C '${REMOTE_RUN}/Nemotron' -xf -"
```

Runtime preflight environment:

```bash
TASK298_REMOTE_RUN=/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z
PYTHONPATH=${TASK298_REMOTE_RUN}/Nemotron/src
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
SUPER3_M1_TRAINING_PROFILE=qwen
```

Task-owned venv setup:

```bash
python3 -m venv --system-site-packages "${REMOTE_RUN}/venv"
"${REMOTE_RUN}/venv/bin/python" -m pip install --no-deps \
  megatron-energon==7.3.2 multi-storage-client==0.49.0 xattr==1.3.0 \
  bracex==2.6 wcmatch==10.1 braceexpand==0.1.7 rapidyaml==0.13.0.post2 \
  deprecation==2.1.0 filetype==1.2.0 webdataset==1.0.2
```

Bridge import command:

```bash
cd /root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/Nemotron
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
PYTHONPATH=${PWD}/src \
/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/venv/bin/python \
  scripts/import_qwen3_4b_local_to_megatron.py \
  --hf-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  --output-dir /root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0
```

Observed environment:

- Python: `/usr/bin/python3`, `3.12.3`
- Torch: `2.9.1+cu129`
- Transformers: `4.57.1`
- Safetensors: `0.7.0`
- NeMo import: `PASS`
- Megatron import: `PASS`
- Megatron-Bridge import: `PASS`
- `AutoBridge.import_ckpt`: `PASS`
- GPUs visible: 8 x NVIDIA H200, 143771 MiB each
- Filesystem free at start: `/root` overlay 176T free; `/mnt/cephfs` 14P free

Command return codes:

- venv support-package install: `0`
- pip check: `1`
- no-training config/import preflight: `0`
- Bridge import driver: `0`
- Bridge import log: `BRIDGE_IMPORT_RC=0`

## Preflight Results

No-training config/import manifest:

`/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/manifests/no_training_30b_config_import_manifest.json`

Manifest sha256:

`3279ed2b1f6383a13954bd43b300ec1f92c847ae409720e563ad8b79a0f04dd7`

Manifest disposition:

`PASS_NO_TRAINING_30B_RUNTIME_CONFIG_IMPORT_PREFLIGHT`

Passed checks:

- HF `AutoConfig.from_pretrained(..., trust_remote_code=True)`
- HF `AutoTokenizer.from_pretrained(..., trust_remote_code=True)`
- Safetensors metadata read for all 16 shards
- `nemo`, `megatron`, `megatron.bridge`, `megatron.bridge.training.config`
- `megatron.bridge.recipes.qwen.qwen3_moe`
- `megatron.energon`
- current-main
  `nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train`
- 30B Qwen3-MoE Bridge recipe builder

Config built but not executed:

- Entrypoint:
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- Config:
  `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`
- Sequence length: `4096`
- Tensor parallel: `4`
- Pipeline parallel: `2`
- Expert parallel: `4`
- Expert tensor parallel: `1`
- Sequence parallel: `true`
- Global batch size: `8`
- Micro batch size: `1`
- Preflight-only train iters value: `1`
- Preflight-only optimizer LR/min LR: `5e-7` / `1e-7`

Side-effect guard after the no-training preflight was false for all guarded
paths:

- `checkpoints`
- `endpoint`
- `hf_export`
- `qwen3_30b_bridge_import_iter0`

The later Bridge import intentionally created only the task-owned
`qwen3_30b_bridge_import_iter0` base-import artifact.

## Bridge Base Import Proof

Remote import root:

`/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`

Bridge import result:

- `IMPORT_DONE`
- `BRIDGE_IMPORT_RC=0`
- Start: `2026-06-02T14:44:12Z`
- End: `2026-06-02T14:48:25Z`
- Latest checkpointed iteration: `0`
- Size: `57G`
- Inventory rows: `16`

Bridge import log:

`/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/logs/bridge_import_30b_iter0.log`

Bridge import log sha256:

`0218eea8ab8334ac697bc465edce9e40ade3afa4523825d450ab152cd912629b`

Checkpoint inventory:

`/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/manifests/bridge_import_30b_inventory.tsv`

Inventory sha256:

`09644a889efa598e8614b60cffa63dbf9ca5be1ed0b2a77ea4cc1120db25c38c`

Full checksum manifest:

`/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/manifests/bridge_import_30b_checksums.sha256`

Checksum manifest sha256:

`d01f2f4a9440d1b11691abf507f2354ecc0e079c3dbb9cb2a0cbb1f4a8a9649c`

Largest imported checkpoint files:

| File | Size bytes |
|---|---:|
| `iter_0000000/__0_0.distcp` | `30556390675` |
| `iter_0000000/__0_1.distcp` | `30556412817` |
| `iter_0000000/.metadata` | `9140515` |
| `iter_0000000/tokenizer/vocab.json` | `3383407` |
| `iter_0000000/tokenizer/merges.txt` | `1671853` |

## Resource And Parallelism Recommendation

Later full 30B SFT task should use the current-main 30B-specific entrypoint:

`src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`

Recommended launch surface for later training:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_PRETRAINED_CHECKPOINT=/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0 \
python -m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=8 \
  src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml \
  train.global_batch_size=8 train.micro_batch_size=1
```

This command is recorded as the later route shape only. It was not run.

Parallelism:

- `tensor_model_parallel_size=4`
- `pipeline_model_parallel_size=2`
- `expert_model_parallel_size=4`
- `expert_tensor_parallel_size=1`
- `sequence_parallel=True`
- Minimum GPUs from TP x PP: `8`
- Recommended resource: one 8 x H200 node, `nproc_per_node=8`

## Eval Route / Export Route Decision

Base model testing route:

- The base HF model can be evaluated through an eval-only SGLang endpoint
  directly from
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Historical 30B base/eval route used SGLang `tp=4`, `dp=2`, 16k context, and
  corrected math max tokens `8192`.

Later SFT checkpoint comparison route:

- A future Megatron SFT checkpoint should use an eval-only HF export plus
  SGLang endpoint unless lead assigns and approves a separate 30B no-export
  in-process MCore load route.
- Any eval-only export/endpoint is a route-finding/testing dependency, not
  promotion, release, or endpoint-promotion clearance.

No eval, corrected AIME scoring, non-AIME canary, export, or endpoint was run
in task298.

## Artifact Checksums

Key local artifact hashes:

| Artifact | sha256 |
|---|---|
| `manifests/no_training_30b_config_import_manifest.json` | `3279ed2b1f6383a13954bd43b300ec1f92c847ae409720e563ad8b79a0f04dd7` |
| `logs/no_training_30b_config_import_preflight.log` | `5ec05b25d96462f7fbf95eb922b0e8f922d373fdd19bbad9415e8a05fdd67668` |
| `logs/runtime_env.log` | `80e9efe532133112f04014cfd69c2078bb838d93a053de14d0fc52299a259f7f` |
| `logs/model_path_inventory.log` | `ede2f77f0892380663cccc9a1ca9d39a83bf9af69c291af22945f7723d338ff4` |
| `manifests/key_artifacts.sha256` | `69fe5bb2b7535347fd522d02f47e94654639b578c97998b2bce4e84139461172` |
| `logs/bridge_import_30b_iter0.log` | `0218eea8ab8334ac697bc465edce9e40ade3afa4523825d450ab152cd912629b` |
| `manifests/bridge_import_30b_du.txt` | `8c022da0c8cb109e899503af8565892db79abe5a9dff41265530c38b17d5c4fe` |
| `manifests/bridge_import_30b_inventory.tsv` | `09644a889efa598e8614b60cffa63dbf9ca5be1ed0b2a77ea4cc1120db25c38c` |
| `manifests/bridge_import_30b_latest_iteration.txt` | `5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9` |
| `manifests/bridge_import_30b_checksums.sha256` | `d01f2f4a9440d1b11691abf507f2354ecc0e079c3dbb9cb2a0cbb1f4a8a9649c` |

## Residual Risks

- `pip check` returned rc `1` in the task-owned venv, with missing/variant
  package warnings including `hydra-core`, `nvidia-resiliency-ext`,
  `causal-conv1d`, `mamba-ssm`, and NeMo dependency version mismatches. The
  30B config/import preflight and Bridge import passed despite this; a later
  full training task may need the same kind of lead-scoped runtime remediation
  used by the 4B smoke path.
- The 30B Bridge import used single-process `AutoBridge.import_ckpt` and wrote
  rank-local torch-dist shards `[t 1/1, p 1/1]`. The later training recipe
  builds TP=4/PP=2/EP=4 and should be checked in its own launch task before any
  optimizer step.
- No 30B no-export/no-endpoint MCore generation route was proven. The eval
  decision therefore remains eval-only HF export plus SGLang for future SFT
  checkpoints unless lead assigns a separate no-export 30B route probe.

## Boundary Confirmation

Confirmed:

- 30B runtime/resource/base-load gate only.
- No SFT training.
- No optimizer step.
- No corrected AIME scoring.
- No non-AIME canary.
- No testing/eval run.
- No export.
- No endpoint.
- No promotion or go/no-go claim.
- No task255 reuse.
- No AIME2025 prompts or labels used as train data.
- No deletion or overwrite under `/mnt/cephfs/data/processing/lei.song`.
- No shared model/data root mutation.
- No main push.
- No merge.
