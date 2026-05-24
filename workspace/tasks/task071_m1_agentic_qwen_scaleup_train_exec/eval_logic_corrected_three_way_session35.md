# Session 35 Corrected MMLU-Pro Three-Way Comparison

## Purpose

Session 34 showed that the original Qwen3-30B-A3B MMLU-Pro score from the
task071 regression harness was dominated by truncation and parser failure. This
session applies the same corrected chat JSON answer-only protocol to all three
30B checkpoints so the MMLU-Pro comparison uses one prompt/parser path.

## Protocol

- Dataset: full MMLU-Pro test split, `12032` rows.
- Input rows: lm-eval sample JSONL artifacts from the existing full-selected
  runs on `vm4vpn`.
- Runner: `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_mmlu_pro_eval.py`
- Prompting: chat JSON answer-only.
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`.
- Endpoint: NemTron SGLang exposed to `vm4vpn` as
  `http://127.0.0.1:13000/v1/chat/completions`.
- Serving for SFT checkpoints: `tp=4`, `dp=2`, all 8 H200 GPUs,
  `context_length=4096`, `max_running_requests=32`.

## Commands

`iter0009119`:

```bash
python3 /tmp/task071_run_corrected_mmlu_pro_eval.py \
  --input-root /tmp/task071_vpn_eval_qwen30b_iter0009119_full/mmlu_pro/task071-qwen3-30b-a3b-agentic-sft-iter0009119-hf \
  --output-dir /tmp/task071_qwen30b_iter0009119_mmlu_corrected_full_session35 \
  --endpoint-url http://127.0.0.1:13000/v1/chat/completions \
  --model-id task071-qwen3-30b-a3b-agentic-sft-iter0009119-hf \
  --parallelism 32 \
  --max-tokens 64 \
  --timeout 180
```

Conservative final:

```bash
python3 /tmp/task071_run_corrected_mmlu_pro_eval.py \
  --input-root /tmp/task071_vpn_eval_qwen30b_conservative_iter0010110_full/mmlu_pro/task071-qwen3-30b-a3b-agentic-sft-conservative-iter0010110-hf \
  --output-dir /tmp/task071_qwen30b_conservative_iter0010110_mmlu_corrected_full_session35 \
  --endpoint-url http://127.0.0.1:13000/v1/chat/completions \
  --model-id task071-qwen3-30b-a3b-agentic-sft-conservative-iter0010110-hf \
  --parallelism 32 \
  --max-tokens 64 \
  --timeout 180
```

## Summary

| Model | Old task071 MMLU-Pro | Old invalid rate | Corrected MMLU-Pro | Parsed rate | Stop rate | Correct / Total | Runtime |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original Qwen3-30B-A3B | 0.0000831117 | 0.9998337766 | 0.5617519947 | 1.0 | 1.0 | 6759 / 12032 | 400.620s |
| SFT iter0009119 | 0.0773769947 | 0.8833942819 | 0.5339926862 | 1.0 | 1.0 | 6425 / 12032 | 194.346s |
| Conservative iter0010110 | 0.0103889628 | 0.9834607713 | 0.5275930851 | 1.0 | 1.0 | 6348 / 12032 | 194.002s |

Corrected same-protocol deltas:

| Delta | Value |
|---|---:|
| SFT iter0009119 minus original | -0.0277593085 |
| Conservative iter0010110 minus original | -0.0341589096 |
| Conservative iter0010110 minus SFT iter0009119 | -0.0063996011 |

## Artifacts

- Original summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_summary_original.json`
- Original raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_results_original.jsonl`
- `iter0009119` summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_summary_iter0009119.json`
- `iter0009119` raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_results_iter0009119.jsonl`
- Conservative summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_summary_conservative_iter0010110.json`
- Conservative raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_results_conservative_iter0010110.jsonl`

## Interpretation

The corrected protocol removes the old invalid-output failure mode for all three
models: each run produced `12032/12032` parsed answers and `12032/12032`
`finish_reason=stop`. Under this protocol, the original Qwen checkpoint is
ahead of both SFT checkpoints on MMLU-Pro. The gap is much smaller than the old
harness suggested: original `0.561752`, SFT iter0009119 `0.533993`,
conservative final `0.527593`.

The conclusion is specific to this corrected answer-only MMLU-Pro debug
protocol. It is still not an official Qwen benchmark recipe, but it is a valid
same-protocol task071 comparison and should replace the old invalid-heavy
MMLU-Pro numbers when reasoning about relative model movement.
