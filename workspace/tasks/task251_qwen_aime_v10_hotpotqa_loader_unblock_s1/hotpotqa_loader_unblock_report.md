# task251 HotpotQA Loader Unblock Report

## Disposition

`HOTPOTQA_UNBLOCKED__PACKING_ENV_BLOCKED`

The task-owned HotpotQA standard-format cache and registry override avoid the
unsupported `hotpotqa/hotpot_qa` `trust_remote_code` path. Local task248 prep
now proceeds through HotpotQA M0 and M1 agentic SFT prep. It then stops before
packed Qwen artifacts because the local Python environment lacks
`cosmos_xenna`, which is imported by `stage1_sft/data_prep.py`.

This is local prep evidence only. No NemTron sync, training, FT live eval,
task243 comparison, promotion claim, or 30B/8-GPU work was run.

## Cache And Override

- Output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1`
- Cache manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/manifest.json`
- Cache manifest sha256:
  `40616924497aaad5d140ec1000f8854881c5decb46d4b11e384f48ba4695f2bf`
- Registry override:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/data_registry.hotpotqa_standard_cache.yaml`
- Registry override sha256:
  `6f1ab374091f0f55e5a39e1facdb2bc078a021a3524fff3570863353a997e2dc`
- Override behavior: `m0_search_hotpotqa` sets `trust_remote_code: false` and
  uses `local_jsonl_files` for `train` and `validation`.

Source:

- HF dataset: `hotpotqa/hotpot_qa`
- Config: `distractor`
- Revision: `1908d6afbbead072334abe2965f91bd2709910ab`
- Source URL:
  `https://huggingface.co/datasets/hotpotqa/hotpot_qa/tree/1908d6afbbead072334abe2965f91bd2709910ab/distractor`

Source Parquet files:

| Split | HF path | Rows | sha256 |
|---|---|---:|---|
| train | `distractor/train-00000-of-00002.parquet` | 45224 | `76d3bb3048a7cc73c1958107c0c5872a00d7e7d00c105b81e92f6769e7822e68` |
| train | `distractor/train-00001-of-00002.parquet` | 45223 | `713661628434fbb19fff7392e2e321e4ed107e3c7c7784d0690946e5f722763f` |
| validation | `distractor/validation-00000-of-00001.parquet` | 7405 | `c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6` |

Task cache files:

| Split | Path | Rows | sha256 |
|---|---|---:|---|
| train | `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/hotpotqa_distractor_train_smoke100.jsonl` | 100 | `c5052dadf2984324627a943b72d3b0016c3bebcbea2fb2ee90d9acf2a85f98a4` |
| validation | `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/hotpotqa_distractor_validation_smoke25.jsonl` | 25 | `4440c6820fab423b265abf06dcbf4981146a1c90a8f95bf8105f2517f865ecb5` |

Split mapping:

- `hf_split: train` -> local cache split `train` -> M0 `search_grounded_qa/train-split.jsonl`.
- `hf_val_split: validation` -> local cache split `validation` -> M0 `search_grounded_qa/val-split.jsonl`.

## Commands And Environment

Environment:

- Repo: `/work-agents/intern_nemotron_worker_2/Nemotron`
- Python: `/usr/bin/python`, Python `3.12.3`
- Key package versions observed: `datasets==4.8.5`,
  `huggingface_hub==0.34.4`, `pyarrow==24.0.0`,
  `transformers==4.52.4`, `tokenizers==0.21.4`, `hydra==1.3.2`,
  `omegaconf==2.3.0`, `pandas==2.2.3`
- Qwen3-4B model/tokenizer path verified:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Task246 decontam corpus:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- Task246 M0 sidecar:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`

Commands:

```bash
PYTHONPATH=src python workspace/tasks/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/build_hotpotqa_standard_cache.py \
  --repo-root /work-agents/intern_nemotron_worker_2/Nemotron \
  --output-root /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1 \
  --max-train-rows 100 \
  --max-validation-rows 25 \
  --overwrite
```

Log:
`/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/logs/build_hotpotqa_standard_cache.log`

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py \
  --data-registry /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/data_registry.hotpotqa_standard_cache.yaml \
  --output-dir /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m0_hotpotqa_probe \
  --dataset-id m0_search_hotpotqa \
  --max-train-per-dataset 100 \
  --max-val-per-dataset 25 \
  --overwrite
```

Log:
`/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/logs/m0_hotpotqa_probe.log`

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py \
  --data-registry /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/data_registry.hotpotqa_standard_cache.yaml \
  --output-dir /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m0_agentic \
  --dataset-id m0_search_hotpotqa --dataset-id m0_search_musique --dataset-id m0_coding_mbpp --dataset-id m0_terminal_bash_commands --dataset-id m0_swe_patch_lite --dataset-id m0_tool_calling_hermes --dataset-id m0_tool_calling_hermes_multi --dataset-id m0_tool_call_repair_negative_hermes --dataset-id m0_structured_outputs_hermes_json --dataset-id m0_reasoning_gsm8k --dataset-id m0_math_numinamath \
  --max-train-per-dataset 100 \
  --max-val-per-dataset 25 \
  --overwrite
