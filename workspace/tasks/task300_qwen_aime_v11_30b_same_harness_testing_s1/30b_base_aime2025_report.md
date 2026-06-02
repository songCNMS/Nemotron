# task300 30B base AIME2025 report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_3,SESSION=5 -->

## Summary

- Task: `task300_qwen_aime_v11_30b_same_harness_testing_s1`
- Branch:
  `intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1`
- PR: #363
  `https://github.com/songCNMS/Nemotron/pull/363`
- Eval source head: `89a3d37117aed5df8a4a211ce1f74f1041dcc487`
- Base model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Route disposition: `BASE_PASS`
- Base score: `15/30`
- Exact-normalized accuracy: `0.5`
- Denominator: all 30 requested corrected AIME2025 rows.

The first corrected same-harness 30B base AIME2025 score is complete. The run
used the task247 corrected AIME2025 input cache and the same endpoint-style
OpenAI chat payload/scoring protocol used for accepted 4B base scoring:
original prompt, `/v1/chat/completions`, `max_tokens=8192`, `temperature=0.0`,
`top_p=1e-5`, last boxed-value parser, `normalize_answer` exact match, and
all-request denominator.

This is a base-score artifact only. It is not FT judgment, canary approval,
training clearance, promotion, endpoint promotion, or 30B scale approval.

## Upstream Gate State

| Gate | Observed state | Task300 effect |
|---|---|---|
| task298 runtime/base-load | PR #364 merged at `2026-06-02T15:13:14Z`, PR head `8f1f7df9d6499eedb150d7e63323df8ee0411f41`, merge commit `a0235f14dc3c49797c507ab4578536ba2d6ed3ac`; route report approves eval-only SGLang endpoint direct from the 30B HF path for base testing | Releases 30B base AIME route |
| task299 data/packing | PR #365 merged at `2026-06-02T15:29:15Z`, approved head `b8b760fb8f46cda8f302adbea106f19cc234e038`, merge commit `205fc919a643b1478964a9e91793247c5e821a38` | Data gate merged after the base run; no effect on base-only score artifact |
| task301 training/checkpoint | No task301 checkpoint consumed in this report | Can still block future canary and FT-vs-base testing |

## Artifact Roots

Local run root:

`/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`

Remote run root:

`/root/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`

Eval artifact directory:

`eval/qwen30b_base_aime2025_30x1_20260602T152351Z`

Key artifacts:

- `summary.json`
- `results.jsonl`
- `full_completions.jsonl`
- `parser_diagnostics.jsonl`
- `manifests/aime_row_manifest.jsonl`
- `manifests/command_env_manifest.json`
- `manifests/endpoint_manifest.json`
- `checksum_manifest.json`
- `endpoint/server_command.txt`
- `endpoint/content_probe.json`
- `endpoint/post_stop_check.log`
- `logs/remote_30b_base_aime_eval.log`

Run-level checksum manifest:

`manifests/run_artifact_checksums.sha256`

## Endpoint / Export Choice

Choice: eval-only SGLang endpoint direct from the base HF model path.

Export choice: no export or conversion.

Server command:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 PYTHONUNBUFFERED=1 python3 -m sglang.launch_server --model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 --served-model-name qwen3-30b-a3b-instruct-2507-base --host 127.0.0.1 --port 13230 --tensor-parallel-size 4 --data-parallel-size 2 --trust-remote-code --context-length 16384 --log-level info --log-level-http warning
```

Endpoint probe:

- URL: `http://127.0.0.1:13230/v1/models`
- Served model: `qwen3-30b-a3b-instruct-2507-base`
- `max_model_len`: `16384`
- Content smoke:
  `/root/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z/endpoint/content_probe.json`
- `message.content` was non-null in the smoke response.

Post-run endpoint stop check:

- `post_stop_check.log` time: `2026-06-02T15:32:32Z`
- Port `13230`: no listener recorded.
- Exact `python3 -m sglang.launch_server` process for port `13230`: none.
- GPU state after stop: eight H200s at `1 MiB`, `0 %`.

