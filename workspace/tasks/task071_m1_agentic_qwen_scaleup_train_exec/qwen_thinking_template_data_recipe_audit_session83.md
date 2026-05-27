# Qwen Thinking / Template / Data Recipe Audit - Session 83

## Question

Do AIME/HMMT failures come from misusing training data or chat templates, such as omitting thinking tokens, disabling the Qwen thinking path, or training with the wrong template so the fine-tuned model stops reasoning and jumps to wrong answers?

## Short Answer

For the current V3/V4/V5/V6 Qwen SFT runs, no. I do not see evidence that a live chat-template mismatch or dropped `reasoning_content` field is the root cause.

There were historical mistakes:

- `task071_qwen30b_a3b_math_final_answer_v1` packed data used `chat_template=super3` and lacked the Qwen chat-template metadata. That run was identified in Session 50 and replaced by Qwen-tokenizer packing.
- Earlier math recipes also over-emphasized answer formatting. That explained parser-format improvement without hard-math recovery.

For the current runs, the stronger diagnosis is:

- The model is trained on Qwen tokenizer rendering, not Super3 rendering.
- The checked Qwen tokenizer has no `<think>`, `reasoning_content`, or `enable_thinking` branches, so `enable_thinking=false` does not remove a hidden thinking prefix for this model.
- Current M0/M1 math converters put full solution traces into assistant `content`, not `reasoning_content`.
- The supervised math traces are much shorter and less search-like than original Qwen's successful AIME/HMMT responses, and training uses `seq_length=4096` while corrected eval gives the original model up to `8192` completion tokens.

So the failure is a data-distribution / recipe mismatch: SFT teaches shorter, parser-readable solutions and reduces the original model's long self-correction behavior.

## Template Evidence

Actual packed metadata:

| Run | `chat_template` | kwargs | pack / train seq length |
|---|---|---|---:|
| Qwen chat v2 | `tokenizer` | `enable_thinking=false`, `truncate_history_thinking=false` | 4096 |
| V3 reasoning replay | `tokenizer` | `enable_thinking=false`, `truncate_history_thinking=false` | 4096 |
| V4 hard recovery | `tokenizer` | `enable_thinking=false`, `truncate_history_thinking=false` | 4096 |
| V5 hard precision | `tokenizer` | `enable_thinking=false`, `truncate_history_thinking=false` | 4096 |
| V6 hard balanced | `tokenizer` | `enable_thinking=false`, `truncate_history_thinking=false` | 4096 |

The old bad run:

| Run | Packed metadata / run config |
|---|---|
| `task071_qwen30b_a3b_math_final_answer_v1` | metadata lacked chat-template fields; packed run config recorded `chat_template=super3` |

Tokenizer check:

- `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507/tokenizer_config.json` has a `2630` char chat template.
- It contains no `enable_thinking`, no `reasoning_content`, and no `<think>` / `</think>` branch.
- Rendering a simple prompt with `{}`, `enable_thinking=false`, and `enable_thinking=true` produces the same text:
  `<|im_start|>user\n...<|im_end|>\n<|im_start|>assistant\n`
- V4/V5 exported `chat_template.jinja` on NemTron also has no thinking branches.

Therefore, for this concrete Qwen3-30B-A3B-Instruct-2507 tokenizer, `enable_thinking=false` is not forcing the model to skip a template-level thinking section.

## Data Field Evidence

M0 math converters:

- GSM8K stores the full source answer in `extra_env_info.reference_solution`.
- NuminaMath stores the full source `solution` in `extra_env_info.reference_solution`.
- M1 `assistant_for_reasoning` copies `reference_solution` into assistant `content`, stripping GSM8K verifier markers and appending `Final answer: \boxed{...}` only when needed.

Current M1 JSONL scans:

| Slice | Rows | Non-empty `reasoning_content` | `<think>` tags |
|---|---:|---:|---:|
| V3 base | 983397 | 0 | 0 |
| V3 verified full solution | 544967 | 0 | 0 |
| V4 hard verified | 184551 | 0 | 0 |
| V5 hard verified | 68583 | 0 | 0 |
| V6 hard verified | 68583 | 0 | 0 |
| V6 broad verified | 107666 | 0 | 0 |

