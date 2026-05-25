# Chat-Template Consistency Review (2026-05-24)

Author: code review by `intern_nemontron_review_cc`. Scope: trace the
`super3` chat-template kwargs (`enable_thinking`,
`truncate_history_thinking`) end-to-end across **M0 data prep → M1 SFT
prep → SFT training (data materialization + tokenization) → M1/M2 RL
(RLVR1 / SWE1 / SWE2 / RLHF) → eval baskets** and identify any
inconsistencies that risk degrading model performance via training /
inference distribution mismatch.

This document is **review notes only**. It does not change runtime
behavior. Each finding lists a proposed action; landing the actions
should be split into separate PRs because some changes (e.g. flipping
`enable_thinking`) deserve a design call before they ship.

---

## TL;DR

The single source of truth for super3's chat template is
`src/nemotron/data_prep/templates/super3.jinja` (verbatim copy of
`nano3.jinja`, +2-line header). The template behavior is parameterized
by **two kwargs**: `enable_thinking` (default `True`) and
`truncate_history_thinking` (default `True`).

**Effective kwargs by stage (today's main)**:

| Stage | `enable_thinking` | `truncate_history_thinking` | Source |
|---|---|---|---|
| M0/M1 SFT data prep | **False** (per-row; always False today since no converter sets `reasoning_content`) | True (default) | `create_masked_messages` in `chat_template.py` derives `enable_thinking=has_thinking` |
| SFT roundtrip smoke | same as SFT prep | True (default) | `run_m1_sft_roundtrip_smoke.py` reuses the same `create_masked_messages` helper |
| RLVR1 (`stage1_rlvr/default.yaml`) | True (template default) | **True** (template default) | tokenizer-level + vLLM neither override `chat_template_kwargs` |
| SWE1 (`stage2_swe1/default.yaml`) | **True** (explicit) | **False** (explicit) | vLLM section `chat_template_kwargs: {enable_thinking: true, truncate_history_thinking: false}` |
| SWE2 (`stage2_swe2/default.yaml`) | **True** (explicit) | **False** (explicit) | same as SWE1 |
| RLHF (`stage3_rlhf/default.yaml`) | True (template default) | **True** (template default) | same shape as RLVR1 |
| Eval baskets (`stage3_eval/config/m1_basket.yaml`, `m1_full_basket.yaml`) | unset → depends on deployment | unset → depends on deployment | basket configs only list `tasks: [...]`; no template kwargs |

**Two real inconsistencies surface**:

1. **`enable_thinking` differs between SFT (False) and all RL stages
   (True)** → the model is taught during SFT to emit `<think></think>`
   immediately after `<|im_start|>assistant\n`, but at RL inference is
   prompted with `<|im_start|>assistant\n<think>\n` and expected to
   fill an open thinking block. Training / inference distribution
   mismatch on the most critical generation boundary.

2. **`truncate_history_thinking` differs across RL stages** (True for
   RLVR1+RLHF, False for SWE1+SWE2) → multi-turn rollouts in
   RLVR1/RLHF strip previous-turn thinking; SWE1/SWE2 preserve it.
   Whatever the model learned during SFT about referencing prior
   thinking will be inconsistent with one or the other set.

Plus two related issues found while tracing:

3. **All 4 RL configs ship `stop_strings: null`** → generations can
   over-run `<|im_end|>`. task071 math-eval audit (session 36) confirmed
   this is already biting in practice: 234/300 AIME generations hit
   the 2048-token cap without ever emitting `\boxed{}`.

4. **Eval basket configs don't pin `chat_template_kwargs`** → eval
   rendering depends on whatever the deployment YAML sets and on
   whatever `tokenizer.chat_template` was saved into the checkpoint.
   No defense against silent drift between training-time template and
   eval-time template.

---

## Detailed findings

### Finding 1 — `enable_thinking` SFT/RL mismatch

**Where**: `src/nemotron/data_prep/core/chat_template.py` line 249-282
(`create_masked_messages`).

```python
has_thinking = any(
    "reasoning_content" in msg and msg["reasoning_content"]
    for msg in messages
)
# ...
chunks = split_template_into_messages(
    messages_i, tokenizer,
    start_from_last_user=True,
    enable_thinking=has_thinking,   # <-- here
    tools=tools,
)
```

Then a `grep -rn 'reasoning_content' src/nemotron/recipes/super3/` returns
**zero** hits inside data-prep code. None of the M0 converters
(`prepare_m0_assets.py`) and none of the M1 supervision builders
(`prepare_m1_agentic_sft.py`) ever populate `reasoning_content` on
the assistant messages they emit. So in practice **every SFT row is
rendered with `enable_thinking=False`**.

When `enable_thinking=False`, super3.jinja line 207-213 emits the
generation prompt as:
```
<|im_start|>assistant\n<think></think>
```

And the per-assistant-turn injection at lines 116-120 prepends
`<think></think>` to any assistant content that doesn't already
contain `<think>`/`</think>`. So **every SFT-trained assistant turn
begins with `<think></think>`** (closed empty thinking block).

But every RL stage uses `enable_thinking=True` (either explicit in
SWE1/SWE2, or template default in RLVR1/RLHF), which makes the
generation prompt:
```
<|im_start|>assistant\n<think>\n
```

— an OPEN thinking block. The model has **never seen this prefix
during SFT** and was not taught to fill it before emitting the final
answer.

**Risk**: undermines the very purpose of `enable_thinking=True` in RL.
The model trained with `<think></think>` will either:
- Immediately emit `</think>` (since it learned the closed-thinking pattern)
- Or produce noise inside the thinking block (it's never been
  supervised on that distribution).

Either way the model is not actually doing supervised reasoning at
RL time even though the template is set up for it.

**Proposed action**: Decide which side moves.

- **Option A**: SFT data prep should pass `enable_thinking=True`
  unconditionally so the rendered SFT prompt matches the RL prompt
  exactly. This requires also choosing how to populate `<think>...
  </think>` for the assistant turns — either (1) put the
  `reasoning_content` field on rows that have a CoT solution (e.g.
  `transform_numinamath_competition` already extracts
  `reference_solution`), or (2) carry the CoT inside `content` as
  `<think>{cot}</think>{answer}` so the template's no-op branch
  preserves it.
- **Option B**: All RL configs explicitly set
  `chat_template_kwargs.enable_thinking=False` so RL prompts match
  what SFT trained against. This forfeits the reasoning RL signal
  but at least removes the distribution mismatch.

Option A is the right answer if the goal is actually
chain-of-thought RL; Option B is the cheaper compatibility fix.

### Finding 2 — `truncate_history_thinking` differs across RL stages

**Where**:
- `stage1_rlvr/config/default.yaml` — no vLLM `chat_template_kwargs`
  block → template default `True`.
- `stage2_swe1/config/default.yaml` line 284 — explicit
  `truncate_history_thinking: false`.
- `stage2_swe2/config/default.yaml` line 285 — explicit
  `truncate_history_thinking: false`.
- `stage3_rlhf/config/default.yaml` — no vLLM `chat_template_kwargs`
  block → template default `True`.

`truncate_history_thinking` controls whether prior-turn `<think>...
</think>` blocks are stripped to `<think></think>` when re-rendering
multi-turn history (super3.jinja lines 128 + 166). The behavior is
significant for multi-turn agentic loops where the model's earlier
thinking is supervision context for later turns.

**Risk**: SFT data prep uses `True` (default). SWE1/SWE2 use
`False` so the model sees its OWN prior thinking verbatim across
turns during RL — but the SFT-time tokenization of any multi-turn
data dropped that content. The model is rewarded during RL for
referencing thinking it was never trained to attend to. RLVR1 and
RLHF inherit `True` so they at least match SFT, but the cross-stage
inconsistency (SWE differs from RLVR/RLHF) is unjustified by any
visible design note.

**Proposed action**: Decide on a single value and pin it everywhere.
The principled choice is whatever matches the SFT-time rendering of
the multi-turn supervision data. If SFT data carries multi-turn
trajectories with full prior thinking (e.g. task031 Agentic SFT v1
preserves multi-turn tool calls), use `False` everywhere. If SFT
data only carries the most recent turn's thinking, use `True`
everywhere. **Mismatch across RL stages is the bug**, not the value.

### Finding 3 — eval basket configs don't pin chat-template kwargs

**Where**:
- `src/nemotron/recipes/super3/stage3_eval/config/m1_basket.yaml`
- `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket.yaml`
- `src/nemotron/recipes/super3/stage3_eval/config/default.yaml`

`grep` returns no `chat_template`, `enable_thinking`, or
`reasoning_parser` references in any eval-stage config. The eval
flow goes through nemo-evaluator-launcher with a deployment YAML
(`deployment: generic` per the `default.yaml`). The actual
`chat_template_kwargs` applied during eval inference depends on:

1. The HF tokenizer's saved `chat_template` field in the checkpoint
   (whatever was set when the checkpoint was written).
2. Whatever the launcher's deployment yaml chooses for kwargs.

Neither is constrained by anything in this repo's eval-stage config.

**Risk**: silent drift. If a checkpoint is saved with one chat
template (or the saved kwargs are inconsistent across stages),
eval will use that, not the per-stage SFT/RL kwargs. Even worse,
two model versions A and B can have different effective eval
prompts if they were saved by different stages.

**Proposed action**: Add explicit `chat_template_kwargs` to the
eval basket configs (or to the deployment yaml) and assert at eval
startup that the resolved kwargs match the stage that produced the
checkpoint. The task071 eval-debug sessions already had to debug
"is the eval using the chat template?" — pinning would prevent that
class of question.

### Finding 4 — `stop_strings: null` across all 4 RL configs

**Where**:
- `stage1_rlvr/config/default.yaml` lines 256-257
- `stage2_swe1/config/default.yaml` lines 259-260
- `stage2_swe2/config/default.yaml` lines 259-260
- `stage3_rlhf/config/default.yaml` lines 254-255

```yaml
stop_token_ids: null
stop_strings: null
```

So vLLM has nothing to terminate on except `eos_token_id` (whichever
the tokenizer ships) and the model's own willingness to emit it.

`task071_m1_agentic_qwen_scaleup_train_exec/eval_logic_math_audit_session36.md`
(landed 2026-05-22) confirms this is already biting:
- 234/300 AIME generations hit the 2048-token cap without ever
  emitting `\boxed{}`.
- 28/30 HMMT generations same pattern.

**Risk**: model burns budget after the answer is already complete;
both reward and eval scoring see truncated outputs.

**Proposed action**: Add `stop_strings: ["<|im_end|>"]` (and
optionally `"</tool_call>\n"` for tool-call envs) to all 4 RL
configs. The token-id form is also fine if `<|im_end|>` is a single
token in the tokenizer.

### Finding 5 — auto-injected `<think></think>` is invisible to converters

**Where**: super3.jinja lines 116-120.

```jinja
{%- if content is string -%}
    {%- if '<think>' not in content and '</think>' not in content -%}
        {%- set content = "<think></think>" ~ content -%}
    {%- endif -%}
{%- endif -%}
```

Every assistant message without `<think>` tags has `<think></think>`
auto-injected. This happens silently — not visible from M0/M1
converter code.

**Risk**: low directly, but it interacts with Finding 1. Anyone
adding a CoT to an assistant turn needs to know they must wrap it
in `<think>...</think>` themselves, or pass it via the
`reasoning_content` field, or the template will collapse it to an
empty thinking block.

**Proposed action**: document this behavior in a comment near the
M1 supervision builders (e.g. in `prepare_m1_agentic_sft.py` near
`assistant_for_reasoning`), and consider exposing a converter-side
helper that wraps CoT properly so individual converters don't have
to think about this.

---

## What is consistent and working

- **Single template source**: `super3.jinja` is the only definition;
  `_apply_chat_template` in `chat_sft_shard_core.py` and the
  roundtrip smoke loader both resolve `chat_template: super3` to the
  same file. Anti-drift covered by
  `test_super3_body_is_currently_verbatim_copy_of_nano3`.
- **SFT data prep and roundtrip smoke** use identical
  `create_masked_messages` helpers, so what the roundtrip smoke
  validates is what production materialization produces.
- **Tool-call serialization** (the `<tool_call><function=...>
  <parameter=...>` XML form) is the same across all rendering paths.
- **GSM8K `####` marker stripping** in `assistant_for_reasoning`
  prevents the GSM8K verifier marker from leaking into SFT targets.

---

## Recommended PR sequence

Two of these are safe-to-land defensive PRs; the other two need
design calls before they ship.

1. **PR A (safe, immediate)** — Add `stop_strings: ["<|im_end|>"]`
   to all 4 RL stage configs. Cures task071's math-eval truncation
   directly. Pure config change, no behavior risk besides shorter
   generations.

2. **PR B (safe, immediate)** — Pin
   `chat_template_kwargs: {enable_thinking: ..., truncate_history_thinking: ...}`
   in the eval `default.yaml` so eval rendering is explicit instead
   of inherited. Initial values match RL stage defaults; can be
   refined per-task later.

3. **PR C (design call required)** — Resolve `truncate_history_thinking`
   inconsistency across RL stages. Pick a single value (False if
   multi-turn supervision preserves prior thinking; True otherwise)
   and apply it to all 4 RL stage configs. Requires confirming
   which value matches SFT-time rendering.

4. **PR D (design call required, biggest impact)** — Resolve
   `enable_thinking` SFT/RL mismatch (Finding 1). Either flip RL to
   `False` (cheap fix, drops CoT-RL signal), or carry
   `reasoning_content` through M0/M1 supervision builders so SFT
   data renders with `enable_thinking=True` and real thinking
   content (correct fix, more work).

---

## Reproducing the findings

```bash
# Template body parity (super3 vs nano3):
diff src/nemotron/data_prep/templates/{nano3,super3}.jinja

# SFT data-prep effective `enable_thinking` is always False:
grep -rn 'reasoning_content' src/nemotron/recipes/super3/

# `truncate_history_thinking` differs across RL stages:
grep -nB2 -A8 'chat_template_kwargs' \
  src/nemotron/recipes/super3/stage2_rl/*/config/default.yaml

# Eval configs don't set kwargs:
grep -rn 'chat_template\|enable_thinking\|reasoning_parser' \
  src/nemotron/recipes/super3/stage3_eval/

# RL stop_strings are null:
grep -n 'stop_strings\|stop_token_ids' \
  src/nemotron/recipes/super3/stage2_rl/*/config/default.yaml
```

## Existing tests for the template

- `tests/data_prep/test_chat_template_super3.py`
  - `test_apply_chat_template_resolves_super3_name`
  - `test_super3_template_renders_four_role_conversation`
  - `test_super3_template_keeps_escaped_tool_markup_as_quoted_text`
  - `test_super3_body_is_currently_verbatim_copy_of_nano3`
- `tests/recipes/super3/test_m1_agentic_sft.py` — covers SFT
  supervision builders; does not exercise template kwargs.

None of the existing tests assert cross-stage `chat_template_kwargs`
consistency. Adding such a test would lock the future fixes in place
(see PR C / PR D).
