# Qwen V5 Final Metrics And Export - Session 78

## Run

- Run name: `task071_qwen30b_a3b_hard_math_precision_v5`
- Remote root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_precision_v5`
- Output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5`
- Training state: completed at `1744/1744`
- GPU state after completion: 8 H200 GPUs idle

## Final Metrics

| Iteration | Validation loss | Validation PPL |
|---:|---:|---:|
| 400 | 0.4572022 | 1.579648 |
| 800 | 0.4302812 | 1.537690 |
| 1200 | 0.4130655 | 1.511444 |
| 1600 | 0.4324673 | 1.541055 |
| 1744 | 0.4126904 | 1.510877 |

Best validation checkpoint: `iter_0001744`.

Training health:

- Max skipped iterations: `0`
- Max nan iterations: `0`
- Latest parsed train loss: iter `1740`, loss `0.4072204`
- Recent-50 train loss mean: `0.41530171`
- Final parsed LR: `8.000175e-08`

Metric artifacts:

- Figure: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/metric_curves_session78_final_iter1744.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/health_summary.json`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/validation_points.csv`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/train_loss_points.csv`

## Checkpoints

Checkpoint marker: `1744`.

Available checkpoints:

- `iter_0000400`
- `iter_0000800`
- `iter_0001200`
- `iter_0001600`
- `iter_0001744`

Each checkpoint is about `399G`.

## HF Export

- Exported checkpoint: `checkpoints/iter_0001744`
- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_precision_v5/hf_export_iter_0001744`
- Export log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_precision_v5/logs/export_iter_0001744_gpu5.log`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-hard-math-precision-v5-iter0001744-hf`
- Size: `61084232276` bytes, about `57G`
- Safetensors shards: `16`
- Manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_precision_v5/hf_export_iter_0001744/task071_export_manifest.json`

Manifest config:

- `model_type=qwen3_moe`
- `num_hidden_layers=48`
- `num_experts=128`
- `num_experts_per_tok=8`
- `vocab_size=151936`
- tokenizer class `Qwen2TokenizerFast`

## Candidate Decision

Use `iter_0001744` as the V5 corrected-eval candidate because it has the best validation loss and exported cleanly to HF format. The recommended evaluation entry is the same corrected protocol used for V3/V4:

- Start SGLang with `tp=4`, `dp=2`, `context_length=16384`, and model id `task071-qwen3-30b-a3b-agentic-sft-hard-math-precision-v5-iter0001744-hf`.
- Run corrected MMLU-Pro full plus corrected AIME25/HMMT full.
- Compare against Session 47 original, V3 `iter_0002200`, and V4 `iter_0000800`.

## Verification

- `source /work-agents/.venv/bin/activate && python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py`
- `source /work-agents/.venv/bin/activate && python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py`
- `git diff --check`
