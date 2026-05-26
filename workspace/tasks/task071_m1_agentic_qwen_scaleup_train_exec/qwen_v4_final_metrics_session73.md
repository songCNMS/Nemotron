# Qwen V4 Hard-Math Recovery Final Metrics - Session 73

## Run State

- Remote run: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4`
- Training status: completed at final iter `1874/1874`
- GPU state after completion: all 8 H200 GPUs idle
- Checkpoint marker: `1874`
- Max skipped iterations: `0`
- Max NaN iterations: `0`

## Metric Artifacts

- Final train log: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/metrics/train.log`
- Final figure: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/metrics/metric_curves_session73_final_iter1870.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/metrics/health_summary.json`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/metrics/validation_points.csv`

## Validation

| Iteration | Loss | PPL |
|---:|---:|---:|
| 400 | 0.4107993 | 1.508023 |
| 800 | 0.358061 | 1.430553 |
| 1200 | 0.3588206 | 1.431640 |
| 1600 | 0.3642109 | 1.439378 |
| 1874 | 0.3586905 | 1.431454 |

Best validation: `iter_0000800`, loss/PPL `0.358061/1.430553`.

## Checkpoints

- `iter_0000400`
- `iter_0000800`
- `iter_0001200`
- `iter_0001600`
- `iter_0001874`

Size check:

- `iter_0000800`: about `399G`
- `iter_0001874`: about `399G`

## Candidate Decision

Primary candidate: `iter_0000800`.

Reason: it has the best validation loss among all saved/evaluated checkpoints. The final checkpoint `iter_0001874` recovered from the iter `1600` validation bump and is close to best, but it is still slightly worse than `iter_0000800`.

Recommended command target for export:

```text
/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4/checkpoints/iter_0000800
```