```

Log:
`/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/logs/m0_agentic_full_probe.log`

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py \
  --m0-input-dir /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m0_agentic \
  --output-dir /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft \
  --overwrite \
  --math-supervision-strategy hard_math_runlength_dp_v10 \
  --math-v10-hard-verified-full-solution-weight 1.0 \
  --math-v10-verified-full-solution-weight 0.0 \
  --math-v10-final-answer-aux-weight 0.0 \
  --math-v10-format-repair-weight 0.0 \
  --math-sidecar-m0-input-dir /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar \
  --math-sidecar-max-records-per-env 8 \
  --math-sidecar-max-val-shadow-per-env 0 \
  --decontaminate-math-against-corpus /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl
```

Log:
`/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/logs/m1_agentic_sft_prep.log`

```bash
export PYTHONPATH=src
export WANDB_MODE=disabled
export WANDB_DISABLED=true
python src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml \
  blend_path=/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft/data_blend_agentic_sft_v0.json \
  output_dir=/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/packed_qwen \
  target_model_family=qwen \
  config_name=qwen_agentic_v0 \
  tokenizer.model=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  chat_template=tokenizer \
  chat_template_kwargs.enable_thinking=false \
  chat_template_kwargs.truncate_history_thinking=false \
  num_shards=8 \
  pack_size=8192 \
  train_ratio=0.98 \
  valid_ratio=0.02 \
  test_ratio=0.0 \
  force=true \
  execution_mode=batch \
  observability.wandb_log_pipeline_stats=false
```

Log:
`/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/logs/qwen_packing.log`

## Results

HotpotQA-only M0 probe:

- Status: `PASS`
- Manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m0_hotpotqa_probe/manifest.json`
- Manifest sha256:
  `6c66c66d28de5a8566214241e917ffc2cc96142ebeaebce007ba1226ad4ec4c6`
- Rows: `m0_search_hotpotqa` train `100`, val `25`
- Errors: none
- `trust_remote_code` error: not reproduced

Task248 M0 selection with override:

- Status: `PASS_WITH_EXISTING_M0_SHORTFALL`
- Manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m0_agentic/manifest.json`
- Manifest sha256:
  `f57fc440e3dfa693827677be5d01da9213e9e0f95958b18d1790d3c99b1dd55d`
- HotpotQA rows: train `100`, val `25`
- Full row count: `1373` JSONL rows across selected M0 splits
- Recorded M0 error: `m0_swe_patch_lite` requested `100/25`
  train/val rows, prepared `100/23`. This is not a HotpotQA blocker and is the
  exit-code-2 condition already tolerated by the generated task248 prep script.

M1 agentic SFT prep:

- Status: `PASS`
- Manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft/manifest.json`
- Manifest sha256:
  `3f367930cd9ddbb568f6ff75bebe3aa2b339332b1e56bd2533ce315cfbbf53ba`
- Blend:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft/data_blend_agentic_sft_v0.json`
- Blend sha256:
  `fdd56cef9f944566a9cd4332ec348ab503258f39a03f94cccd93c70b84b9b338`
- Rows: train `1100`, val shadow `273`, math heldout eval `0`
- Errors: `0`
- M0 sidecar knobs: train cap `8`, val shadow cap `0`
- Math decontamination: applied against the task246 heldout corpus, corpus
  size `560`, blocker findings `0`, dropped rows `0`

Qwen packing:

- Status: `FAIL_ENV_DEPENDENCY`
- No packed shards were produced under:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/packed_qwen`
- Exact blocker:

```text
Traceback (most recent call last):
  File "/work-agents/intern_nemotron_worker_2/Nemotron/src/nemotron/recipes/super3/stage1_sft/data_prep.py", line 100, in <module>
    import cosmos_xenna.pipelines.v1 as pipelines_v1
ModuleNotFoundError: No module named 'cosmos_xenna'
```

## Boundary Checks

- Qwen3-4B only path was used:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- AIME2025 prompts/labels were not added to trainable rows by this task.
  They were used only through the task246 heldout decontamination corpus.
- `agentic_sft_v0_math_heldout_eval.jsonl` has `0` rows.
- No files under `/mnt/cephfs/data/processing/lei.song` were deleted or
  modified.
- No NemTron sync, training, FT live eval, task243 comparison, promotion claim,
  or 30B/8-GPU run was executed.

## Task248 Readiness

Task248 local prep is not fully ready for training continuation yet because
packed Qwen shards, a training plan, checkpoints, exports, and FT eval artifacts
still do not exist.

Task248 can resume past the previous HotpotQA loader blocker by using:

```bash
--data-registry /work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_standard_cache/data_registry.hotpotqa_standard_cache.yaml
```

The next local continuation requirement is an environment with the Xenna
data-prep dependency available, for example the repo's documented Xenna extra
environment for `stage1_sft/data_prep.py`. After that, rerun the Qwen packing
command above and only proceed toward training-plan/NemTron sync after packed
shards and the Qwen chat contract validate.
