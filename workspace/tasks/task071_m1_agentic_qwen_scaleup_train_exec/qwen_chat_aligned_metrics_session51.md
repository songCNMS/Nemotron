# Qwen Chat-Aligned 30B Retrain Metrics - Session 51

## Run

- Run name: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Remote root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Local metrics root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics`
- Tmux session: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Planned train iters: `8740`

## Current Metrics

- Latest synced train iteration: `1280/8740` (`14.65%`)
- Latest train lm loss: `0.3881855`
- Recent 50 train lm loss mean: `0.390078948`
- Latest learning rate: `9.592108e-07`
- Latest checkpoint marker: `1000`
- Max skipped iterations reported: `0`
- Max nan iterations reported: `0`

## Validation

| Iteration | Validation loss | Validation PPL |
|---:|---:|---:|
| 500 | 0.4614768 | 1.586415 |
| 1000 | 0.3756810 | 1.455983 |

The latest validation point improves over the previous point. The run remains healthy through the first two eval/save intervals.

## Early Comparison With v1

Baseline: `task071_qwen30b_a3b_math_final_answer_v1`, which used Super3-template packed rows.

| Iteration | Qwen-chat loss | v1 loss | Delta loss | Qwen-chat PPL | v1 PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 0.4614768 | 0.4612986 | +0.0001782 | 1.586415 | 1.586132 | +0.000283 |
| 1000 | 0.3756810 | 0.3763687 | -0.0006877 | 1.455983 | 1.456984 | -0.001001 |

## Artifacts

- Curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/validation_points.csv`
- Comparison markdown: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/early_comparison_vs_task071_qwen30b_a3b_math_final_answer_v1.md`

## Verification

- `python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.

## Next Action

- Continue monitoring to iter `1500` and `2000`, refresh the curve image, and compare validation against both v1 and the conservative baseline before checkpoint export decisions.
