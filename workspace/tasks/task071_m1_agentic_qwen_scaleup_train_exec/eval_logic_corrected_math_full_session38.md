# Session 38 Corrected AIME/HMMT Full Comparison

## Purpose

Sessions 36 and 37 showed that the previous task071 AIME25/HMMT numbers were
strongly affected by output truncation and final-answer parser coverage. This
session records a corrected full math comparison config and reruns the full
AIME25/HMMT comparison on the three Qwen3-30B-A3B checkpoints.

## Protocol

Tracked config:
`src/nemotron/recipes/super3/stage3_eval/config/m1_corrected_math_comparison.yaml`

Runner:
`workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py`

Common runtime:

| Setting | Value |
|---|---|
| Endpoint shape | OpenAI chat completions |
| SGLang context length | `16384` |
| Parallelism | `tp=4`, `dp=2`, 8 H200 GPUs |
| AIME sample | 300 rows, 30 AIME 2025 problems x10 repeats |
| HMMT sample | 30 HMMT February 2025 entries |
| Prompt variant | original benchmark prompts |
| AIME max tokens | `8192` |
| HMMT max tokens | `8192` |
| Sampling | `temperature=0.0`, `top_p=1e-5` |
| Scoring | exact-normalized boxed answer match |

For HMMT, exact-normalized scoring is a stricter debug metric than the original
nemo-skills symbolic scorer; parser coverage is reported separately so the score
can be interpreted with the final-answer contract.

## Results

| Model | AIME old score | AIME corrected | AIME parsed | AIME finish | HMMT old symbolic | HMMT corrected exact | HMMT parsed | HMMT finish |
|---|---:|---:|---:|---|---:|---:|---:|---|
| Original Qwen3-30B-A3B | 0.166667 | 0.516667 | 0.613333 | stop=173, length=127 | 6.666667 | 26.666667 | 0.566667 | stop=14, length=16 |
| SFT iter0009119 | 0.0 | 0.0 | 0.033333 | stop=300 | 0.0 | 0.0 | 0.033333 | stop=30 |
| Conservative iter0010110 | 0.033333 | 0.033333 | 0.993333 | stop=298, length=2 | 0.0 | 6.666667 | 1.0 | stop=30 |

Same-protocol corrected deltas:

| Delta | AIME corrected | HMMT corrected exact percent |
|---|---:|---:|
| SFT iter0009119 minus original | -0.516667 | -26.666667 |
| Conservative iter0010110 minus original | -0.483333 | -20.000000 |
| Conservative iter0010110 minus SFT iter0009119 | +0.033333 | +6.666667 |

## Artifacts

- Original AIME summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_original_session38/summary.json`
- Original AIME raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_original_session38/results.jsonl`
- Original HMMT 8192 summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_original_hmmt8192_session38/summary.json`
- Original HMMT 8192 raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_original_hmmt8192_session38/results.jsonl`
- SFT iter0009119 summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_iter0009119_session38/summary.json`
- SFT iter0009119 raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_iter0009119_session38/results.jsonl`
- Conservative iter0010110 summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_conservative_iter0010110_session38/summary.json`
- Conservative iter0010110 raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/corrected_math_full_conservative_iter0010110_session38/results.jsonl`

## Interpretation

The original checkpoint improves sharply under the corrected long-output math
protocol: AIME rises from `0.166667` to `0.516667`, and HMMT exact-normalized
correct percent rises from the previous symbolic `6.666667` regression score to
`26.666667`. It still has substantial truncation at 8192 tokens, so these
numbers are task071 corrected-debug metrics rather than official Qwen metrics.

The SFT iter0009119 checkpoint usually stops after only a few tokens and rarely
emits a boxed answer under the original math prompts, giving near-zero parser
coverage and zero corrected accuracy.

The conservative iter0010110 checkpoint restores parser coverage almost
completely, but most answers are wrong: AIME remains `0.033333`, while HMMT exact
correctness reaches `6.666667`. This indicates the conservative strategy fixed
the final-answer format more than the underlying competition-math accuracy.
