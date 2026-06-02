# task287 non-AIME canary and retention report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

- Task: `task287_qwen_aime_v11_non_aime_canary_retention_s1`
- Branch:
  `intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1`
- PR: #352
- Base: `origin/main`
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `bb33e3eee4f42bd3ab57ea5288053ad40223b27f`
- Local output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`
- Remote run root:
  `/root/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`
- Disposition: `BLOCK`

The task285 iter2 Megatron torch-dist checkpoint can be loaded directly on one
H200 without export or endpoint, but the allowed no-export/no-endpoint local
MCore generation route did not produce canary completion artifacts. No canary
PASS or AIME release is claimed.

## Inputs

- Base Qwen3-4B path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Candidate checkpoint:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`
- Checkpoint root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`
- Latest iteration file: `2`
- Checkpoint metadata:
  `metadata.json` reports `sharded_backend=torch_dist`.
- Prompt source:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
- Prompt source sha256:
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`
- Prompt manifest:
  `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z/manifests/canary_prompt_manifest.json`
- Prompt manifest sha256:
  `69d6634c47eea160548fe2779b6dd6038dc7605e8c9a894660a385efc9ae7cc2`

The prompt manifest contains five synthetic non-AIME prompts:

| Prompt id | Expected | Prompt sha256 |
|---|---:|---|
| `synthetic_arithmetic_sum_37_58` | `95` | `03ab87b34860b54318aca63967e084f48b7d98d4279b098491b41864d64ded22` |
| `synthetic_counting_pens_6_9` | `15` | `d26f79ae8c62499c63a345a178b44aacde5a30aa11022dec960b113a77bf68b2` |
| `synthetic_linear_expression_2x_plus_y` | `29` | `aa9513d595eca0e1aac25499694bbb5b7ace6d9f831fea2a857aed937f7a1290` |
| `synthetic_next_integer_246` | `247` | `989178e58334a31a663f6c7571889f1827c1015b270d2d6cb5cd26b670f57166` |
| `synthetic_word_completion_ready_set` | `go` | `634170a504ee86d582d32fb173fdf6ec554e67f7d1c8fd79846fbdcd2377971e` |

The prompt source explicitly marks the prompts as synthetic, non-AIME,
not training rows, review-only, and not trainable data.

## Commands And Environment

The repo was synced to the task-owned NemTron path with `.git` excluded:

```bash
tar --exclude .git -C /work-agents/intern_nemotron_worker_3/Nemotron -cf - . \
  | ssh NemTron "rm -rf '${REMOTE_RUN}/Nemotron' && mkdir -p '${REMOTE_RUN}/Nemotron' && tar -C '${REMOTE_RUN}/Nemotron' -xf -"
```

Read-only and canary probes used:

```bash
ssh NemTron "REMOTE_RUN='...' PYTHONPATH='${REMOTE_RUN}/Nemotron/src' python3 - <<'PY' ..."
ssh NemTron "CUDA_VISIBLE_DEVICES=0 PYTHONPATH='${REMOTE_RUN}/Nemotron/src' python3 - <<'PY' ..."
```

The direct local route attempted for canary generation was:

- `megatron.bridge.training.model_load_save.load_megatron_model`
- `megatron.bridge.training.model_load_save.load_tokenizer`
- `megatron.core.inference.model_inference_wrappers.gpt.GPTInferenceWrapper`
- `megatron.core.inference.text_generation_controllers.TextGenerationController`
- `megatron.core.inference.engines.StaticInferenceEngine`

Environment evidence:

- Host: `lg-cmc-b7r201-f08u26-h200-000126`
- Python: `/usr/bin/python3`
- Torch: `2.9.1+cu129`
- GPU used for load/canary attempts: `CUDA_VISIBLE_DEVICES=0`
- GPU model: `NVIDIA H200`
- GPU scale: one GPU only, not 8-GPU.
- No endpoint process was launched and no export path was used.

## Checkpoint Load Proof

Single-GPU checkpoint load probe:

- Log:
  `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z/logs/remote_single_gpu_checkpoint_load_probe.log`
- Log sha256:
  `e63eb5634677e2640984bd8666b5b7134f6f6ce71ff9982ba68322c2672d61c1`

Observed result:

- `LOAD_MEGATRON_MODEL=PASS`
- `MODEL_TYPE=builtins.list`
- `MODEL_LEN=1`
- `MODEL0_TYPE=megatron.core.transformer.module.Float16Module`
- `MODEL0_DEVICE=cuda:0`
- `MODEL0_DTYPE=torch.bfloat16`
- `MODEL_EVAL_SET=PASS`

The load emitted missing `_extra_state` warnings but returned a model and set it
to eval mode. This is checkpoint-load proof only; it is not completion proof or
quality evidence.

## Canary Attempts

No canary completion artifacts were produced. The expected files
`canary_summary.json`, `canary_results.jsonl`, and
`canary_full_completions.jsonl` are absent because generation did not complete.

