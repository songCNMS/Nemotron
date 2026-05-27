# Qwen V7 Iter 0782 Corrected Eval - Session 91

## Scope

- Run: `task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar`
- HF export: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/hf_export_iter_0000782`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-hard-math-long-reasoning-v7-full-sidecar-iter0000782-hf`
- Remote eval workspace: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session91_corrected_eval`
- Local copied outputs: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v7_iter0782_session91/remote_corrected_eval_outputs`

## Serving

- Tmux session: `task071_qwen_v7_iter0782_sglang_eval`
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`
- `/v1/models`: returned `max_model_len=16384`
- Chat smoke: prompt `Reply exactly: ready` returned exact `ready`

The endpoint was stopped after full eval completed.

## Full Corrected Metrics

| Benchmark | Rows | Accuracy / Score | Parsed Rate | Finish Summary |
|---|---:|---:|---:|---|
| MMLU-Pro corrected chat JSON | 12032 | 0.5601728723404256 | 1.0 | stop 12032 |
| AIME25 corrected original prompt | 300 | 0.21 | 0.91 | stop 273, length 27 |
| HMMT corrected original prompt | 30 | 16.666666666666668% | 0.5666666666666667 | stop 15, length 15 |

Extra math counters:

- AIME25: `63/300` exact-normalized correct, `83/300` responses contain expected answer, average completion tokens `2094.5433333333335`.
- HMMT: `5/30` exact-normalized correct, `6/30` responses contain expected answer, average completion tokens `5846`.

## Same-Protocol Comparison

| Model | MMLU-Pro | AIME25 | HMMT exact % |
|---|---:|---:|---:|
| Original Qwen Session 47 | 0.562001329787234 | 0.5333333333333333 | 43.333333333333336 |
| V3 iter2200 Session 67 | 0.5525265957446809 | 0.08666666666666667 | 0.0 |
| V4 iter0800 Session 74 | 0.5587599734042553 | 0.08333333333333333 | 3.3333333333333335 |
| V5 iter1744 Session 79 | 0.5581781914893617 | 0.06666666666666667 | 0.0 |
| V7 iter0782 Session 91 | 0.5601728723404256 | 0.21 | 16.666666666666668 |

V7 deltas:

- Versus original: MMLU-Pro `-0.0018284574468083958`, AIME25 `-0.3233333333333333`, HMMT exact percent `-26.666666666666668`.
- Versus V5 iter1744: MMLU-Pro `+0.001994680851063905`, AIME25 `+0.14333333333333334`, HMMT exact percent `+16.666666666666668`.

## Gate Result

- MMLU-Pro gate `>=0.55`: pass.
- AIME25 gate `>=0.20`: pass.
- HMMT gate `>=10.0%`: pass.

V7 is the first 30B SFT candidate in this sequence to pass all three corrected gates. It still trails original Qwen on AIME/HMMT, and HMMT has low parsed rate because half of the rows hit the 8192-token generation cap. The useful next action is to inspect correct versus length-truncated HMMT/AIME rows, then tune the V7 hard-row filter or generation-length policy before a production-scale eval basket.
