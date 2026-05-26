# Qwen Chat-Aligned 30B Retrain Metrics - Session 52

## Run

- Run name: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Remote root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Local metrics root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics`
- Tmux session: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Planned train iters: `8740`

## Current Metrics

- Latest synced train iteration: `2120/8740` (`24.26%`)
- Latest train lm loss: `0.4114348`
- Recent 50 train lm loss mean: `0.390227312`
- Latest learning rate: `8.839769e-07`
- Latest checkpoint marker: `2000`
- Max skipped iterations reported: `0`
- Max nan iterations reported: `0`

## Validation

| Iteration | Validation loss | Validation PPL |
|---:|---:|---:|
| 500 | 0.4614768 | 1.586415 |
| 1000 | 0.3756810 | 1.455983 |
| 1500 | 0.3804657 | 1.462966 |
| 2000 | 0.3635950 | 1.438491 |

The `2000` validation point is the best validation point observed in this corrected Qwen-chat aligned run so far.

## Comparison With v1

Baseline: `task071_qwen30b_a3b_math_final_answer_v1`, the stopped math-sidecar run packed with the Super3 template.

| Iteration | Qwen-chat loss | v1 loss | Delta loss | Qwen-chat PPL | v1 PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 0.4614768 | 0.4612986 | +0.0001782 | 1.586415 | 1.586132 | +0.000283 |
| 1000 | 0.3756810 | 0.3763687 | -0.0006877 | 1.455983 | 1.456984 | -0.001001 |
| 1500 | 0.3804657 | 0.3830907 | -0.0026250 | 1.462966 | 1.466811 | -0.003845 |
| 2000 | 0.3635950 | 0.3630795 | +0.0005155 | 1.438491 | 1.437750 | +0.000741 |

## Directional Comparison With Conservative Baseline

Baseline: `task071_qwen30b_a3b_sft_strategy_conservative_v2`. This comparison is directional only because the baseline used a different data blend and supervision recipe.

| Iteration | Qwen-chat loss | Conservative loss | Delta loss | Qwen-chat PPL | Conservative PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 0.4614768 | 0.3861638 | +0.0753130 | 1.586415 | 1.471326 | +0.115089 |
| 1000 | 0.3756810 | 0.4025858 | -0.0269048 | 1.455983 | 1.495687 | -0.039704 |
| 1500 | 0.3804657 | 0.4071296 | -0.0266639 | 1.462966 | 1.502499 | -0.039533 |
| 2000 | 0.3635950 | 0.3947224 | -0.0311274 | 1.438491 | 1.483972 | -0.045481 |

## Artifacts

- Curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/validation_points.csv`
- v1 comparison markdown: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/early_comparison_vs_task071_qwen30b_a3b_math_final_answer_v1.md`

## Verification

- `python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `git diff --check` passed.

## Next Action

- Continue monitoring to eval/save points `2500` and `3000`, refresh the curve image, and decide whether the validation trend warrants keeping the run active through the planned `8740` iterations.
