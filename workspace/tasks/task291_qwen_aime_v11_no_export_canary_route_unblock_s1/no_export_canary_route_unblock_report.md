# task291 no-export canary route unblock report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=4 -->

## Summary

- Task: `task291_qwen_aime_v11_no_export_canary_route_unblock_s1`
- Branch:
  `intern_nemotron_worker_2/task291_qwen_aime_v11_no_export_canary_route_unblock_s1`
- PR: #354
  `https://github.com/songCNMS/Nemotron/pull/354`
- Evidence source head:
  `dfb6ca64a5479990be9d4f54defb9f294c09866f`
- Base history includes task287/#352 and task290/#353 through
  `origin/main` `a372dcd7cd866dc02951f4f1c86eaf05a4c885b4`.
- Disposition: `PASS`

The task285 Qwen3-4B iter2 Megatron checkpoint loaded on one H200 and produced
retained completions for all five synthetic non-AIME canary prompts through a
no-export/no-endpoint in-process MCore route. This is canary route evidence
only; it is not AIME/task243, promotion, export, endpoint, or 30B evidence.

## Inputs

- Checkpoint iteration:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`
- Base model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Prompt source:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
- Prompt source sha256:
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`

## Route

Helper:
`workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_no_export_canary_probe.py`

Route id:
`direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy`

Narrow route repairs applied:

- Held a single-rank NCCL process group and MCore model-parallel state open for
  checkpoint load plus inference wrapper construction.
- Loaded the checkpoint with
  `megatron.bridge.training.model_load_save.load_megatron_model(..., skip_temp_dist_context=True)`.
- Set checkpoint `model_config.attention_backend` from `None` to
  `AttnBackend.auto` in memory only.
- Used MCore `SamplingParams(top_k=1, temperature=1.0, top_p=0.0)` so the
  controller takes its documented greedy `argmax` branch instead of the
  `torch.multinomial` path that triggered task287 invalid-probability CUDA
  asserts.
- Disabled segment retention because
  `DefaultTokenizerText` does not provide `offsets`.
- If `request.generated_text` is empty while generated token ids exist, retained
  text is decoded with the same checkpoint tokenizer from `generated_tokens`.

No export, conversion, endpoint, training loop, optimizer step, AIME/task243
eval, task255 artifact, 30B, or 8-GPU path was used.

## Commands And Environment

Local sync to task-owned NemTron run root:

```bash
tar --exclude .git -C /work-agents/intern_nemotron_worker_2/Nemotron -cf - . \
  | ssh NemTron "rm -rf '${REMOTE}/Nemotron' '${REMOTE}/artifacts' && mkdir -p '${REMOTE}/Nemotron' '${REMOTE}/artifacts' && tar -C '${REMOTE}/Nemotron' -xf -"
```

Remote canary command:

```bash
cd /root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z/Nemotron
CUDA_VISIBLE_DEVICES=0 \
PYTHONPATH=/root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z/Nemotron/src \
python3 workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_no_export_canary_probe.py \
  --output-root /root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z/artifacts \
  --checkpoint-iter-dir /root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002 \
  --base-model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  --prompt-yaml /root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z/Nemotron/src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml \
  --source-head dfb6ca64a5479990be9d4f54defb9f294c09866f \
  --max-tokens 256 --top-k 1 --temperature 1.0 --top-p 0.0 --random-seed 1234
```

Observed environment:

- Host: `lg-cmc-b7r201-f08u26-h200-000126`
- Python: `/usr/bin/python3`, `3.12.3`
- Torch: `2.9.1+cu129`
- GPU visibility: `CUDA_VISIBLE_DEVICES=0`
- Visible CUDA devices: `1`
- GPU model: `NVIDIA H200`

## Artifacts

- Local run root:
  `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- Remote run root:
  `/root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- Remote artifact root:
  `/root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z/artifacts`

Key files and sha256:

