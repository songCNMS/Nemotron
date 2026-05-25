# Qwen Chat-Aligned 30B Retrain Metrics - Session 56

## Run

- Run name: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Remote root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Local metrics root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics`
- Tmux session: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Planned train iters: `8740`

## Current Metrics

- Latest synced train iteration: `5000/8740` (`57.21%`)
- Latest train lm loss: `0.3745380`
- Recent 50 train lm loss mean: `0.380308006`
- Checkpoint marker: `5000`
- Max skipped iterations reported: `0`
- Max nan iterations reported: `0`

## Validation

| Iteration | Validation loss | Validation PPL | Delta loss vs best |
|---:|---:|---:|---:|
| 3000 | 0.3531853 | 1.423595 | +0.0000000 |
| 3500 | 0.3879959 | 1.474024 | +0.0348106 |
| 4000 | 0.3775419 | 1.458695 | +0.0243566 |
| 4500 | 0.3790836 | 1.460945 | +0.0258983 |
| 5000 | 0.3781844 | 1.459632 | +0.0249991 |

The run has not recovered to the iter `3000` validation quality after the 3500-point rebound. Iter `5000` is slightly better than iter `4500`, but still materially above the current best.

## Directional Comparison

Conservative baseline: `task071_qwen30b_a3b_sft_strategy_conservative_v2`. This comparison is directional only because the data blend and supervision recipe differ.

| Iteration | Qwen-chat loss | Conservative loss | Delta loss | Qwen-chat PPL | Conservative PPL | Delta PPL |
|---:|---:|---:|---:|---:|---:|---:|
| 4500 | 0.3790836 | 0.3960631 | -0.0169795 | 1.460945 | 1.485963 | -0.025018 |
| 5000 | 0.3781844 | 0.3774891 | +0.0006953 | 1.459632 | 1.458618 | +0.001014 |

Direct v1 comparison is unavailable for `4500` and `5000` because the stopped v1 metrics end at `4000`.

## Checkpoint Candidate

- Current export/eval candidate: `iter_0003000`.
- Candidate path: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/checkpoints/iter_0003000`
- Candidate validation: loss/PPL `0.3531853/1.423595`.
- Remote existence check: `iter_0003000`, `iter_0004500`, and `iter_0005000` all exist; each is about `399G`.
- Non-candidate note: `iter_0005000` has a complete checkpoint but validation loss is `+0.0249991` above iter `3000`.

## Export/Eval Prep

- Source HF model: `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Suggested export output path: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/hf_export_iter_0003000`
- Suggested export log path: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/logs/export_iter_0003000.log`
- Suggested model id: `task071-qwen3-30b-a3b-agentic-sft-qwen-chat-iter0003000-hf`
- Export command pattern: use Megatron-Bridge `AutoBridge.from_hf_pretrained(source_hf, trust_remote_code=True).export_ckpt(megatron_path=iter_0003000, hf_path=hf_export_iter_0003000)`.
- Post-export checks: expected HF export size around `57G`, expected `16` safetensors shards, `AutoConfig` and `AutoTokenizer` load, then write `task071_export_manifest.json`.
- Eval path: serve exported HF checkpoint with SGLang using the same corrected Qwen 30B endpoint settings, then run corrected MMLU-Pro, AIME25, and HMMT plus the selected full basket if resources allow.

## Artifacts

- Latest curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves.png`
- Session curve image: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session56_iter5000.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/validation_points.csv`

## Verification

- `python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py` passed.
- `git diff --check` passed.

## Next Action

- Export/register `iter_0003000` as HF, validate the HF artifact, start a SGLang endpoint, and run corrected MMLU-Pro/AIME25/HMMT evaluation while the training run continues to provide more checkpoints for comparison.