## Eval Command / Environment

Eval command:

```bash
cd /root/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z/Nemotron
CUDA_VISIBLE_DEVICES= PYTHONPATH=/root/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z/Nemotron/src python3 workspace/tasks/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_sglang_base_aime_eval.py \
  --aime-score-cache /root/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z/input/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db \
  --output-dir /root/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z/eval/qwen30b_base_aime2025_30x1_20260602T152351Z \
  --endpoint-url http://127.0.0.1:13230/v1/chat/completions \
  --model-id qwen3-30b-a3b-instruct-2507-base \
  --model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  --source-head 89a3d37117aed5df8a4a211ce1f74f1041dcc487 \
  --task298-approved-head 8f1f7df9d6499eedb150d7e63323df8ee0411f41 \
  --task298-pr-merge-commit a0235f14dc3c49797c507ab4578536ba2d6ed3ac \
  --aime-prompt-variant original \
  --aime-max-tokens 8192 \
  --aime-limit-rows 30 \
  --parallelism 4 \
  --timeout 1200
```

Environment captured in `manifests/command_env_manifest.json`:

- Host: `lg-cmc-b7r201-f08u26-h200-000126`
- Python: `/usr/bin/python3`, `3.12.3`
- Eval client `CUDA_VISIBLE_DEVICES`: empty string; generation happened through
  the eval-only endpoint.
- Endpoint GPUs: `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`
- Endpoint parallelism: SGLang `tensor-parallel-size=4`,
  `data-parallel-size=2`, context length `16384`.
- Task298 approved head:
  `8f1f7df9d6499eedb150d7e63323df8ee0411f41`
- Task298 merge commit:
  `a0235f14dc3c49797c507ab4578536ba2d6ed3ac`

## Protocol Proof

Input cache:

`input/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`

Input cache sha256:

`c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`

Input source manifest sha256:

`0c68142e83da11107e5dbaa86bfad1dbba87799354853de196c5f2434139b171`

Protocol:

- Task: `aime25`
- Rows: `30`
- Repeats: `1`
- Prompt variant: `original`
- Endpoint: `/v1/chat/completions`
- `max_tokens`: `8192`
- `temperature`: `0.0`
- `top_p`: `1e-5`
- Parser: last boxed value from `boxed_values`
- Normalizer: `normalize_answer`
- Denominator: all requested rows
- Score normalization: exact-normalized accuracy = correct rows / all
  requested rows

The task300 runner was added only to retain full completions, prompt hashes,
parser diagnostics, endpoint manifest, command/env manifest, and checksum
manifest. The scoring functions and payload semantics are aligned with the
corrected task071/task247 endpoint harness.

## Results

Summary:

- Total requests: `30`
- Status counts: `ok=30`
- Correct rows: `15`
- Denominator rows: `30`
- Exact-normalized accuracy: `0.5`
- Parsed rows: `19/30`
- Parsed rate: `0.6333333333333333`
- Finish reasons: `stop=19`, `length=11`
- Contains expected rows: `19`
- Average completion tokens: `5798.233333333334`
- Runtime: `187.932` seconds

Correct sample IDs:

`aime_01_r01`, `aime_02_r01`, `aime_03_r01`, `aime_04_r01`,
`aime_06_r01`, `aime_08_r01`, `aime_16_r01`, `aime_17_r01`,
`aime_19_r01`, `aime_21_r01`, `aime_22_r01`, `aime_23_r01`,
`aime_24_r01`, `aime_25_r01`, `aime_26_r01`

Length/unparsed sample IDs:

`aime_05_r01`, `aime_09_r01`, `aime_11_r01`, `aime_12_r01`,
`aime_15_r01`, `aime_18_r01`, `aime_20_r01`, `aime_27_r01`,
`aime_28_r01`, `aime_29_r01`, `aime_30_r01`

All 11 length rows are counted as incorrect under the all-request denominator.

## Checksums

Key artifact hashes:

