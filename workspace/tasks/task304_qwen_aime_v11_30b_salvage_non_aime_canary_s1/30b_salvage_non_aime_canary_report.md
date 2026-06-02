# task304 30B salvage non-AIME canary report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

- Task: `task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1`
- Branch:
  `intern_nemotron_worker_3/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1`
- PR: TBD
- Evidence source head: `d8e58461ca1cede2569589f95414c360e0ddd9bc`
- Disposition: `PASS`

The task301 Qwen3-30B-A3B `iter_0000035` salvage checkpoint loaded through a
no-export/no-endpoint in-process MCore route on 8x H200 with task301 checkpoint
parallelism `TP=4`, `PP=2`, `EP=4`, `ETP=1`. It generated and retained full
completions for all five synthetic non-AIME canary prompts. All five expected
answers matched exactly, with no empty responses, mixed-script flags, or
degeneration flags.

This is a bounded non-AIME canary only. It is not AIME2025/task243 evidence,
promotion approval, endpoint approval, export approval, or a go/no-go decision
for the 30B FT model.

## Inputs

- Salvage checkpoint:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Prompt source:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
- Prompt source sha256:
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`
- Prompt set id:
  `qwen_v11_non_aime_export_load_canary_v1`

The prompt manifest confirms `synthetic_prompts_only=true`,
`excludes_aime2025=true`, `no_aime2025_prompt_or_label_text=true`, and
`excludes_training_rows=true`.

## Route

Runner:
`workspace/tasks/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_30b_no_export_canary_probe.py`

Route id:
`direct_in_process_mcore_static_engine_no_export_no_endpoint_30b_tp4_pp2_ep4_etp1_topk1_greedy`

Route details:

- Synced the current branch to a task-owned NemTron `/root` run directory before
  launch.
- Used `torch.distributed.run --nproc_per_node=8` with
  `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`.
- Initialized MCore model parallelism with `TP=4`, `PP=2`, `CP=1`, `EP=4`,
  `ETP=1`.
- Loaded the checkpoint with
  `megatron.bridge.training.model_load_save.load_megatron_model(..., skip_temp_dist_context=True)`
  and explicit `mp_overrides` matching task301 checkpoint parallelism.
- Used MCore static-engine generation with greedy `top_k=1`,
  `temperature=1.0`, `top_p=0.0`, and `max_tokens=256`.
- Retained rank-local completion artifacts and selected rank 0 for aggregate
  canary results.

The first run at `run_20260602T174849Z` blocked before generation because the
loader wrapper defaulted model parallelism back to 1x and hit a distributed
checkpoint access-pattern validation error. The bounded repair was to pass
explicit `mp_overrides`; no export, endpoint, training, AIME data, or conversion
was used.

## Commands And Environment

Local sync pattern:

```bash
tar --exclude='.git' --exclude='__pycache__' --exclude='.mypy_cache' --exclude='.pytest_cache' -cf - . \
  | ssh NemTron "rm -rf '${REMOTE_ROOT}/Nemotron' '${REMOTE_ROOT}/artifacts' '${REMOTE_ROOT}/logs' && mkdir -p '${REMOTE_ROOT}/Nemotron' '${REMOTE_ROOT}/artifacts' '${REMOTE_ROOT}/logs' && tar -C '${REMOTE_ROOT}/Nemotron' -xf -"
```

Remote canary command:

```bash
cd /root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z/Nemotron
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
PYTHONPATH=/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z/Nemotron/src \
python3 -m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=8 \
  workspace/tasks/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_30b_no_export_canary_probe.py \
  --output-root /root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z/artifacts \
  --checkpoint-iter-dir /root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035 \
  --base-model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  --prompt-yaml /root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z/Nemotron/src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml \
  --source-head d8e58461ca1cede2569589f95414c360e0ddd9bc \
  --max-tokens 256 --top-k 1 --temperature 1.0 --top-p 0.0 \
  --random-seed 1234 --tensor-model-parallel-size 4 \
  --pipeline-model-parallel-size 2 --expert-model-parallel-size 4 \
  --expert-tensor-parallel-size 1 --context-parallel-size 1 \
  --rank-timeout-minutes 30
