# Qwen Chat-Aligned 30B Retrain Metrics - Session 53

## Run

- Run name: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Remote root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Local metrics root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics`
- Tmux session: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Planned train iters: `8740`

## Current Metrics

- Latest synced train iteration: `3350/8740` (`38.33%`)
- Latest train lm loss: `0.4001406`
- Recent 50 train lm loss mean: `0.381169328`
- Latest learning rate: `7.206947e-07`
- Latest checkpoint marker: `3000`
- Max skipped iterations reported: `0`
- Max nan iterations reported: `0`

## Validation

| Iteration | Validation loss | Validation PPL |
|---:|---:|---:|
| 500 | 0.4614768 | 1.586415 |
| 1000 | 0.3756810 | 1.455983 |
| 1500 | 0.3804657 | 1.462966 |
| 2000 | 0.3635950 | 1.438491 |
| 2500 | 0.3618866 | 1.436036 |
| 3000 | 0.3531853 | 1.423595 |

The `3000` validation point is the best validation point observed in this corrected Qwen-chat aligned run so far.

## Comparison With v1

Baseline: `task071_qwen30b_a3b_math_final_answer_v1`, the stopped math-sidecar run packed with the Super3 template.

| Iteration | Qwen-chat loss | v1 loss | Delta loss | Qwen-chat PPL | v1 PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 0.4614768 | 0.4612986 | +0.0001782 | 1.586415 | 1.586132 | +0.000283 |
| 1000 | 0.3756810 | 0.3763687 | -0.0006877 | 1.455983 | 1.456984 | -0.001001 |
| 1500 | 0.3804657 | 0.3830907 | -0.0026250 | 1.462966 | 1.466811 | -0.003845 |
| 2000 | 0.3635950 | 0.3630795 | +0.0005155 | 1.438491 | 1.437750 | +0.000741 |
| 2500 | 0.3618866 | 0.3616964 | +0.0001902 | 1.436036 | 1.435763 | +0.000273 |
| 3000 | 0.3531853 | 0.3541151 | -0.0009298 | 1.423595 | 1.424919 | -0.001324 |

## Directional Comparison With Conservative Baseline

Baseline: `task071_qwen30b_a3b_sft_strategy_conservative_v2`. This comparison is directional only because the baseline used a different data blend and supervision recipe.

| Iteration | Qwen-chat loss | Conservative loss | Delta loss | Qwen-chat PPL | Conservative PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 0.4614768 | 0.3861638 | +0.0753130 | 1.586415 | 1.471326 | +0.115089 |
| 1000 | 0.3756810 | 0.4025858 | -0.0269048 | 1.455983 | 1.495687 | -0.039704 |
| 1500 | 0.3804657 | 0.4071296 | -0.0266639 | 1.462966 | 1.502499 | -0.039533 |
| 2000 | 0.3635950 | 0.3947224 | -0.0311274 | 1.438491 | 1.483972 | -0.045481 |
| 2500 | 0.3618866 | 0.4022133 | -0.0403267 | 1.436036 | 1.495130 | -0.059094 |
| 3000 | 0.3531853 | 0.4029848 | -0.0497995 | 1.423595 | 1.496284 | -0.072689 |

## Decision

- Continue the run through eval/save points `3500` and `4000`.
- Rationale: validation improved from `2500` to `3000`, `3000` is current best, recent train loss mean is lower than the Session 52 window, and skipped/nan stayed at `0/0`.
- Specific risk to watch: the old v1 run regressed at validation `3500`, so the next check should compare `3500` and `4000` against both v1 and the current best at `3000`.

## Artifacts

- Curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves.png`
- Session curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session53_iter3000.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/validation_points.csv`
- v1 comparison markdown: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/early_comparison_vs_task071_qwen30b_a3b_math_final_answer_v1.md`

## Verification

- `python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `git diff --check` passed.

## Next Action

- Monitor eval/save points `3500` and `4000`, refresh curves, and decide from validation whether to continue through full `8740` or prepare an early checkpoint export candidate.