| Attempt | Artifact dir | Status | Blocker | Key hashes |
|---|---|---|---|---|
| `20260602T071900Z` | `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z/canary/qwen4b_task285_iter2_non_aime_canary_20260602T071900Z` | `BLOCK` | Script import path used `megatron.core.transformer.module.get_model_config`, which is not exported in this runtime. | `canary_blocker.json` `551e76adcb3a29ad421bed4ad48d60b31225b664896d10ae715df5bb87b4a9e9`; `checkpoint_load_manifest.json` `e48c8128d4360e93f7858b682474c293ad715bd441fbaa791f33c131b7f83b13`; `canary_command.json` `cc828682f2020a7a72f4afc1bb492b6cac9e2f67335f35a90f23d888c5684fa3` |
| `20260602T072300Z` | `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z/canary/qwen4b_task285_iter2_non_aime_canary_20260602T072300Z` | `BLOCK` | Generation reached `GPTInferenceWrapper` but failed with `ValueError: Unknown attention backend None`. | `canary_blocker.json` `77a6c76e8ddb993d4c4cdf4e460980b8654849f4c86333a9a82dcd62b842720d`; log `remote_direct_canary_run_retry1.log` `c1a8c122e74086fb687bca5403e723879056b835c3dab761b174ba69e8ba27f9` |
| `20260602T072800Z` | `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z/canary/qwen4b_task285_iter2_non_aime_canary_20260602T072800Z` | `BLOCK` | After in-memory attention backend adjustment to `AttnBackend.auto`, generation entered sampling and failed with `torch.AcceleratorError: CUDA error: device-side assert triggered`; CUDA assertion text reported invalid probability tensor. | `canary_blocker.json` `aa451bfb364e1c44b67f6a0beb2612a2f331582555909445099c228c480aab2e`; log `remote_direct_canary_run_retry2.log` `f32df07a0ab624057a93b3615f28416dc212c3d511bd617fa1c2508825e65473` |

The last attempt had already completed by the time the follow-up request to
stop workaround probing was processed. No probes were launched after that
request.

## Route And Dependency Evidence

Relevant logs and hashes:

| Log | sha256 | Finding |
|---|---|---|
| `remote_symbol_probe.log` | `097b500443c750bfb1d6495ad282dff7c77fd47d6fd3c4a0039ccd147ad9de82` | NemTron has `megatron.bridge`, `nemo`, and `megatron.core.inference`; `megatron.core.inference.text_generation` is missing; `megatron.bridge.recipes.qwen` import fails on missing `megatron.energon`. |
| `remote_checkpoint_metadata_probe.log` | `9f9f212ad3024e931ac82f3027a3ef6a43dd50f08a6507e2a7617c030e0218e8` | Checkpoint root, `latest_checkpointed_iteration.txt`, iter2 directory, and base model path are present. |
| `remote_inference_api_probe.log` | `69f8fb97122d18f6da067b5b0f3cb98b3d74b328312b0945171929e290ca5a20` | MCore inference primitives exist, but no ready in-repo canary generator exists. |
| `remote_direct_generation_route_probe.log` | `0b669b627bc88d4ca83a628bedad95e1afa78cbd13106fe946af94cc1966432c` | MCore engine primitives require a pre-built engine; `megatron.bridge.training.finetune` import fails on missing `nvidia_resiliency_ext`. |
| `remote_bridge_config_tokenizer_probe.log` | `4b63671b105448688f04152e93565f586937f84809a7fffc052e4b6491cd9d4f` | `load_model_config` and `load_tokenizer` pass; config type is `Qwen3ModelProvider`, TP=2, PP=1, BF16. |
| `remote_bridge_load_source_probe.log` | `ab201801527cec41319da0d4e2d4da8857ab11d592d242ced7ab0895d96f41fe` | `load_megatron_model` and `build_and_load_model` source show a direct distributed-checkpoint load helper exists. |

## Metrics

- Prompt rows requested for canary: `5`
- Retained completion rows: `0`
- Correct canary answers: `0/5`
- Canary pass: `false`
- Disposition: `BLOCK`

This is not a model-quality failure. It is a route/runtime blocker: the allowed
no-export/no-endpoint generation path could not produce retained completions
from the task285 iter2 checkpoint.

## Boundary Confirmation

Confirmed:

- No training or additional optimizer steps.
- No AIME2025/task243 eval.
- No AIME2025 prompts or labels used as trainable data.
- No task255 reuse.
- No export.
- No endpoint launch.
- No promotion or go/no-go pass claim.
- No shared deletion.
- No 30B.
- No 8-GPU.
- No main push or merge.

Global Qwen AIME gate remains `NO-GO/HOLD`. A future corrected AIME2025
same-harness FT-vs-base comparison remains blocked until a new lead-cleared
task produces a passing non-AIME canary with retained completions or supplies a
different approved no-export/no-endpoint generation route.
