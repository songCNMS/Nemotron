# Qwen Chat-Aligned Math Strategy Review - Session 60

## Conclusion

The Qwen-chat aligned SFT run fixed a large part of the response-format problem, but it did not recover Qwen's original math reasoning quality. The corrected full eval shows high parser coverage on AIME25 and HMMT, while exact correctness remains far below the original Qwen3-30B-A3B baseline.

This means the next training revision should not keep increasing final-answer-only exposure. It should rebalance toward verified full-solution math reasoning, keep final-answer formatting as a weak auxiliary signal, and choose checkpoints through corrected eval gates rather than validation loss alone.

## Evidence

Training run: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`

| Checkpoint | Validation loss | PPL | Decision |
|---|---:|---:|---|
| iter_0003000 | 0.3531853 | 1.423595 | Best validation and exported eval candidate |
| iter_0008740 | 0.3842467 | 1.468508 | Final checkpoint, worse than iter_0003000 |

Corrected full eval for `iter_0003000`:

| Benchmark | Original corrected score | iter_0003000 score | Delta | iter_0003000 parsed rate |
|---|---:|---:|---:|---:|
| MMLU-Pro | 0.562001329787234 | 0.5340757978723404 | -0.027925531914893636 | 1.0 |
| AIME25 | 0.5333333333333333 | 0.06666666666666667 | -0.4666666666666667 | 0.9266666666666666 |
| HMMT | 43.333333333333336 | 0.0 | -43.333333333333336 | 1.0 |

Error-shape audit from the corrected math result JSONL:

| Task | Rows | Stop | Length | Parsed | Correct | Contains expected answer | Boxed-value shape |
|---|---:|---:|---:|---:|---:|---:|---|
| AIME25 | 300 | 278 | 22 | 278 | 20 | 39 | 268 rows with 1 box, 10 rows with 2 boxes, 22 rows with no box |
| HMMT | 30 | 30 | 0 | 30 | 0 | 1 | 29 rows with 1 box, 1 row with 2 boxes |

Observed failure patterns:

- AIME repeats are deterministic at temperature `0.0`: wrong reasoning often repeats the same wrong boxed answer across all 10 repeats for a problem.
- AIME has `contains_expected_rows=39` but only `correct_rows=20`, so some generations mention the expected value somewhere while selecting a different final boxed answer.
- HMMT has perfect parsed rate and all rows finish by `stop`, but `correct_rows=0`, which rules out a pure parser or length-limit explanation.
- MMLU-Pro is only moderately below original, so the failure is concentrated in math reasoning rather than a global serving or tokenizer collapse.

## Diagnosis

The current math-final-answer sidecar likely over-trained a narrow behavior: produce a parser-readable final answer. It did not provide enough reliable, high-quality reasoning traces to preserve the original model's solution ability on competition math.

The validation set is also not sufficient as the checkpoint selector for this objective. `iter_0003000` is the best validation checkpoint, but it is still poor on AIME/HMMT. Running beyond `iter_0003000` worsens validation, so the next experiment should improve the data mix and supervision target instead of extending this run.

The useful part of this run is still clear: Qwen tokenizer chat-template packing with `enable_thinking=false` works, the training loop is stable, and the parser-readable answer format can be learned. The missing piece is reasoning-quality supervision.

## Next Training Strategy

Start from the original Qwen3-30B-A3B-Instruct-2507 checkpoint, not from `iter_0003000` or `iter_0008740`.

Data mix:

- Keep the agentic SFT base blend for search, coding, general tool calling, and reasoning tasks at its normal weight.
- Add a verified math reasoning replay slice using rows with complete reference solutions. Prefer `extra_env_info.reference_solution` when available, preserve the reasoning trace, and end with `Final answer: \boxed{...}` only when needed.
- Down-weight final-answer-only or answer-normalization sidecar rows to `0.15-0.25` effective weight and cap them to at most `10-15%` of math tokens.
- Keep repair/negative formatting rows as an auxiliary slice under `5%` of tokens, not as a main math training signal.
- Hold out competition-style rows without trusted solutions for eval/dev unless a verified solution trace is available.

Training schedule:

- Use the same Qwen tokenizer chat contract: `chat_template=tokenizer`, `enable_thinking=false`, `truncate_history_thinking=false`.
- Use a shorter first pass from the original checkpoint: target `0.20-0.30` epoch over the new blend, `global_batch_size=8`, sequence length `4096`, save/eval interval `500`.
- Use a conservative LR for the first recovery run: `optimizer.lr=5e-7`, `optimizer.min_lr=1e-7`, warmup `100`.
- Export candidates around `iter_2000`, `iter_3000`, and `iter_3500`; do not rely on the final checkpoint if corrected eval gates disagree.

Eval gates:

- Run corrected MMLU-Pro mini plus corrected math mini after each candidate export.
- Math mini should include fixed AIME/HMMT rows with original prompts, `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`, and the same exact-normalized parser used in Session 59.
- Promote to full corrected eval only if mini math improves while MMLU-Pro remains close to original.

First recovery targets:

| Metric | Minimum recovery gate |
|---|---:|
| MMLU-Pro corrected full | >= 0.55 or no more than 0.02 below original |
| AIME25 corrected full | >= 0.20 |
| HMMT corrected full | >= 10.0 exact-normalized percent |
| AIME/HMMT parsed rate | >= 0.90 |
| Training health | skipped/nan remains 0 |

## Concrete Next Work

1. Add a v3 data-prep entry that separates math rows into `verified_full_solution`, `final_answer_aux`, `format_repair`, and `heldout_eval` buckets.
2. Regenerate packed Qwen-chat artifacts with bucket counts and token counts recorded in metadata.
3. Generate `task071_qwen30b_a3b_math_reasoning_replay_v3` scripts from the original Qwen checkpoint with the shorter conservative schedule.
4. Run local data validation, sync to NemTron, start training, and evaluate exported candidates through the corrected mini gates before any full-basket run.
