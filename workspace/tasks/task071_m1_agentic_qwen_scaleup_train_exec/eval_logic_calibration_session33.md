# Session 33 MMLU-Pro Calibration

## Purpose

Session 32 found that the Qwen3-30B-A3B original baseline MMLU-Pro score was
dominated by harness mismatch: the old run used completions with
`max_gen_toks=32` while asking the model to reason step by step, which made
almost every sample invalid. Session 33 runs a small corrected calibration
before expanding the new setting.

## Endpoint

- Host: `NemTron`
- SGLang session: `task071_qwen30b_original_debug_sglang`
- Model id: `qwen3-30b-a3b-instruct-2507-original-debug`
- Endpoint through vpn: `http://127.0.0.1:13000/v1/chat/completions`
- Context length: `8192`

## Slice

- Source artifacts: `vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_full/mmlu_pro`
- Sampling: first 20 rows from each of 14 MMLU-Pro categories
- Total requests: `280`
- Prompting: chat JSON answer-only
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`

## Result

| Metric | Old task071 MMLU-Pro on same slice | Corrected calibration |
|---|---:|---:|
| Accuracy | 0.000000 | 0.617857 |
| Parsed rate | 0.000000 | 1.000000 |
| Invalid rate | 1.000000 | 0.000000 |
| Stop finish rate | 0.000000 | 1.000000 |

The corrected setting eliminates the parser and truncation failure on this
slice. This does not yet reproduce Qwen's official 78.4 MMLU-Pro number because
the calibration uses a simple answer-only JSON prompt, first-20-per-category
sampling, and does not claim to match Qwen's official evaluation recipe. It is
sufficient to show that the previous original baseline was not a valid
official-comparable metric.

## Artifacts

- Summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_calibration_summary_original.json`
- Raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_calibration_results_original.jsonl`
- Script: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/run_mmlu_corrected_calibration.py`

## Expansion Criteria

Before running full corrected comparisons for original, iter0009119, and final:

- Keep parsed rate at `1.0` on the calibration slice.
- Keep finish reason `stop` on all calibration responses.
- Freeze the exact prompt and parser in a reusable script.
- Decide whether full corrected MMLU-Pro should use answer-only JSON, a
  chain-of-thought prompt with larger generation, or the exact Qwen official
  prompt recipe.
