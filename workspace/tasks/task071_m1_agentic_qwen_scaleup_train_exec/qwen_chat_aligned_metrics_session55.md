# Qwen Chat-Aligned 30B Retrain Metrics - Session 55

## Run

- Run name: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Remote root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Local metrics root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics`
- Tmux session: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Planned train iters: `8740`

## Current Metrics

- Latest synced train iteration: `4280/8740` (`48.97%`)
- Latest train lm loss: `0.3979205`
- Recent 50 train lm loss mean: `0.377208316`
- Latest learning rate: `5.728975e-07`
- Checkpoint marker: `4000`
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
| 3500 | 0.3879959 | 1.474024 |
| 4000 | 0.3775419 | 1.458695 |

The `4000` validation point recovered from the `3500` regression, but the best checkpoint remains iter `3000`.

## Comparison

Baseline v1: `task071_qwen30b_a3b_math_final_answer_v1`.

| Iteration | Qwen-chat loss | v1 loss | Delta loss | Qwen-chat PPL | v1 PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 3000 | 0.3531853 | 0.3541151 | -0.0009298 | 1.423595 | 1.424919 | -0.001324 |
| 3500 | 0.3879959 | 0.3861476 | +0.0018483 | 1.474024 | 1.471302 | +0.002722 |
| 4000 | 0.3775419 | 0.3747286 | +0.0028133 | 1.458695 | 1.454597 | +0.004098 |

Directional conservative baseline: `task071_qwen30b_a3b_sft_strategy_conservative_v2`. This comparison is not a controlled one-variable experiment.

| Iteration | Qwen-chat loss | Conservative loss | Delta loss | Qwen-chat PPL | Conservative PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 3500 | 0.3879959 | 0.3752722 | +0.0127237 | 1.474024 | 1.455387 | +0.018637 |
| 4000 | 0.3775419 | 0.3803424 | -0.0028005 | 1.458695 | 1.462785 | -0.004090 |

## Decision

- Keep iter `3000` as the current export/eval candidate because it has the best validation loss so far.
- Keep training active through eval/save points `4500` and `5000`.
- Decision criterion: if validation remains materially above iter `3000`, prepare export/eval from iter `3000`; if validation recovers near or below iter `3000`, re-evaluate the candidate checkpoint.

## Artifacts

- Latest curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves.png`
- Session curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session55_iter4000.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/validation_points.csv`

## Verification

- `python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `git diff --check` passed.

## Next Action

- Monitor eval/save points `4500` and `5000`, refresh curves, and choose between exporting iter `3000` or a newer checkpoint based on validation recovery.
