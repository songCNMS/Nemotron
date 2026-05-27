# Qwen V5 iter1744 corrected eval - Session 79

## Scope

- Checkpoint: `task071_qwen30b_a3b_hard_math_precision_v5/checkpoints/iter_0001744`.
- HF export: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_precision_v5/hf_export_iter_0001744`.
- Model id: `task071-qwen3-30b-a3b-agentic-sft-hard-math-precision-v5-iter0001744-hf`.
- Serving: NemTron SGLang, `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`.
- Remote eval workspace: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session79_corrected_eval`.
- Local copied outputs: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v5_iter1744_session79/remote_corrected_eval_outputs`.

## Execution Notes

- Local SSH tunnel to NemTron was unstable after `/v1/models` checks, causing connection-refused smoke failures. Those failed rows were not used as scores.
- The stable path was to copy corrected-eval runners and input artifacts to NemTron, then call the local endpoint at `http://127.0.0.1:30000/v1/chat/completions`.
- Smoke checks passed on NemTron:
  - MMLU-Pro per-category 1: `14` rows, accuracy `0.6428571428571429`, parsed rate `1.0`.
  - AIME/HMMT 1 row each: `2` rows, both parsed, no exact-normalized correct rows.
- Mid-scale checks passed:
  - MMLU-Pro per-category 20: `280` rows, accuracy `0.6214285714285714`, parsed rate `1.0`.
  - AIME25 30 rows: accuracy `0.0`, parsed rate `1.0`.
  - HMMT 30 rows: exact-normalized correct percent `6.666666666666667`, parsed rate `0.8333333333333334`.

## Full Corrected Metrics

| Benchmark | Rows | Accuracy / Score | Parsed Rate | Finish Summary |
|---|---:|---:|---:|---|
| MMLU-Pro corrected chat JSON | 12032 | 0.5581781914893617 | 1.0 | stop 12032 |
| AIME25 corrected original prompt | 300 | 0.06666666666666667 | 0.94 | stop 282, length 18 |
| HMMT corrected original prompt | 30 | 0.0 | 0.9 | stop 27, length 3 |

Extra math counters:

- AIME25: `20/300` exact-normalized correct, `30/300` responses contain expected answer, average completion tokens `1100.74`.
- HMMT: `0/30` exact-normalized correct, `2/30` responses contain expected answer, average completion tokens `1657.7`.

## Same-Protocol Comparison

| Model | MMLU-Pro | AIME25 | HMMT exact % |
|---|---:|---:|---:|
| Original Qwen Session 47 | 0.562001329787234 | 0.5333333333333333 | 43.333333333333336 |
| V3 iter2200 Session 67 | 0.5525265957446809 | 0.08666666666666667 | 0.0 |
| V4 iter0800 Session 74 | 0.5587599734042553 | 0.08333333333333333 | 3.3333333333333335 |
| V5 iter1744 Session 79 | 0.5581781914893617 | 0.06666666666666667 | 0.0 |

V5 deltas:

- Versus original: MMLU-Pro `-0.0038231382978723397`, AIME25 `-0.4666666666666667`, HMMT exact percent `-43.333333333333336`.
- Versus V3 iter2200: MMLU-Pro `+0.005651595744680803`, AIME25 `-0.020000000000000004`, HMMT exact percent `+0.0`.
- Versus V4 iter0800: MMLU-Pro `-0.0005817819148936128`, AIME25 `-0.016666666666666663`, HMMT exact percent `-3.3333333333333335`.

## Gate Result

- MMLU-Pro gate `>=0.55`: pass.
- AIME25 gate `>=0.20`: fail.
- HMMT gate `>=10.0%`: fail.

V5 preserves broad MMLU-Pro quality, but the stricter hard-math precision sidecar did not recover AIME/HMMT. The next recipe should keep the corrected Qwen chat-template pipeline, then reintroduce broader verified full-solution diversity and add stronger final-answer extraction supervision without using AIME25/HMMT eval labels.

## Cleanup

- Stopped SGLang tmux session `task071_qwen_v5_iter1744_sglang_full_eval` after full eval completed.
- Copied remote eval outputs back to the local debug workspace listed above.
