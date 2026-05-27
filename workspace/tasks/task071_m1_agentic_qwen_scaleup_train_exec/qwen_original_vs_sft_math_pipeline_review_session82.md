# Qwen Original vs SFT AIME/HMMT Pipeline Review - Session 82

## Scope

This review checks why AIME25 and HMMT scores differ sharply between the original Qwen3-30B-A3B-Instruct-2507 model and the task071 fine-tuned checkpoints. It covers:

- corrected math eval runner and scoring protocol
- raw original-model and SFT-model outputs on the same benchmark rows
- Qwen chat-template and packed-data metadata
- M1 hard-math sidecar data shape
- likely root causes and concrete gates for the next recipe

## Verdict

The AIME/HMMT gap is not explained by a parser bug or by the current Qwen chat-template contract. The corrected eval parser actually covers SFT outputs much better than original outputs.

The main failure is a real behavior regression introduced by SFT: the fine-tuned models learn to emit short, well-formatted boxed answers, but the reasoning is shallow and often wrong. The original model spends far more generation budget on long self-corrective reasoning; when the runner can parse a final box, those original parsed rows are much more likely to be correct.

## Eval Protocol Check

The corrected math runner `run_corrected_math_full_eval.py` uses the same protocol for original and SFT models:

- OpenAI-compatible chat endpoint with a single user message.
- `temperature=0.0`, `top_p=1e-5`.
- default math generation cap `max_tokens=8192`.
- final prediction is the last parsed `\boxed{...}` span.
- answer comparison uses normalized exact match.
- summaries include `parsed_rows`, `correct_rows`, finish reasons, and average completion tokens.

For the corrected 30B comparisons, SGLang was served with a 16k context window. The runner and protocol are therefore sufficient to expose the difference between "not parsed" and "parsed but wrong".

## Raw Metric Evidence

| Run | Task | Parsed | Correct | Finish reasons | Avg completion tokens |
|---|---:|---:|---:|---|---:|
| Original Session 38 | AIME25, 300 rows | 184 | 155 | stop 173, length 127 | 5736.9 |
| Original Session 38, HMMT 8192 | HMMT, 30 rows | 17 | 8 | stop 14, length 16 | 6860.8 |
| SFT iter0009119 | AIME25, 300 rows | 10 | 0 | stop 300 | 3.6 |
| SFT iter0009119 | HMMT, 30 rows | 1 | 0 | stop 30 | 3.9 |
| Conservative iter0010110 | AIME25, 300 rows | 298 | 10 | stop 298, length 2 | 733.8 |
| Conservative iter0010110 | HMMT, 30 rows | 30 | 2 | stop 30 | 791.2 |
| Qwen chat iter3000 | AIME25, 300 rows | 278 | 20 | stop 278, length 22 | 1213.4 |
| Qwen chat iter3000 | HMMT, 30 rows | 30 | 0 | stop 30 | 776.2 |
| V3 iter2200 | AIME25, 300 rows | 282 | 26 | stop 282, length 18 | 1054.6 |
| V3 iter2200 | HMMT, 30 rows | 30 | 0 | stop 30 | 719.7 |
| V4 iter0800 | AIME25, 300 rows | 284 | 25 | stop 284, length 16 | 1079.7 |
| V4 iter0800 | HMMT, 30 rows | 29 | 1 | stop 29, length 1 | 1141.4 |
| V5 iter1744 | AIME25, 300 rows | 282 | 20 | stop 282, length 18 | 1100.7 |
| V5 iter1744 | HMMT, 30 rows | 27 | 0 | stop 27, length 3 | 1657.7 |

Key ratios:

- Original AIME parsed rows are correct at `155/184 = 84.2%`.
- Original HMMT parsed rows are correct at `8/17 = 47.1%`.
- V3 AIME parsed rows are correct at `26/282 = 9.2%`; V3 HMMT is `0/30`.
- V4/V5 show the same pattern: high parse coverage, low hard-math correctness.

This means the parser is not hiding SFT performance. It is mostly helping SFT by recognizing the short boxed outputs.

## Same-Row Evidence

For sample `aime_01_r01`, expected answer `293`:

| Run | Parsed prediction | Correct | Completion tokens | Output shape |
|---|---:|---:|---:|---|
| Original Session 38 | 293 | true | 4821 | long derivation, self-checks, final box |
| SFT iter0009119 | none | false | 3 | degenerate short output |
| Conservative iter0010110 | 145 | false | 701 | short wrong rectangle-area shortcut |
| Qwen chat iter3000 | 145 | false | 551 | same wrong shortcut |
| V3 iter2200 | 73 | false | 591 | short wrong coordinate setup |
| V4 iter0800 | 145 | false | 761 | same wrong shortcut |
| V5 iter1744 | 145 | false | 795 | same wrong shortcut |

