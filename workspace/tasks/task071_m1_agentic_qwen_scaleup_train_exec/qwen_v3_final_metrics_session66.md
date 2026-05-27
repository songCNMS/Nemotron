# Qwen v3 Final Metrics Session 66

Run: `task071_qwen30b_a3b_math_reasoning_replay_v3`

Remote run root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_reasoning_replay_v3`

Local metrics root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_reasoning_replay_v3/metrics`

## Final Training State

- Final iteration: `2200/2200`
- Final checkpoint marker: `2200`
- Final checkpoint: `checkpoints/iter_0002200`
- Final checkpoint size: about `399G`
- GPU state after completion: all 8 H200 GPUs idle
- Max skipped iterations reported: `0`
- Max nan iterations reported: `0`

## Validation

| Iteration | Validation loss | PPL |
|---:|---:|---:|
| 500 | 0.4362881 | 1.546954 |
| 1000 | 0.4158402 | 1.515644 |
| 1500 | 0.4110765 | 1.508441 |
| 2000 | 0.4093007 | 1.505765 |
| 2200 | 0.4087007 | 1.504861 |

Best validation checkpoint by loss: `iter_0002200`.

## Artifacts

- Final curve: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_reasoning_replay_v3/metrics/metric_curves_session66_final_iter2200.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_reasoning_replay_v3/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_reasoning_replay_v3/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_reasoning_replay_v3/metrics/validation_points.csv`

## Candidate

Use `iter_0002200` as the primary export and corrected mini-eval candidate. The validation loss improved monotonically across all eval points and the final checkpoint is the best observed validation point for this run.
