# task306 30B task301 same-harness AIME evaluation report

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nemotron_worker_3,SESSION=7 -->

## Summary

- Task: `task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1`
- Branch:
  `intern_nemotron_worker_3/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1`
- PR: `#369`
- Eval source head: `894e2e71e72f09926128e37f22000802804522bc`
- Candidate checkpoint:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`
- Base model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Accepted base comparator: task300 Qwen3-30B-A3B corrected AIME2025
  `15/30 = 0.5`
- Task306 FT score: `14/30`
- Exact-normalized FT accuracy: `0.4666666666666667`
- Delta versus base: `-1/30`, `-0.033333333333333326`
- Disposition: `FAIL`

The task301 Qwen3-30B-A3B `iter_0000035` salvage checkpoint completed the
corrected AIME2025 30x1 held-out evaluation through the bounded no-export,
no-endpoint MCore route. The result is below the accepted task300 30B base
comparator, so this is a fail/no-promotion record.

This report does not authorize promotion, endpoint launch, export, additional
training, task255 reuse, AIME2025 train-data use, shared deletion, direct main
push, or merge/self-merge.

## Artifact Roots

Local run root:

`/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`

Remote run root:

`/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`

Remote artifact root:

`/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z/artifacts`

Key retained local files:

- `artifacts/aime_eval/summary.json`
- `artifacts/aime_eval/results.jsonl`
- `artifacts/aime_eval/full_completions.jsonl`
- `artifacts/aime_eval/parser_diagnostics.jsonl`
- `artifacts/aime_eval/results_rank*.jsonl`
- `artifacts/aime_eval/full_completions_rank*.jsonl`
- `artifacts/aime_eval/parser_diagnostics_rank*.jsonl`
- `artifacts/manifests/aime_prompt_manifest.json`
- `artifacts/manifests/checkpoint_load_manifest_rank*.json`
- `artifacts/manifests/command_env_manifest_rank*.json`
- `artifacts/manifests/checksum_manifest.json`
- `artifacts/logs/ranks/rank*_events.jsonl`
- `logs/remote_no_export_aime_eval_command.txt`
- `logs/remote_no_export_aime_eval.log`
- `logs/remote_no_export_aime_eval.rc`
- `input/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`
- `input/qwen30b_base_aime2025_30x1_20260602T152351Z/*`

The remote return code was `0`. The local tar copy emitted only a small
remote/local clock-skew timestamp warning for log mtimes.

## Route

Runner:

`workspace/tasks/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_30b_no_export_aime_eval.py`

Route id:

`direct_in_process_mcore_static_engine_no_export_no_endpoint_30b_tp4_pp2_ep4_etp1_topk1_greedy_corrected_aime25`

Execution route:

- No export or conversion.
- No endpoint.
- `torch.distributed.run` with `nproc_per_node=8`.
- GPUs: `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`.
- Host: `lg-cmc-b7r201-f08u26-h200-000126`.
- Python: `/usr/bin/python3`, `3.12.3`.
- Torch: `2.9.1+cu129`.
- GPU type observed by manifest: `NVIDIA H200`.
- Parallelism: `TP=4`, `PP=2`, `CP=1`, `EP=4`, `ETP=1`, world size `8`.
- Sampling: `max_tokens=8192`, `batch_size=1`, `top_k=1`,
  `temperature=1.0`, `top_p=0.0`, `random_seed=1234`.

Remote command:

```bash
cd '/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z/Nemotron' && CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 PYTHONUNBUFFERED=1 PYTHONPATH='/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z/Nemotron/src' python3 -m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=8 workspace/tasks/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_30b_no_export_aime_eval.py --output-root '/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z/artifacts' --checkpoint-iter-dir /root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035 --base-model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 --aime-score-cache '/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z/input/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db' --base-artifact-root '/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z/input/qwen30b_base_aime2025_30x1_20260602T152351Z' --source-head '894e2e71e72f09926128e37f22000802804522bc' --aime-prompt-variant original --aime-limit-rows 30 --max-tokens 8192 --batch-size 1 --top-k 1 --temperature 1.0 --top-p 0.0 --random-seed 1234 --tensor-model-parallel-size 4 --pipeline-model-parallel-size 2 --expert-model-parallel-size 4 --expert-tensor-parallel-size 1 --context-parallel-size 1 --rank-timeout-minutes 240
```

## Checkpoint Load Proof

`artifacts/manifests/checkpoint_load_manifest_rank0.json` reports:

- `load_megatron_model`: `PASS`
- Model wrapper type:
  `megatron.core.transformer.module.Float16Module`
- Unwrapped model type:
  `megatron.core.models.gpt.gpt_model.GPTModel`
- Model device: `cuda:0`
- Model dtype: `torch.bfloat16`
- Model eval mode: `true`
- Hidden size: `2048`
- Layers: `48`
- Attention heads: `32`
- `seq_length`: `4096`
- Padded vocab size: `151936`
- Effective checkpoint parallelism: `TP=4`, `PP=2`, `EP=4`, `ETP=1`
- `sequence_parallel`: `true`

## Protocol Proof

Accepted base artifact root reused as local task input:

`input/qwen30b_base_aime2025_30x1_20260602T152351Z`

Base artifact hashes recorded in task306 summary:

| Base artifact | sha256 |
|---|---|
| `summary.json` | `4a31904c118b09f80c1d77e7cd3aee0ede7117634b620092ea95e6306529e2ec` |
| `results.jsonl` | `19c853420a6827fa70b43db74bba987ba984a150e0e2c799234f0abfa26642fb` |
| `full_completions.jsonl` | `27bf059b5a6a2868e75435af4b1c738e7ded5649a3d0b48cc52b4c7d76f243a7` |
| `parser_diagnostics.jsonl` | `aefd30646c089ebfe5ae3c36ed0725a0ffb0217925ff711fb5790b7851d87d8e` |
| `checksum_manifest.json` | `1fba8fea61e4ac179fea6c5e267f3cfb2005a3072f5b2e710287924c0c42abc0` |

Task306 protocol equivalence evidence:

- Same corrected AIME2025 input cache: `true`.
- AIME cache sha256:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`.
- Same prompt variant: `original`.
- Same requested row count and denominator: `30`.
- Prompt token mismatch count against task300 base artifacts: `0`.
- Same max tokens: `8192`.
- Same parser and normalizer: last boxed-value parser and `normalize_answer`
  exact match copied from the corrected task247/task300 harness family.
- Same all-request denominator: all 30 requested rows.
- Selected rank policy: rank 0 aggregate; no best-correct rank selection.

Residual:

- `sampling_exact_parameter_match=false`.
- Task300 base used SGLang `/v1/chat/completions` with
  `temperature=0.0`, `top_p=1e-5`.
- Task306 used the no-export MCore greedy route with `top_k=1`,
  `temperature=1.0`, `top_p=0.0`.
- This is a deterministic greedy semantic-match residual, not a byte-identical
  endpoint transport claim.

## Metrics

Summary from `artifacts/aime_eval/summary.json`:

| Metric | Value |
|---|---:|
| Total requested rows | `30` |
| Status `ok` rows | `30` |
| Correct rows | `14` |
| Denominator rows | `30` |
| Exact-normalized accuracy | `0.4666666666666667` |
| Parsed rows | `17` |
| Parsed rate | `0.5666666666666667` |
| Finish `stop` rows | `17` |
| Finish `length` rows | `13` |
| Contains expected rows | `17` |
| Average completion tokens | `5831.333333333333` |
| Base correct rows | `15` |
| Base accuracy | `0.5` |
| Delta correct | `-1` |
| Delta accuracy | `-0.033333333333333326` |
| Disposition | `FAIL` |

Correct sample ids:

`aime_01_r01`, `aime_02_r01`, `aime_03_r01`, `aime_04_r01`,
`aime_06_r01`, `aime_08_r01`, `aime_16_r01`, `aime_17_r01`,
`aime_18_r01`, `aime_19_r01`, `aime_21_r01`, `aime_22_r01`,
`aime_23_r01`, `aime_24_r01`

Incorrect sample ids:

`aime_05_r01`, `aime_07_r01`, `aime_09_r01`, `aime_10_r01`,
`aime_11_r01`, `aime_12_r01`, `aime_13_r01`, `aime_14_r01`,
`aime_15_r01`, `aime_20_r01`, `aime_25_r01`, `aime_26_r01`,
`aime_27_r01`, `aime_28_r01`, `aime_29_r01`, `aime_30_r01`

Per-row diagnostics from rank 0 aggregate:

| Sample | Finish | Parsed | Correct | Prediction | Expected | Completion tokens |
|---|---|---:|---:|---|---|---:|
| `aime_01_r01` | `stop` | true | true | `70` | `70` | `4125` |
| `aime_02_r01` | `stop` | true | true | `588` | `588` | `4733` |
| `aime_03_r01` | `stop` | true | true | `16` | `16` | `1357` |
| `aime_04_r01` | `stop` | true | true | `117` | `117` | `3050` |
| `aime_05_r01` | `length` | false | false | `None` | `279` | `8192` |
| `aime_06_r01` | `stop` | true | true | `504` | `504` | `1333` |
| `aime_07_r01` | `stop` | true | false | `271` | `821` | `7614` |
| `aime_08_r01` | `stop` | true | true | `77` | `77` | `2036` |
| `aime_09_r01` | `length` | false | false | `None` | `62` | `8192` |
| `aime_10_r01` | `stop` | true | false | `70` | `81` | `5030` |
| `aime_11_r01` | `length` | false | false | `None` | `259` | `8192` |
| `aime_12_r01` | `length` | false | false | `None` | `510` | `8192` |
| `aime_13_r01` | `length` | false | false | `None` | `204` | `8192` |
| `aime_14_r01` | `length` | false | false | `None` | `60` | `8192` |
| `aime_15_r01` | `length` | false | false | `None` | `735` | `8192` |
| `aime_16_r01` | `stop` | true | true | `468` | `468` | `1508` |
| `aime_17_r01` | `stop` | true | true | `49` | `49` | `1451` |
| `aime_18_r01` | `stop` | true | true | `82` | `82` | `7107` |
| `aime_19_r01` | `stop` | true | true | `106` | `106` | `1888` |
| `aime_20_r01` | `stop` | true | false | `360` | `336^\circ` | `7892` |
| `aime_21_r01` | `stop` | true | true | `293` | `293` | `4678` |
| `aime_22_r01` | `stop` | true | true | `237` | `237` | `2442` |
| `aime_23_r01` | `stop` | true | true | `610` | `610` | `7542` |
| `aime_24_r01` | `stop` | true | true | `149` | `149` | `4658` |
| `aime_25_r01` | `length` | false | false | `None` | `907` | `8192` |
| `aime_26_r01` | `length` | false | false | `None` | `113` | `8192` |
| `aime_27_r01` | `length` | false | false | `None` | `19` | `8192` |
| `aime_28_r01` | `length` | false | false | `None` | `248` | `8192` |
| `aime_29_r01` | `length` | false | false | `None` | `104` | `8192` |
| `aime_30_r01` | `length` | false | false | `None` | `240` | `8192` |

## Task306 Checksums

| Artifact | sha256 |
|---|---|
| `artifacts/aime_eval/summary.json` | `a3e046e3d5417095bd2d1072609dcdaf90ad17620015062efaac561e028ab947` |
| `artifacts/aime_eval/results.jsonl` | `46a702b31208661633b6b783e48f8fac3d6b60e06da3fdb9c3972a51cfa3f827` |
| `artifacts/aime_eval/full_completions.jsonl` | `32bb1e75f653711961b052a1008e53c668eb3787b8c5e3ea1369ed7ba8373704` |
| `artifacts/aime_eval/parser_diagnostics.jsonl` | `7c185fca5dc94105ff77aca48e70cfdeef8d5560a7b790682bdc312b2e807354` |
| `artifacts/manifests/checksum_manifest.json` | `a82f55bc0d9de7adb28aa28812a5d9b8d557a580ac6709cd7483452e3a8f02cd` |
| `artifacts/manifests/aime_prompt_manifest.json` | `23776fa86ca73f708f851b0355d0caaa00645267704ed309a7e5e4d2d94950f0` |
| `artifacts/manifests/checkpoint_load_manifest_rank0.json` | `fc5d745fb9df110b0c3bec639d87759fe4ebd13b9750d89e68f3d5d98ea4cf78` |
| `artifacts/manifests/command_env_manifest_rank0.json` | `0ea2edb381fe047d5280c3273dd0ef5a6faf525bac4e4870e5d1fc9dd9a86fdd` |
| `logs/remote_no_export_aime_eval.log` | `23f168f34636cd84946b5c4f8fee6a59c29670991e66ec2efcc5e9ef44c58fab` |
| `logs/remote_no_export_aime_eval_command.txt` | `e7ad13a6a14bcd6b81c91fa4dd994af5f39485700a7f58dc0c745a9143a8ada7` |
| `logs/remote_no_export_aime_eval.rc` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |

## Validation Checks

- `python3 -m py_compile
  workspace/tasks/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_30b_no_export_aime_eval.py`
- JSON validation for:
  - `artifacts/aime_eval/summary.json`
  - `artifacts/manifests/checksum_manifest.json`
  - `artifacts/manifests/aime_prompt_manifest.json`
- Row count validation:
  - `results.jsonl`: `30`
  - `full_completions.jsonl`: `30`
  - `parser_diagnostics.jsonl`: `30`
- Artifact checksum extraction with `sha256sum`.
- `git diff --check`

## Boundary Confirmation

The task-owned run confirms:

- Qwen3-30B-A3B only.
- No training or optimizer steps.
- AIME2025 was used only as held-out evaluation input.
- No AIME2025 prompt or label was used as trainable data.
- No task255 reuse.
- No export or conversion.
- No endpoint or production endpoint.
- No promotion.
- No shared deletion.
- No main push or merge/self-merge.

## Residuals

- Final score is `14/30`, below accepted base `15/30`; disposition is `FAIL`.
- The no-export MCore route is not byte-identical to the task300 SGLang
  endpoint transport/sampling route. The explicit residual is
  `sampling_exact_parameter_match=false`; deterministic greedy intent is matched
  through the accepted no-export route substitute.
- The run had 13 length rows, all counted incorrect under the all-request
  denominator.
- This is evidence/report closeout only. Independent review or runbook updates
  require a separate lead assignment.
