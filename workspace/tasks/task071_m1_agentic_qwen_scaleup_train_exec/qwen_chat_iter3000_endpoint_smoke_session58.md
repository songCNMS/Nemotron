# Qwen Chat-Aligned Iter 3000 Endpoint Smoke - Session 58

## Runtime State

Training run: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`

- Active training tmux: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Latest checkpoint marker during this session: `6000`
- Validation@6000: loss/PPL `0.3681244/1.445022`
- Best observed validation remains iter `3000`: loss/PPL `0.3531853/1.423595`
- Refreshed plot: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session58_iter6000.png`

## Endpoint Attempts

Target HF export:

`/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/hf_export_iter_0003000`

First attempt:

- `tp=4`, `dp=2`, `context_length=16384`
- `mem_fraction_static=0.25`
- `max_running_requests=1`
- `max_total_tokens=16384`
- Result: failed during memory-pool init with `Not enough memory. Please try to increase --mem-fraction-static`
- Training health after failure: training continued, GPU memory returned to the pre-serving level

Successful smoke endpoint:

- Tmux session: `task071_qwen_chat_iter3000_sglang_smoke`
- Log: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/logs/sglang_iter0003000_concurrent_smoke_mem035.log`
- `tp=4`, `dp=2`, `context_length=16384`
- `mem_fraction_static=0.35`
- `max_running_requests=1`
- `max_total_tokens=12288`
- `--disable-cuda-graph`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-qwen-chat-iter0003000-hf`

The endpoint returned `/v1/models` with `max_model_len=16384`. Chat smoke returned exact `ready`.

## Corrected Eval Smoke

MMLU-Pro corrected smoke:

- Input: Session 46 original MMLU-Pro sample JSONL copied from `vm4vpn`
- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_chat_iter3000_session58/mmlu_smoke_percat1`
- Rows: `14` total, one per category
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`, `parallelism=1`
- Status: `ok=14/14`
- Parsed rate: `1.0`
- Corrected accuracy: `0.5714285714285714` (`8/14`)
- Old same-row invalid rate: `1.0`

Math corrected smoke:

- AIME score cache: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db`
- HMMT JSONL: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/hmmt_output.jsonl`
- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_chat_iter3000_session58/math_smoke_1each`
- Rows: AIME25 `1`, HMMT `1`
- Prompt variant: original
- Generation: `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`, `parallelism=1`
- Status: `ok=2/2`
- Finish: `stop=2/2`
- Parsed rate: `1.0`
- Exact-normalized correctness: `0/2`

## Cleanup

The smoke endpoint was stopped after validation to avoid ongoing contention with the active training job.

- Port `30000`: clear after cleanup
- GPU memory: returned to training-only levels
- Training health after cleanup: continued through at least iter `6230/8740`, skipped/nan `0/0`

## Full Eval Entry

For full corrected comparison, start the same endpoint in a dedicated serving window or after training completion:

- `tp=4`, `dp=2`, `context_length=16384`
- Start with `mem_fraction_static=0.35`, `max_running_requests=1`, `max_total_tokens=12288`, `--disable-cuda-graph`
- If no training process is active, restore the prior full-eval shape with larger static memory and request concurrency
- Run corrected MMLU-Pro full, then AIME25/HMMT full, and compare against Session 47 original corrected metrics