| Artifact | sha256 |
|---|---|
| `summary.json` | `4a31904c118b09f80c1d77e7cd3aee0ede7117634b620092ea95e6306529e2ec` |
| `results.jsonl` | `19c853420a6827fa70b43db74bba987ba984a150e0e2c799234f0abfa26642fb` |
| `full_completions.jsonl` | `27bf059b5a6a2868e75435af4b1c738e7ded5649a3d0b48cc52b4c7d76f243a7` |
| `parser_diagnostics.jsonl` | `aefd30646c089ebfe5ae3c36ed0725a0ffb0217925ff711fb5790b7851d87d8e` |
| `manifests/aime_row_manifest.jsonl` | `cda747b03fdb7fd657c10f06147a00167e51e1bc23901939f640690662f32784` |
| `manifests/command_env_manifest.json` | `e4f6c67f5a0be30e7672d96ee7635e26b202875553db676325ebd7a66af907c8` |
| `manifests/endpoint_manifest.json` | `1e10c3b9ea92d8d581bd203e7641ec2e0a5db38e3770f04faeeb9ef7ea0d9c17` |
| `checksum_manifest.json` | `1fba8fea61e4ac179fea6c5e267f3cfb2005a3072f5b2e710287924c0c42abc0` |
| `endpoint/server_command.txt` | `50bbc5cfbc0263fbb01fbd8b0fc9335bdaa3b5176e28469f569afaff4fa6b636` |
| `endpoint/content_probe.json` | `3ee1429b66dab872a683a933ba9a6d92769c575b4246bbf0ee8b7fa3e8accc41` |
| `endpoint/post_stop_check.log` | `df4eaced132e5c3babd920e3579c08f85ccc2eb877a113bebb1fa129dad74e02` |
| `endpoint/sglang_qwen30b_base_13230.log` | `412810691970d87ddf98051905a54a92a0e8a10e51e1a2a36c375f741b9e58c5` |
| `logs/remote_30b_base_aime_eval.log` | `47b9dc2dcc9461b0fc36a34d3e060e00bb4dbb46f964d3241b41612bfe9737d6` |
| `input/aime_score_cache.opencompass_a6ad95f.db` | `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74` |
| `input/aime_score_cache_source_manifest.json` | `0c68142e83da11107e5dbaa86bfad1dbba87799354853de196c5f2434139b171` |
| `manifests/run_artifact_checksums.sha256` | `4ae7f6a8ccf6d2e7508103242f9a359f2f25f5a7d4f74f6ba8ddb714a02d6363` |

## Checks

- `python3 -m py_compile
  workspace/tasks/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_sglang_base_aime_eval.py`
- `git diff --check`
- ASCII check for the new runner.
- JSON validation for `summary.json`, `command_env_manifest.json`,
  `endpoint_manifest.json`, and `content_probe.json`.
- JSONL validation for `results.jsonl`, `full_completions.jsonl`,
  `parser_diagnostics.jsonl`, and `manifests/aime_row_manifest.jsonl`.
- Row-count check: all four JSONL artifacts contain exactly `30` rows.

## Residuals

- This is a 30-problem x 1-repeat base score only.
- `11/30` requests hit `finish_reason=length` at 8192 generated tokens and are
  unparsed/incorrect under the all-request denominator.
- The endpoint route was eval-only and stopped after the run; no persistent or
  promotion endpoint remains.
- Future 30B FT comparison must use the same corrected cache, prompt variant,
  endpoint/chat API semantics, sampling settings, parser, normalizer, and
  all-request denominator.
- No task301 checkpoint, non-AIME canary, or FT AIME run is included here.

## Boundary Confirmation

Confirmed:

- No training or optimizer steps.
- No FT eval.
- No non-AIME canary.
- No task255 reuse.
- No AIME2025 prompts or labels as trainable data.
- AIME2025 was used only as held-out eval/decontam input.
- No export or conversion.
- No export for promotion.
- No endpoint promotion.
- No promotion or go/no-go claim beyond reporting the base comparator score.
- No shared deletion.
- No main push or merge.
