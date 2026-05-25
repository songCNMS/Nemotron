# Qwen Chat-Aligned 30B Retrain Metrics - Session 54

## Request

- User request: return the metrics curve image.
- Returned image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session54_iter3500.png`
- Feishu image message id: `om_x100b6e7161ba14a4b4bf4743bbc48dc`
- Feishu text message id: `om_x100b6e71615994b0b2685ab8dcfcd75`

## Current Metrics

- Run name: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Latest synced train iteration: `3500/8740` (`40.05%`)
- Latest train lm loss: `0.4007806`
- Latest learning rate: `6.977427e-07`
- Max skipped iterations reported: `0`
- Max nan iterations reported: `0`
- Checkpoint state at final spot-check: `3500` save had started; `latest_checkpointed_iteration.txt` still reported `3000`

## Validation

| Iteration | Validation loss | Validation PPL |
|---:|---:|---:|
| 500 | 0.4614768 | 1.586415 |
| 1000 | 0.3756810 | 1.455983 |
| 1500 | 0.3804657 | 1.462966 |
| 2000 | 0.3635950 | 1.438491 |
| 2500 | 0.3618866 | 1.436036 |
| 3000 | 0.3531853 | 1.423595 |
| 3500 | 0.3879959 | 1.474024 |

Best validation remains iter `3000` at loss/PPL `0.3531853/1.423595`. The iter `3500` point regressed to `0.3879959/1.474024`.

## v1 Comparison

Baseline: `task071_qwen30b_a3b_math_final_answer_v1`.

| Iteration | Qwen-chat loss | v1 loss | Delta loss | Qwen-chat PPL | v1 PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 3000 | 0.3531853 | 0.3541151 | -0.0009298 | 1.423595 | 1.424919 | -0.001324 |
| 3500 | 0.3879959 | 0.3861476 | +0.0018483 | 1.474024 | 1.471302 | +0.002722 |

The Qwen-chat aligned run reproduced the same mid-run validation rebound pattern as v1 around `3500`.

## Artifacts

- Latest curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves.png`
- Session curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session54_iter3500.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/validation_points.csv`

## Verification

- `python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `git diff --check` passed.

## Next Action

- Monitor checkpoint save completion for `3500`, then wait for validation@4000 to decide whether the `3500` regression is transient or the run should favor the iter `3000` checkpoint for export/eval.
