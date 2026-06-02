# task293 task285 iter2 corrected AIME2025 eval report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_3,SESSION=3 -->

## Summary

- Task: `task293_qwen_aime_v11_task285_same_harness_aime_eval_s1`
- Branch:
  `intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1`
- Run source head: `87de0a97e6c0406a4b67520faab6b11d91d9131e`
- Run id: `run_20260602T085237Z`
- Disposition: `PASS` for the task293 corrected AIME2025 eval gate only.

The task285 Qwen3-4B V11 iter2 checkpoint scored `12/30` exact-normalized
corrected AIME2025 accuracy `0.4` under the task293 no-export/no-endpoint local
MCore route. The accepted task247 Qwen3-4B base comparator is `11/30 =
0.36666666666666664`, so the FT result is `+1` correct and `+0.03333333333333338`
accuracy versus base.

This is not promotion, scale-up, endpoint, export, 30B, or 8-GPU approval.

## Inputs

- Candidate checkpoint:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`
- Qwen3-4B base/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Accepted base artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`
- Accepted base input cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`
- Local task293 output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`
- Remote task293 output root:
  `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`

## Command And Environment

Remote command:

```bash
cd /root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/Nemotron
CUDA_VISIBLE_DEVICES=0 \
PYTHONPATH=/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/Nemotron/src \
python3 workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py \
  --output-root /root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/artifacts \
  --checkpoint-iter-dir /root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002 \
  --base-model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  --aime-score-cache /root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/input/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db \
  --base-artifact-root /root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/input/qwen4b_base_aime2025_30x1_20260601T170700Z \
  --source-head 87de0a97e6c0406a4b67520faab6b11d91d9131e \
  --aime-prompt-variant original \
  --aime-limit-rows 30 \
  --max-tokens 8192 \
  --batch-size 1 \
  --top-k 1 \
  --temperature 1.0 \
  --top-p 0.0 \
  --random-seed 1234
```

Observed environment:

- Host: `lg-cmc-b7r201-f08u26-h200-000126`
- Python: `/usr/bin/python3`, `3.12.3`
- Torch: `2.9.1+cu129`
- CUDA visibility: `CUDA_VISIBLE_DEVICES=0`
- Visible CUDA devices: `1`
- GPU: `NVIDIA H200`
- Runtime: `7396.045` seconds

## Protocol Proof

- Same AIME source cache as accepted base, copied into task293 run input:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`
- Same task247 source manifest hash:
  `0c68142e83da11107e5dbaa86bfad1dbba87799354853de196c5f2434139b171`
- Same corrected AIME row count and denominator: `30` requested rows, all
  request rows included in denominator.
- Same prompt variant: `original`.
- Same max-token cap: `8192`.
- Same corrected parser/normalizer/scorer logic copied from task247's
  `run_corrected_math_full_eval.py`: `boxed_values`, `normalize_answer`,
  last boxed prediction, exact-normalized `correct`, and
  `contains_expected`.
- Prompt-token proof against task247 base: `0` prompt-token mismatches across
  all 30 rows. First three local formatted prompt token counts were `66`,
  `177`, and `145`, matching base usage.
- Generation route: task293 used the task291-approved no-export/no-endpoint
  in-process MCore static engine route. It uses `top_k=1` greedy argmax with
  `temperature=1.0`, `top_p=0.0` to preserve deterministic generation without
  launching an endpoint. The accepted base used SGLang `/v1/chat/completions`
  with `temperature=0.0`, `top_p=1e-5`; exact transport/sampling parameters are
  therefore not byte-identical, but the deterministic greedy intent, prompt
  tokenization, parser, normalization, max tokens, cache, and denominator match.

Accepted task247 base artifact hashes:

| File | sha256 |
|---|---|
| `summary.json` | `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639` |
| `results.jsonl` | `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961` |
| `command.txt` | `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40` |
| `endpoint_model_manifest.json` | `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354` |

## Metrics

| Metric | FT task285 iter2 | Accepted base |
|---|---:|---:|
| Correct | `12/30` | `11/30` |
| Exact-normalized accuracy | `0.4` | `0.36666666666666664` |
| Delta correct | `+1` | |
| Parsed rows | `21/30` | `23/30` |
| Request status | `30/30 ok` | `30/30 ok` |
| Finish reasons | `stop=21`, `length=9` | `stop=21`, `length=9` |
| Avg completion tokens | `5452.866666666667` | `5726.266666666666` |

Correct rows:
`aime_01_r01`, `aime_03_r01`, `aime_04_r01`, `aime_05_r01`,
`aime_06_r01`, `aime_16_r01`, `aime_17_r01`, `aime_19_r01`,
`aime_21_r01`, `aime_22_r01`, `aime_24_r01`, `aime_27_r01`.

Length-capped rows:
`aime_09_r01`, `aime_10_r01`, `aime_11_r01`, `aime_12_r01`,
`aime_18_r01`, `aime_23_r01`, `aime_28_r01`, `aime_29_r01`,
`aime_30_r01`.

## Artifacts

Local copied artifacts:

| File | sha256 |
|---|---|
| `artifacts/aime_eval/summary.json` | `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7` |
| `artifacts/aime_eval/results.jsonl` | `4cbc2a9543a658df6a3e18e3128c5a5c9a173f9a575372095cfcbe5d6232aca5` |
| `artifacts/aime_eval/full_completions.jsonl` | `5cb1e11ab8d331127c7c12f2cd8c04d83d2e6bd93445a5ebffc62363e2a818b4` |
| `artifacts/manifests/aime_prompt_manifest.json` | `93146086fcc2214fc3c866354e23358d320377caddb6d2b5a2bd58954e85b919` |
| `artifacts/manifests/checkpoint_load_manifest.json` | `243044f2e548e0c8b1b539e9c11fee17a39b4d45898e1a6601382716e4d90c74` |
| `artifacts/manifests/command_env_manifest.json` | `5b128b5cc84159b8603b07fc92475ebc768152b7c0ea0fae0897c6635a502ccf` |
| `artifacts/manifests/checksum_manifest.json` | `6a47e802433648248658010125db51474d0b4af565dc10c637d004900948e7d4` |
| `logs/remote_no_export_aime_eval.log` | `c0dbfcd93cbb7c615c7f784b201a862e338c4eea23c0faf6d9dd9aa5bdcae4ab` |
| `logs/remote_no_export_aime_eval_command.txt` | `39bfe804e49eb34ada919ef0ec557313a7cea7eed26c86ab18f746cf2fdd487b` |

## Boundary Confirmation

Confirmed:

- Qwen3-4B only.
- One visible GPU only.
- No training or optimizer steps.
- No AIME2025 prompts or labels as trainable data; AIME2025 was used only as
  held-out eval input.
- No task255 reuse.
- No export or conversion.
- No endpoint launch.
- No promotion or global go/no-go claim beyond this reported eval result.
- No shared deletion.
- No main push or merge.
- No 30B.
- No 8-GPU.

Residual risk: task293's FT generation backend is the no-export/no-endpoint
MCore route approved after task291, while the accepted base comparator was
collected through SGLang `/v1/chat/completions`. Prompt tokenization, cache,
parser, denominator, max tokens, and deterministic greedy intent match; exact
transport and sampling parameter surfaces are not byte-identical because
task293 explicitly forbids endpoint launch.
