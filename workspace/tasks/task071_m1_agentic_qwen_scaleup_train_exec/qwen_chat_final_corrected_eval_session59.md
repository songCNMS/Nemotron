# Qwen Chat-Aligned Final Metrics and Iter 3000 Corrected Eval - Session 59

## Training Completion

Run: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`

- Final train iteration: `8740/8740`
- Final checkpoint: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/checkpoints/iter_0008740`
- Exported eval candidate: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/hf_export_iter_0003000`
- Final metric curve: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session59_final.png`
- Max skipped/nan iterations: `0/0`

Validation summary:

| Iteration | Validation loss | PPL |
|---:|---:|---:|
| 3000 | 0.3531853 | 1.423595 |
| 5500 | 0.3557427 | 1.427240 |
| 6000 | 0.3681244 | 1.445022 |
| 8500 | 0.4024086 | 1.495422 |
| 8740 | 0.3842467 | 1.468508 |

Decision: iter `3000` remains the eval/export candidate. The final checkpoint is worse on validation loss.

## Parser Fix

The final Megatron validation line uses this format:

`validation loss at iteration 8740 on validation set | lm loss value: ...`

`plot_qwen_sft_metrics.py` now accepts the optional `on validation set` phrase, so final validation points are included in `validation_points.csv`, plots, and `health_summary.json`.

## Full Corrected Eval

Endpoint:

- Tmux session: `task071_qwen_chat_iter3000_sglang_full_eval`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-qwen-chat-iter0003000-hf`
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`
- Endpoint status: `/v1/models` returned `max_model_len=16384`

MMLU-Pro corrected full:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_chat_iter3000_session59/mmlu_corrected_full`
- Rows: `12032`
- Prompting: chat JSON answer-only
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`
- Status: `ok=12032/12032`
- Parsed rate: `1.0`
- Accuracy: `0.5340757978723404`

Math corrected full:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_chat_iter3000_session59/math_corrected_full`
- Prompting: original prompts
- Generation: `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`

| Task | Rows | Status OK | Stop | Length | Parsed rate | Score |
|---|---:|---:|---:|---:|---:|---:|
| AIME25 | 300 | 300 | 278 | 22 | 0.9266666666666666 | 0.06666666666666667 |
| HMMT | 30 | 30 | 30 | 0 | 1.0 | 0.0 |

## Comparison

Original reference is Session 47 corrected eval:

- MMLU-Pro: `0.562001329787234`
- AIME25: `0.5333333333333333`
- HMMT exact percent: `43.333333333333336`

| Metric | Original | Iter3000 | Delta |
|---|---:|---:|---:|
| MMLU-Pro corrected accuracy | 0.562001329787234 | 0.5340757978723404 | -0.027925531914893636 |
| AIME25 corrected accuracy | 0.5333333333333333 | 0.06666666666666667 | -0.4666666666666667 |
| HMMT corrected exact percent | 43.333333333333336 | 0.0 | -43.333333333333336 |

Interpretation:

- Qwen-chat aligned SFT at iter3000 keeps MMLU-Pro close to the earlier 30B SFT level and well below the original model by about 2.8 points.
- AIME/HMMT parser coverage is much better than the old regression harness, but math correctness remains far below original.
- The added math final-answer supervision did not recover original-model math ability in this run; it mostly improved parseability.

## Cleanup

After full corrected eval, `task071_qwen_chat_iter3000_sglang_full_eval` was stopped.

- Port `30000`: clear
- GPU state: all 8 H200 GPUs released
