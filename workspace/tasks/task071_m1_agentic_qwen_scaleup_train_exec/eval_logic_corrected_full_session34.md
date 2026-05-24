# Session 34 Corrected MMLU-Pro Full Run

## Purpose

Session 32 found that the original task071 MMLU-Pro baseline for
Qwen3-30B-A3B-Instruct-2507 mostly measured truncation and parser failure:
the launcher used a completions path with `max_gen_toks=32` while the prompt
asked for step-by-step reasoning. Session 33 confirmed on a 280-sample
calibration slice that a parser-aligned chat prompt removes the invalid-output
failure mode. Session 34 runs the same corrected MMLU-Pro protocol on the full
test split.

## Endpoint

- Host: NemTron
- tmux session: `task071_qwen30b_original_debug_sglang`
- Model id: `qwen3-30b-a3b-instruct-2507-original-debug`
- Endpoint via vpn tunnel: `http://127.0.0.1:13000/v1/chat/completions`
- Served context length: `8192`

## Runner

- Script: `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_mmlu_pro_eval.py`
- Prompting: chat JSON answer-only
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`
- Parallelism: `16`

Command executed on `vm4vpn`:

```bash
python3 /tmp/task071_run_corrected_mmlu_pro_eval.py \
  --input-root /tmp/task071_vpn_eval_qwen30b_original_full/mmlu_pro/qwen3-30b-a3b-instruct-2507-original \
  --output-dir /tmp/task071_qwen30b_original_mmlu_corrected_full \
  --endpoint-url http://127.0.0.1:13000/v1/chat/completions \
  --model-id qwen3-30b-a3b-instruct-2507-original-debug \
  --parallelism 16 \
  --max-tokens 64 \
  --timeout 180
```

## Result

| Metric | Old task071 MMLU-Pro rows | Corrected chat JSON run |
|---|---:|---:|
| Evaluated rows | 12032 | 12032 |
| Accuracy | 0.0000831117 | 0.5617519947 |
| Invalid rate | 0.9998337766 | 0.0 |
| Parsed rate | 0.0001662234 | 1.0 |
| Stop finish rate | 0.0 | 1.0 |
| Correct answers | 1 | 6759 |

Per-category corrected accuracy:

| Category | Correct / Total | Accuracy |
|---|---:|---:|
| biology | 600 / 717 | 0.8368200837 |
| business | 373 / 789 | 0.4727503169 |
| chemistry | 467 / 1132 | 0.4125441696 |
| computer_science | 231 / 410 | 0.5634146341 |
| economics | 606 / 844 | 0.7180094787 |
| engineering | 468 / 969 | 0.4829721362 |
| health | 556 / 818 | 0.6797066015 |
| history | 242 / 381 | 0.6351706037 |
| law | 488 / 1101 | 0.4432334242 |
| math | 700 / 1351 | 0.5181347150 |
| other | 516 / 924 | 0.5584415584 |
| philosophy | 288 / 499 | 0.5771543086 |
| physics | 618 / 1299 | 0.4757505774 |
| psychology | 606 / 798 | 0.7593984962 |

## Artifacts

- Summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_summary_original.json`
- Raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/mmlu_corrected_full_results_original.jsonl`
- Structured manifest entry: `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_full_non_dry_results_qwen3_30b_a3b_instruct_2507_original.yaml`

## Interpretation

The old original Qwen3-30B-A3B MMLU-Pro score of `0.0000831117` is not a valid
model-quality signal. It is dominated by the old harness configuration, which
truncated nearly every response before a parser-readable answer appeared. The
corrected full run reaches `0.5617519947` with complete parsing and no length
finish events.

This is still not an official Qwen-comparable score. The corrected protocol uses
a simple answer-only JSON chat prompt rather than the exact official recipe, so
it should be used to debug task071 evaluation logic and to define the next
full-model corrected comparison, not as a replacement for official MMLU-Pro
reporting.