The original model reaches the correct `\boxed{293}` after thousands of tokens. The SFT variants terminate much earlier and repeatedly converge to plausible but wrong boxed answers. This is a model-behavior difference, not an eval artifact.

## Training Data and Template Review

The current Qwen-specific packed artifacts for V3/V4/V5/V6 record:

- `chat_template=tokenizer`
- `chat_template_kwargs.enable_thinking=false`
- `chat_template_kwargs.truncate_history_thinking=false`
- `pack_size=4096`

Session 75 also verified that the source Qwen tokenizer and exported checkpoints render the checked prompt identically, and that the saved tokenizer template does not branch on `enable_thinking` or `<think>`. Current runs are therefore not explained by the older Super3-template mismatch.

The M1 hard-math sidecars are much shorter than the original model's successful eval traces:

| Data slice | Rows | Boxed rate | Short under 1200 chars | Assistant chars p50 | p90 |
|---|---:|---:|---:|---:|---:|
| V3 base | 983397 | 0.882 | 0.659 | 902 | 2137 |
| V3 verified | 544967 | 1.000 | 0.691 | 898 | 1899 |
| V4 hard | 184551 | 1.000 | 0.501 | 1198 | 2226 |
| V5 hard | 68583 | 1.000 | 0.252 | 1468 | 2413 |
| V6 hard | 68583 | 1.000 | 0.253 | 1465 | 2412 |
| V6 broad | 107666 | 1.000 | 0.809 | 766 | 1561 |
| V6 repair | 9659 | 1.000 | 0.485 | 1232 | 2493 |

By contrast, the original model's successful AIME/HMMT eval outputs often use around 5k to 7k completion tokens. The supervised data is teaching a much shorter response distribution than the one the original model uses to solve hard math.

There are also sidecar quality risks:

- Some rows contain malformed final-answer text such as nested or duplicated boxed formatting.
- The "verified" status is based on dataset metadata and deterministic filters, not a proof-level verifier.
- V6 reintroduced many short broad rows, which can reinforce fast boxed-answer behavior even when the hard sidecar is stricter.

## Root Causes

1. Output-policy compression: SFT shifts the model from long self-corrective reasoning to short boxed-answer responses.
2. Reasoning supervision length mismatch: `pack_size=4096` and short sidecar solutions do not preserve 8k-style solving trajectories seen in original correct outputs.
3. Sidecar verification is too weak for AIME/HMMT recovery: format and metadata checks are not enough to guarantee proof-quality reasoning.
4. Validation loss and MMLU-Pro are not hard-math gates: V3/V4/V5 can pass or nearly match MMLU-Pro while still failing AIME/HMMT.
5. Pilot success criteria were too loose: a pipeline smoke that produces parsed answers is insufficient when the benchmark target is hard-math correctness.

## What Is Not the Main Cause

- Not a pure parser issue: SFT parsed rates are much higher than original parsed rates, but SFT parsed answers are mostly wrong.
- Not the current Qwen chat-template mismatch: current packed metadata and Session 75 audit show tokenizer-native rendering with thinking disabled.
- Not only context length: corrected 30B evals used 16k context and 8192 generation caps; original still outperforms SFT on hard math.
- Not random row noise: repeated AIME rows show stable wrong-answer clusters for SFT variants.

## Recommended Gates and Fixes

- Gate every hard-math recipe with paired original-vs-candidate corrected mini eval on the same rows before any full 30B run.
- Require nonzero AIME/HMMT correctness on the pilot, not just successful requests or high parsed rate.
- Track parsed-correct ratio and average completion tokens as first-class metrics.
- Add policy-retention data from original-model successful long traces on public training-like hard-math prompts, excluding heldout AIME25/HMMT labels.
- Increase or separate hard-math packing length for long-solution replay, or train a stage that can supervise longer solution trajectories.
- Filter sidecar rows by solution length, answer-location, malformed boxing, reasoning structure, and verifier or majority consistency.
- Keep MMLU-Pro as a broad regression guard, but do not use it as the hard-math promotion gate.

## Operational Decision

Do not restart V6 full 30B training from the current recipe. The right next action is a smaller end-to-end pilot with stronger long-solution/verified reasoning data and a corrected AIME/HMMT gate before scale-up.
