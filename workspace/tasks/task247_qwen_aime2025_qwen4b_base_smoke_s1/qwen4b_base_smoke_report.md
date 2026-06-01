# task247 Qwen3-4B base AIME2025 smoke report

<!-- METADATA:STATUS=ReadyForPR,SESSION=1 -->

## Summary

Produced the first same-harness Qwen3-4B base AIME2025 pilot artifact for
task247. The valid run used the approved base checkpoint and tokenizer:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

Base pilot score:

- Numerator: `11`
- Denominator: `30`
- Exact-normalized accuracy: `0.36666666666666664`
- Request status: `30/30 ok`
- Parsed rows: `23/30`
- Finish reasons: `stop=21`, `length=9`
- Average completion tokens: `5726.266666666666`

This task did not judge any FT checkpoint, train, launch 30B, launch 8-GPU
scale, push `main`, or merge.

## Input Cache

No pre-existing task071 AIME score cache was visible locally or on `NemTron`.
I built a task-owned evaluator cache from pinned `opencompass/AIME2025`
sources, using the AIME_2025 prompt shape observed in task233 simple-evals
artifacts.

- Local cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`
- Remote cache used by runner:
  `/root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db`
- Source manifest:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache_source_manifest.json`
- Source dataset: `opencompass/AIME2025`
- Source revision: `a6ad95f611d72cf628a80b58bd0432ef6638f958`
- Row count: `30`
- Unique problem count: `30`
- Repeat policy: `1` request per problem

Source file hashes:

- `aime2025-I.jsonl`: `b91b3c96f05d9635d2a0692b124ebe023c1ff59cb19c074275e6c4b349d0659e`
- `aime2025-II.jsonl`: `16a2dcfbbf9db1b11f8a69a3ba5e4cac73e3641b19a37e2307e9c12240bbed5e`
- `README.md`: `43ac9ef26311be77671372031a242d031858ba836a6d79f323a1bac748e012ac`

The cache contains held-out labels for evaluator scoring only. It is stored as
a task-owned output artifact and is not committed into the repo.

## Protocol

The valid run used the task243/#319 corrected runner:

`workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py`

Command shape:

```bash
python3 /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/eval/run_corrected_math_full_eval.py \
  --aime-score-cache /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db \
  --hmmt-output-jsonl /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/not_used_hmmt.jsonl \
  --output-dir /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/eval/qwen4b_base_aime2025_30x1_20260601T170700Z \
  --endpoint-url http://127.0.0.1:13147/v1/chat/completions \
  --model-id qwen3-4b-instruct-2507-base \
  --tasks aime25 \
  --aime-prompt-variant original \
  --aime-max-tokens 8192 \
  --aime-limit-rows 30 \
  --parallelism 4 \
  --timeout 900
```

Sampling and denominator policy:

- `temperature=0.0`
- `top_p=1e-5`
- `max_tokens=8192`
- `/v1/chat/completions`
- exact-normalized boxed/symbolic answer match
- denominator includes all request rows, including unparsed and length-capped rows

## Endpoint

Lead-observed/local common ports remained unavailable:

- `127.0.0.1:13000`: connection refused
- `127.0.0.1:30001`: connection refused

I launched a task-owned Qwen3-4B base endpoint on `NemTron`:

```bash
CUDA_VISIBLE_DEVICES=0 python3 -m sglang.launch_server \
  --model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  --served-model-name qwen3-4b-instruct-2507-base \
  --host 127.0.0.1 \
  --port 13147 \
  --tensor-parallel-size 1 \
  --trust-remote-code \
  --context-length 16384
```

The endpoint was stopped after artifact collection. A post-run probe showed no
listener on port `13147` and no remaining Qwen3-4B SGLang compute process.

## Valid Artifacts

Remote output directory:

`/root/task247_qwen_aime2025_qwen4b_base_smoke_s1/eval/qwen4b_base_aime2025_30x1_20260601T170700Z`

Local copied output directory:

`/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`

Required files:

- `summary.json`
- `results.jsonl`
- `command.txt`
- `endpoint_model_manifest.json`

Artifact hashes:

- `summary.json`: `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`
- `results.jsonl`: `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`
- `command.txt`: `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`
- `endpoint_model_manifest.json`: `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354`

## Diagnostic Failed Attempt

The first endpoint launch included `--reasoning-parser qwen3`. SGLang then
returned assistant text in `message.reasoning_content` while
`message.content` was `null`. The task243 runner expects `message.content`, so
all 30 rows failed with:

`AttributeError("'NoneType' object has no attribute 'find'")`

That run is retained only as a diagnostic artifact and is not used as the base
score:

`/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170000Z_failed_reasoning_parser`

## Residual Risk

- The base score is a pilot `30 x 1` artifact, not a full `300`-request
  repeated evaluation.
- The input cache was generated from pinned `opencompass/AIME2025` JSONL files
  because the historical task071 cache path was not visible in this worker
  environment.
- Any FT comparison must use the same cache, runner, prompt variant, endpoint
  route, sampling parameters, and all-request denominator. No FT judgment is
  made in this task.
