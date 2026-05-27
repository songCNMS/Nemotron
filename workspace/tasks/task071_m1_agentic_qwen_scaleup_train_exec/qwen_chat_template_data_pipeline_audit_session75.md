# Session 75 Qwen Chat Template And Data Pipeline Audit

## Scope

- SFT data-prep rendering path: JSONL `messages` -> `create_masked_messages` -> tokenizer `apply_chat_template` -> packed Parquet loss masks.
- Qwen V4 hard-math recovery artifacts used for the most recent train/export/eval cycle.
- Eval serving path for original Qwen and V4 HF export through SGLang chat completions.

## Findings

1. Current V4 train/eval prompts are aligned for the checked Qwen3-30B-A3B-Instruct-2507 tokenizer.
   - Packed metadata records `chat_template=tokenizer`.
   - Packed metadata records `chat_template_kwargs={"enable_thinking": false, "truncate_history_thinking": false}`.
   - The source tokenizer and V4 exported tokenizer both render the checked prompt as:
     `"<|im_start|>user\nReply exactly: ready<|im_end|>\n<|im_start|>assistant\n"`.
   - Direct `enable_thinking=false`, nested `chat_template_kwargs`, and direct `enable_thinking=true` all produced identical render text for this tokenizer because the saved template has no thinking variables.

2. Current V4 SFT data does not contain hidden `reasoning_content`.
   - `agentic_sft_v0_train.jsonl`: `983397` rows, `0` rows with non-empty `reasoning_content`.
   - `agentic_sft_v0_math_hard_verified_full_solution_train.jsonl`: `184551` rows, `0` rows with non-empty `reasoning_content`.
   - `agentic_sft_v0_math_verified_full_solution_train.jsonl`: `90104` rows, `0` rows with non-empty `reasoning_content`.
   - Math full-solution reasoning is supervised through assistant `content`, not through `<think>...</think>` blocks.

3. A real data-prep bug existed in the generic chat-template helper.
   - The helper passed `chat_template_kwargs={...}` to `tokenizer.apply_chat_template`.
   - HuggingFace tokenizer-native templates commonly read variables such as `enable_thinking` as top-level Jinja variables.
   - Local `super3/nano3` templates read the nested `chat_template_kwargs` object.
   - The helper now passes both shapes: top-level kwargs and nested `chat_template_kwargs`.

4. The most recent corrected eval metrics are not explained by a current Qwen thinking-template mismatch.
   - V4 export template has no `enable_thinking` or `<think>` branches.
   - Original Qwen source tokenizer also has no checked thinking branches.
   - Eval config still pins the intended Qwen chat kwargs, which matters for tokenizer variants whose template does consume these variables.

## Code Changes

- `src/nemotron/data_prep/core/chat_template.py`
  - Added a render-kwargs adapter that expands `enable_thinking` and `truncate_history_thinking` to top-level template variables while preserving nested `chat_template_kwargs`.
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/run_m1_sft_roundtrip_smoke.py`
  - Updated `SmokeTokenizer` to accept top-level template kwargs and merge them into the nested Super3 kwargs object.
- `tests/data_prep/test_chat_template_super3.py`
  - Added a regression test proving tokenizer-native templates receive top-level kwargs on every render call.

## Verification

- `pytest -q tests/data_prep/test_chat_template_super3.py ... test_rl_chat_template_kwargs_consistency.py`: `36 passed`.
- `pytest -q tests/data_prep/test_chat_template_super3.py`: `5 passed`.
- `ruff check` on patched files: passed.
- `py_compile` on patched Python files: passed.
- M1 roundtrip smoke on 5 V4 JSONL rows: passed, `1` packed row, `841` tokens, `298` loss tokens.