This means there were no hidden thinking tokens in `reasoning_content` for the current pipeline to omit. The reasoning supervision is visible content.

Loss-mask check:

- `chat_sft_shard_core._tokenize_chunks_with_mask` sets loss mask `1` for assistant chunks and `0` for system/user/tool chunks.
- Tests pin that tool role tokens stay at loss mask `0`.
- The first packed rows decoded from V3/V4/V5/V6 contain Qwen `<|im_start|>` / `<|im_end|>` delimiters, no Super3-only text, and no `<think>` tags.

## Recipe Evidence

Training schedule:

| Run | Epochs | LR | Train seq length |
|---|---:|---:|---:|
| V3 | 0.25 | `5e-7` | 4096 |
| V4 | 0.20 | `3e-7` | 4096 |
| V5 | 0.20 | `2e-7` | 4096 |
| V6 | 0.20 | `2e-7` | 4096 |

Math sidecar scale:

| Run | Main math sidecars in blend |
|---|---|
| V3 | `544967` verified full-solution rows, `16099` format repair rows, `6` final-answer aux rows |
| V4 | `184551` hard verified rows, `90104` broad verified rows |
| V5 | `68583` hard verified rows |
| V6 | `68583` hard verified rows, `107666` broad verified rows, `9659` format repair rows, `1` final-answer aux row |

Current V4/V5/V6 are not dominated by final-answer-only auxiliary data. The issue is the quality and length distribution of the visible solution traces.

Representative assistant content lengths:

| Slice | p50 chars | p90 chars |
|---|---:|---:|
| V3 verified | 898 | 1899 |
| V4 hard verified | 1198 | 2226 |
| V5 hard verified | 1468 | 2413 |
| V6 hard verified | 1465 | 2412 |
| V6 broad verified | 766 | 1561 |

Original corrected eval successful outputs are much longer:

- Original AIME avg completion tokens: `5736.9`.
- Original HMMT 8192 avg completion tokens: `6860.8`.
- Same-row `aime_01_r01`: original uses `4821` completion tokens to reach correct `293`; SFT variants use about `551-795` tokens and return wrong `145` or `73`.

## Ruled-Out Hypotheses

- Current runs are not using Super3 chat-template packing.
- Current Qwen tokenizer does not expose a `<think>` template path that `enable_thinking=false` suppresses.
- Current M1 math data does not contain non-empty `reasoning_content` that is being dropped.
- Current V4/V5/V6 are not mainly final-answer-only auxiliary training.
- Parser failure is not the main reason: SFT parsed rate is higher than original parsed rate, but parsed answers are wrong.

## Confirmed / Likely Issues

1. Historical template misuse existed and was real for `math_final_answer_v1`, but it is not the current V3/V4/V5/V6 root cause.
2. The current training recipe compresses the model's hard-math response style: visible solution traces are much shorter than the original model's successful AIME/HMMT generations.
3. `seq_length=4096` plus `pack_size=4096` does not train the 8k-token search/self-correction trajectories that corrected eval exposes in the original model.
4. The sidecar filters verify format/source metadata, not proof correctness. They can train plausible but wrong shortcut reasoning.
5. MMLU-Pro and validation loss remain weak gates for hard math; they do not detect the loss of long AIME/HMMT reasoning.

## Recommendation

Do not treat this as a current chat-template bug. The next recipe should explicitly target long hard-math reasoning retention:

- Build a pilot set of verified long AIME/HMMT-style full-solution traces from public training-like sources, excluding heldout eval labels.
- Increase hard-math sequence length or split a dedicated long-context hard-math stage so supervision can cover 8k-style solutions.
- Filter sidecars with stronger answer correctness checks, not only boxed-answer presence.
- Add original-model retention traces for hard math, then gate candidates by same-row AIME/HMMT parsed-correct ratio and average completion length.
- Keep Qwen tokenizer template packing, but add a guard that fails if future tokenizer templates introduce `<think>` / `enable_thinking` branches while M1 still has no `reasoning_content`.
