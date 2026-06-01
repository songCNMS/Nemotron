# task257 task255 same-harness AIME2025 eval report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_3,SESSION=2 -->

## Summary

- Task: `task257_qwen_aime_v10_task255_same_harness_eval_s1`
- Worker branch:
  `intern_nemotron_worker_3/task257_qwen_aime_v10_task255_same_harness_eval_s1`
- PR: pending at report-authoring time
- Task255 PR: #329, OPEN/CLEAN at head
  `d62036e405edc5daa322c09bb89da19b176bb7bf`
- Task255 FT artifact:
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`
- Base evidence: reused accepted task247 Qwen3-4B base run because protocol,
  input cache, prompt, sampling, endpoint route, parser shape, and denominator
  matched the FT run.
- FT score on the exact readable artifact path: `0/30` exact-normalized
  accuracy `0.0`.
- Accepted base score: `11/30` exact-normalized accuracy
  `0.36666666666666664`.
- Disposition: current exact-path FT result is below base, so it is a
  Qwen3-4B non-regression FAIL if the task255 artifact is accepted. Because
  task256 records REQUEST_CHANGES/HOLD on independent artifact accessibility,
  the overall gate remains HOLD/no promotion.

## Base Evidence Reused

- Base model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Accepted base artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/`
- Base input cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`
- Base cache sha256:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`
- Base summary sha256:
  `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`
- Base results sha256:
  `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`
- Base command sha256:
  `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`
- Base endpoint manifest sha256:
  `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354`
- Base command:

```bash
python3 /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/eval/run_corrected_math_full_eval.py --aime-score-cache /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db --hmmt-output-jsonl /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/not_used_hmmt.jsonl --output-dir /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/eval/qwen4b_base_aime2025_30x1_20260601T170700Z --endpoint-url http://127.0.0.1:13147/v1/chat/completions --model-id qwen3-4b-instruct-2507-base --tasks aime25 --aime-prompt-variant original --aime-max-tokens 8192 --aime-limit-rows 30 --parallelism 4 --timeout 900
```

Base result:

- `30/30` requests ok
- finish reasons: `stop=21,length=9`
- parsed: `23/30`
- correct: `11/30`
- exact-normalized accuracy: `0.36666666666666664`
- average completion tokens: `5726.266666666666`

## FT Endpoint And Run

- Endpoint host: `NemTron`
- Endpoint URL: `http://127.0.0.1:13157/v1/chat/completions`
- Served model: `task255-qwen3-4b-v10-ft-iter0000001`
- Model path:
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`
- Server command:

```bash
CUDA_VISIBLE_DEVICES=0 python3 -m sglang.launch_server --model-path /root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001 --served-model-name task255-qwen3-4b-v10-ft-iter0000001 --host 127.0.0.1 --port 13157 --tensor-parallel-size 1 --trust-remote-code --context-length 16384
```

- Parser/endpoint shape: no reasoning parser; `/v1/chat/completions` returned
  `message.content`, matching the task247 accepted base endpoint shape.
- Remote output:
  `/root/task257_qwen_aime_v10_task255_same_harness_eval_s1/eval/task255_ft_aime2025_30x1_20260601T204900Z`
- Local output:
  `/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/ft_eval/task255_ft_aime2025_30x1_20260601T204900Z/`
- Local endpoint log:
  `/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/logs/sglang_task255_ft_13157.log`
- Eval command:

```bash
python3 /root/task257_qwen_aime_v10_task255_same_harness_eval_s1/eval/run_corrected_math_full_eval.py --aime-score-cache /root/task257_qwen_aime_v10_task255_same_harness_eval_s1/input/aime_score_cache.opencompass_a6ad95f.db --hmmt-output-jsonl /root/task257_qwen_aime_v10_task255_same_harness_eval_s1/input/not_used_hmmt.jsonl --output-dir /root/task257_qwen_aime_v10_task255_same_harness_eval_s1/eval/task255_ft_aime2025_30x1_20260601T204900Z --endpoint-url http://127.0.0.1:13157/v1/chat/completions --model-id task255-qwen3-4b-v10-ft-iter0000001 --tasks aime25 --aime-prompt-variant original --aime-max-tokens 8192 --aime-limit-rows 30 --parallelism 4 --timeout 900
```

## FT Artifact Hashes

- `summary.json`:
  `ba3dd7b10af3fbafd678df434602b3bee0e829a357025e38e5109cbed7367e6e`
- `results.jsonl`:
  `e4d4ba6ece47e0dff6693066488ebba7461fd12fb8ad6dc26741bb931030f5e6`
- `command.txt`:
  `e82f9f50e2aaad46d7aa54334ab422022c2d45444aa13ec13114ad4968bb902d`
- `endpoint_model_manifest.json`:
  `710bb2db20296762ebb6951db566abfcab90bb406e10ef7b2b548fead06f35d9`
- endpoint log:
  `1011e6c3b373455ca9b7a9a3a87443139a87e581e7daf6d8c966b38551e949b7`
- `summary.json` and `endpoint_model_manifest.json` passed
  `python3 -m json.tool`; `results.jsonl` has 30 lines.

## FT Result

- `30/30` requests ok
- finish reasons: `stop=7,length=23`
- parsed: `0/30`
- correct: `0/30`
- exact-normalized accuracy: `0.0`
- average completion tokens: `7202.433333333333`

This is lower than the accepted same-harness base score `11/30`.

## Task255 And Task256 Status

- PR #329 check at closeout: OPEN/CLEAN, base `main`, head
  `d62036e405edc5daa322c09bb89da19b176bb7bf`.
- Task255 worker_2 export report sha256:
  `3893af84bfdb4d78c4f31074a8454b2fa2bab2d69cfec71c42a36b75c49e7686`.
- NemTron read-only artifact probe found the FT export path readable with
  `config.json`, tokenizer files, and three safetensors shards.
- Task256 worker_5 review branch:
  `intern_nemotron_worker_5/task256_qwen_aime_v10_task255_artifact_review_s1`
  at `9b77d7ee57293697860095791ad7e6661241abca`.
- Task256 status from worker_5 docs: REQUEST_CHANGES/HOLD because worker_5
  could not directly access the exact `/root/task255...` checkpoint/HF export
  directories for independent hashing/config inspection.

## Cleanup And Boundaries

- NemTron cleanup verified after run: no listener on port `13157`, no matching
  `sglang.launch_server` process, and no visible GPU compute process.
- No training was run.
- AIME2025 prompts/labels were not used as trainable data.
- No artifact was modified.
- No 30B/8-GPU work was launched.
- No promotion or scale-up clearance is claimed.
- No main push, self-merge, or shared `/mnt/cephfs/data/processing/lei.song`
  deletion was performed.
