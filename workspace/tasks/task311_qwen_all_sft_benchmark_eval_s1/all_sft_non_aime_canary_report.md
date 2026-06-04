# task311 all-SFT non-AIME canary report

<!-- METADATA:STATUS=Pass,ASSIGNEE=intern_nemotron_worker_3,SESSION=8 -->

## Summary

- Task: `task311_qwen_all_sft_benchmark_eval_s1`
- Worker branch:
  `intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1`
- PR: `#371`
- Branch base: current `origin/main`
  `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Canary run source head:
  `d2e275e3ec775cd8f73f7bdeeb0bd7f07b44c372`
- Status: `PASS_NON_AIME_CANARY_ONLY`
- Run ID: `run_20260603T173607Z`
- Local output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`
- NemTron output root:
  `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`

Lead released only checkpoint-load plus synthetic non-AIME
canary/completion-retention for the task310 salvage checkpoint after task313
review and task310 merge. This report records that canary result only. It does
not run or authorize benchmark eval, AIME/task243 eval, MMLU-Pro/HMMT/M1 basket
eval, export, endpoint, promotion, additional training, task255 reuse,
AIME2025 train data, shared deletion, self-merge, or main push.

## Inputs

- Candidate checkpoint:
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Prompt YAML:
  `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z/Nemotron/src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
- Prompt YAML sha256:
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`
- Prompt set:
  `qwen_v11_non_aime_export_load_canary_v1`
- Prompt provenance: five synthetic, non-AIME, non-trainable canary prompts.
  The prompt manifest records `excludes_aime2025=true`,
  `excludes_training_rows=true`, and `no_aime2025_prompt_or_label_text=true`.

## Command and Route

Retained command:

```bash
cd '/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z/Nemotron' && CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 PYTHONUNBUFFERED=1 PYTHONPATH='/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z/Nemotron/src' python3 -m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=8 workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/run_30b_no_export_canary_probe.py --output-root '/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z/artifacts' --checkpoint-iter-dir /root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035 --base-model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 --prompt-yaml '/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z/Nemotron/src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml' --source-head 'd2e275e3ec775cd8f73f7bdeeb0bd7f07b44c372' --max-tokens 256 --top-k 1 --temperature 1.0 --top-p 0.0 --random-seed 1234 --tensor-model-parallel-size 4 --pipeline-model-parallel-size 2 --expert-model-parallel-size 4 --expert-tensor-parallel-size 1 --context-parallel-size 1 --rank-timeout-minutes 30
```

Route:
`direct_in_process_mcore_static_engine_no_export_no_endpoint_30b_tp4_pp2_ep4_etp1_topk1_greedy`.

The wrapper used for task311 delegates to the accepted task304 no-export
canary runner while stamping task311 artifact metadata. The inherited stdout
label `TASK304_DISPOSITION=PASS` is therefore a log-label residual; artifact
metadata uses `task311_qwen_all_sft_benchmark_eval_s1`.

## Checkpoint Load Proof

Rank 0 checkpoint-load manifest:

- `load_megatron_model=PASS`
- model type: `megatron.core.transformer.module.Float16Module`
- unwrapped model type: `megatron.core.models.gpt.gpt_model.GPTModel`
- device: `cuda:0`
- dtype: `torch.bfloat16`
- eval mode: `true`
- TP/PP/EP/ETP: `4/2/4/1`
- world size: `8`
- hidden size: `2048`
- layers: `48`
- attention heads: `32`
- sequence length: `4096`
- padded vocab size: `151936`

## Canary Metrics

| Metric | Value |
|---|---:|
| Disposition | `PASS` |
| Remote return code | `0` |
| Prompts requested | 5 |
| Completions retained | 5 |
| Non-empty responses | 5 |
| Exact expected-answer matches | 5 |
| Empty responses | 0 |
| Mixed-script responses | 0 |
| Degeneration count | 0 |
| Final-answer marker count | 9 |
| Selected rank | 0 |
| Elapsed seconds | 88.738 |

Decision diagnostics show all five prompt IDs checked, no failed prompt IDs, no
missing prompt IDs, no duplicate prompt IDs, and denominator policy
`all_canary_prompts`.

## Completion Retention

- Aggregate `canary_results.jsonl`: 5 rows.
- Aggregate `canary_full_completions.jsonl`: 5 rows.
- Rank-local result files: 8 files, 5 rows each.
- Rank-local full-completion files: 8 files, 5 rows each.
- Total retained result/full-completion rows across rank-local plus aggregate
  files: 90.

## Key Artifacts and Hashes

| Artifact | sha256 |
|---|---|
| `artifacts/canary/canary_summary.json` | `5da06d50f23bd581d2de5988f999cc4a2d7bb162f487afef1033c29810ce93b5` |
| `artifacts/canary/canary_decision.json` | `7678a8f8f3445882a1e5ea575169d37aae7f7ad9ead14b4f5d788fa5c5cb3ba5` |
| `artifacts/canary/canary_results.jsonl` | `8fb1dc751b080b067f3cad981ae2dc74f3b829e26230cebda6447302aef6cadf` |
| `artifacts/canary/canary_full_completions.jsonl` | `fd86644308d690340545be0fb308912dac87ddd8c3b499e2af4556635c3409f7` |
| `artifacts/manifests/canary_prompt_manifest.json` | `3838d39a779bd28df90ced9a1f9ba99f61bdb3dd747083450be0334cdf52c0b2` |
| `artifacts/manifests/checkpoint_load_manifest_rank0.json` | `5cb3f410e834d5e1e2fc454e205c433a181d95611479d49911292717f49b47b3` |
| `artifacts/manifests/command_env_manifest_rank0.json` | `c456090c0c57420f1f88eca16baf0b22795989ae342d82f8ed5920b206dc9f1e` |
| `artifacts/manifests/checksum_manifest.json` | `cc0f2be1d99e4b1caad4e5eb4e4e7d6f6a3bf99be2d28ff0c9e9b2beb23307d4` |
| `logs/remote_no_export_canary.log` | `785ac96d43ae42d18024620e6c2349cf108d081d6a2cbed2e7f68d093f5545db` |
| `logs/remote_no_export_canary_command.txt` | `5daaba446de385c1741fc53180969395a7d4827da0299bfb3cae95e096d756e8` |
| `logs/remote_no_export_canary.rc` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |

## Checks

- `python3 -m py_compile workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/run_30b_no_export_canary_probe.py`
- JSON parse check for `canary_summary.json` and `checksum_manifest.json`.
- Row-count check for aggregate and rank-local result/full-completion JSONL
  files.
- `git diff --check`

## Residuals

- This is a bounded synthetic non-AIME canary only. It does not establish any
  benchmark base-vs-FT result.
- The no-export route uses top-k=1 greedy MCore sampling. The prompt manifest
  retains the original chat-completions generation contract and records the
  route-level sampling override.
- The logs contain strict-load missing `_extra_state` warnings consistent with
  the prior task304 canary path. Checkpoint load still passed and the remote
  command exited `0`.
- The inherited task304 runner prints a task304 disposition label to stdout;
  retained task311 artifacts carry task311 task IDs.

## Boundary Confirmation

- No training or optimizer steps.
- No AIME2025 prompts or labels used as trainable data.
- No AIME/task243 eval.
- No benchmark eval, including MMLU-Pro, HMMT, or M1 basket rows.
- No task255 reuse.
- No shared deletion under `/mnt/cephfs/data/processing/lei.song`.
- No export, endpoint, promotion, product-code edit, direct main push, merge,
  or self-merge.