```

Observed environment:

- Host: `lg-cmc-b7r201-f08u26-h200-000126`
- Python: `/usr/bin/python3`, `3.12.3`
- Torch: `2.9.1+cu129`
- GPU visibility: `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`
- GPUs: 8x NVIDIA H200
- Post-run GPU state: each GPU returned to `1 MiB`, `0 %`.
- Remote return code: `0`

## Artifacts

Local run root:

`/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`

Remote run root:

`/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`

Remote artifact root:

`/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z/artifacts`

Key files and sha256:

| File | sha256 |
|---|---|
| `artifacts/canary/canary_summary.json` | `be1a1b544a8f007c4ffceaa5dc758434f8452b4dace0c4f054ca43c8d9ca7c5f` |
| `artifacts/canary/canary_decision.json` | `7678a8f8f3445882a1e5ea575169d37aae7f7ad9ead14b4f5d788fa5c5cb3ba5` |
| `artifacts/canary/canary_results.jsonl` | `35bde0394601c94a278c81600ab9fd5039ac9985ea47219226a138041f81a462` |
| `artifacts/canary/canary_full_completions.jsonl` | `7589dced789173f3956712ca0c0c17215e03d90cb71419ce22209d8aa9bad957` |
| `artifacts/manifests/canary_prompt_manifest.json` | `7b8de981e7d55bd146c557edffd689ed7d1c4af76a14037a0bdfa7770f262da5` |
| `artifacts/manifests/checkpoint_load_manifest_rank0.json` | `2989b432df6e804c6afe11e86ee0baafaed1ea42c2d6b24f9de1317abb92d901` |
| `artifacts/manifests/command_env_manifest_rank0.json` | `d5e282347975d510d2d58b57f26dd8628566d16893b0cd41aba2a8f7a3ee55d8` |
| `artifacts/manifests/checksum_manifest.json` | `0bdbdd6cc28c7c76d6966d1e60832f048c7eb64dff3931c84e269c1a1c2be27b` |
| `artifacts/logs/ranks/rank00_events.jsonl` | `702b1640e2861b45a7811e0bfc31fa705f2b8cca9fc413b7b85cd797f4b26132` |
| `logs/remote_no_export_canary.log` | `18d8dbd021f72f4117f0e183da910a6242ca5d75efe6509816c54a09f5f6d872` |
| `logs/remote_no_export_canary_command.txt` | `83721a5516e716452427e1c72cea3a67fca4f533a418872b3f1cc688b1e9ac20` |
| `logs/remote_no_export_canary.rc` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `logs/local_source_prompt_hashes.sha256` | `91ab609880b63a00f6385872cc3efdeccc8046e86780defba57c587682cd5a94` |

Full completion retention:

- Aggregate retained rows: `5` in `canary_full_completions.jsonl`
- Per-rank retained rows: `5` in each `canary_full_completions_rank0.jsonl`
  through `canary_full_completions_rank7.jsonl`
- Aggregate result rows: `5` in `canary_results.jsonl`
- Per-rank result rows: `5` in each `canary_results_rank0.jsonl` through
  `canary_results_rank7.jsonl`

## Checkpoint Load Proof

`checkpoint_load_manifest_rank0.json` reports:

- `load_megatron_model`: `PASS`
- `model0_type`: `megatron.core.transformer.module.Float16Module`
- `unwrapped_model_type`: `megatron.core.models.gpt.gpt_model.GPTModel`
- `model_device`: `cuda:0`
- `model_dtype`: `torch.bfloat16`
- `model_eval`: `true`
- `tensor_model_parallel_size`: `4`
- `pipeline_model_parallel_size`: `2`
- `expert_model_parallel_size`: `4`
- `expert_tensor_parallel_size`: `1`
- `sequence_parallel`: `true`
- `hidden_size`: `2048`
- `num_layers`: `48`
- `num_attention_heads`: `32`
- `seq_length`: `4096`
- `padded_vocab_size`: `151936`

The rank0 event log records the effective loader override:

```json
{"event":"load_megatron_model_start","mp_overrides":{"tensor_model_parallel_size":4,"pipeline_model_parallel_size":2,"context_parallel_size":1,"expert_model_parallel_size":4,"expert_tensor_parallel_size":1,"sequence_parallel":true,"virtual_pipeline_model_parallel_size":null,"hierarchical_context_parallel_sizes":null,"perform_initialization":false}}
```

## Canary Metrics

Summary:

- Prompt rows requested: `5`
- Retained completion rows: `5`
- Non-empty responses: `5`
- Exact expected-answer matches: `5/5`
- Missing prompt ids: none
- Failed prompt ids: none
- Final-answer marker count: `9`
- Empty responses: `0`
- Mixed-script count: `0`
- Degeneration count: `0`
- Selected rank: `0`
- Elapsed time: `89.62` seconds

Per prompt:

| Prompt id | Completion tokens | Extracted | Expected | Content chars | Status |
|---|---:|---|---|---:|---|
| `synthetic_arithmetic_sum_37_58` | 31 | `95` | `95` | 24 | `ok` |
| `synthetic_counting_pens_6_9` | 38 | `15` | `15` | 74 | `ok` |
| `synthetic_linear_expression_2x_plus_y` | 59 | `29` | `29` | 104 | `ok` |
| `synthetic_next_integer_246` | 41 | `247` | `247` | 130 | `ok` |
| `synthetic_word_completion_ready_set` | 10 | `go` | `go` | 33 | `ok` |

Every rank produced the same aggregate counts: `5` completions retained, `5`
exact expected-answer matches, `0` empty, `0` mixed-script, and `0`
degeneration.

## Residuals

- This is a five-prompt synthetic non-AIME canary. It proves bounded checkpoint
  load and completion retention, not benchmark quality.
- Generation uses the accepted no-export MCore greedy-route substitute
  `top_k=1`, `temperature=1.0`, `top_p=0.0`, while the prompt YAML's endpoint
  contract records endpoint-style `temperature=0.0`, `top_p=1e-5`. This is the
  same deterministic greedy semantic-match residual accepted for no-export
  route evidence; it is not an endpoint equivalence claim.
- `command_env_manifest_rank0.json` was written before the `mp_overrides` field
  was added to the in-memory command manifest, so that one field is `null`
  there. The effective override is still recorded in
  `rank00_events.jsonl`, and the checkpoint load manifest proves the loaded
  model parallelism.
- The salvage checkpoint remains a salvage candidate from task301/task303. This
  PASS does not clear AIME2025/task243 or promotion. Any future corrected AIME
  FT-vs-base gate needs a separate explicit lead assignment.

## Boundary Confirmation

Confirmed:

- Qwen3-30B-A3B only.
- No training or optimizer steps.
- No AIME2025/task243 eval.
- No AIME2025 train prompts or labels.
- No task255 reuse.
- No export or conversion.
- No endpoint launch.
- No promotion claim.
- No shared deletion.
- No main push or merge.
- 8x H200 was used only because the task301 30B checkpoint requires the saved
  task301 distributed parallelism for direct no-export checkpoint load.