| File | sha256 |
|---|---|
| `artifacts/canary/canary_summary.json` | `dd855c2c32b0b7411ee1cd365311363f1d3338753560107768b684b8fb660d40` |
| `artifacts/canary/canary_decision.json` | `c3c9964b6024e1fb137c0db66d255e773727dc8d30fde75c56834b34778c0bca` |
| `artifacts/canary/canary_results.jsonl` | `67e6304786f5bb79fee07f5253ff4de2e449d2756aa6fd2d38762322bdad3dc7` |
| `artifacts/canary/canary_full_completions.jsonl` | `b2768f75415abfeb268b58ba425abe41a7b169fdacbd07e9aa27422e46d7611d` |
| `artifacts/manifests/canary_prompt_manifest.json` | `87993e038420a850723551f0a5118068e734c41130f8f316d8b814a714f61e73` |
| `artifacts/manifests/checkpoint_load_manifest.json` | `f3c974552ae182ab93ec122f6038650fc57479133034d2971b1c277dad8f4390` |
| `artifacts/manifests/command_env_manifest.json` | `24edd402c7772931a2d6422865b16baa7ec2dae9fe9881bc5a5742fd72ccee76` |
| `artifacts/manifests/checksum_manifest.json` | `08477bf8be669314a54359edeeca16de4605262ce5d553944e3477e4ff46f97d` |
| `logs/remote_no_export_canary_probe.log` | `e2044aae855a7a660968e3d2940c946ca874198bef2a04e05163c4235707f17b` |
| `logs/remote_no_export_canary_probe_command.txt` | `09f53671a35a05c4c9f158f28faa63fee7b2ae9eff57bc51cbdb935dadc462b5` |
| `logs/sync_to_nemtron.log` | `9193ea64e5774f6d85010761c68697777f60ee156f370eaf964218b08b895486` |

## Checkpoint Load Proof

`checkpoint_load_manifest.json` reports:

- `load_megatron_model`: `PASS`
- `model0_type`: `megatron.core.transformer.module.Float16Module`
- `unwrapped_model_type`: `megatron.core.models.gpt.gpt_model.GPTModel`
- `model_device`: `cuda:0`
- `model_dtype`: `torch.bfloat16`
- `model_eval`: `true`
- `attention_backend_before`: `None`
- `attention_backend_after`: `<AttnBackend.auto: 5>`
- `padded_vocab_size`: `151936`
- `tokenizer_vocab_size`: `151669`

## Canary Metrics

- Prompt rows requested: `5`
- Retained completion rows: `5`
- Exact expected-answer matches: `5/5`
- Final-answer marker count: `9`
- Offline canary decision: `pass`
- Missing prompt ids: none
- Failed prompt ids: none

Per prompt:

| Prompt id | Completion tokens | Extracted | Expected | Status |
|---|---:|---|---|---|
| `synthetic_arithmetic_sum_37_58` | 45 | `95` | `95` | `ok` |
| `synthetic_counting_pens_6_9` | 39 | `15` | `15` | `ok` |
| `synthetic_linear_expression_2x_plus_y` | 62 | `29` | `29` | `ok` |
| `synthetic_next_integer_246` | 27 | `247` | `247` | `ok` |
| `synthetic_word_completion_ready_set` | 10 | `go` | `go` | `ok` |

The `synthetic_word_completion_ready_set` row used
`generated_tokens_detokenize_fallback`; the MCore request had token ids but an
empty `generated_text` field. The retained text is:
`ready, set, go.\n\nFinal Answer: go`.

## Boundary Confirmation

Confirmed:

- Qwen3-4B only.
- One visible GPU only.
- No training or optimizer steps.
- No AIME2025/task243 eval.
- No AIME2025 train prompts or labels.
- No task255 reuse.
- No export or conversion.
- No endpoint launch.
- No promotion or go/no-go claim.
- No shared deletion, including no deletion under
  `/mnt/cephfs/data/processing/lei.song`.
- No 30B.
- No 8-GPU.
- No main push or merge.

Residual risk: this is a local no-export/no-endpoint MCore canary route pass
with a narrow detokenization fallback for one row. It still requires independent
review before any AIME/task243 comparison is released.
