# task068 - task_knowledge

## Why this is non-trivial

The RLHF stage runs TWO NeMo-Gym envs in parallel:

- `genrm_compare` — preference judge (rewards good answers)
- `single_step_tool_use_with_argument_comparison` — tool-call validity
  check (rewards well-formed tool calls)

If only the GenRM env emits reward, the policy learns to give eloquent
prose that the judge prefers but stops emitting correct tool calls.
Plan §5.6 explicitly calls this out: "tool-call-validity check still
passes per plan §5.6 note".

The data side for the second env doesn't exist today — that's this
task's deliverable.

## Why naïve cross-product fails

- ~7k HelpSteer-2 train rows × ~30k Hermes M0 rows = ~200M candidate
  pairs
- Even with sampling cap K=20, that's 140k rows — bigger than the M0
  Hermes corpus itself
- Many HelpSteer-2 prompts have no tool-call interpretation (poetry,
  opinion, chitchat); pairing them produces noise that confuses the
  tool-call verifier

## Relevance filter candidates

| Approach | Pro | Con |
|---|---|---|
| Keyword heuristic | Cheap, deterministic | High false positive on common words |
| Embedding similarity | Captures semantic intent | Needs embedding model + cluster ops |
| LLM zero-shot classifier | Highest quality | Expensive at corpus scale |
| Hermes prompt template match | Free + precise | Low recall |

Session 1 decision: probably **keyword heuristic + Hermes prompt
template match** combined — cheap, deterministic, good enough for
first iteration. Embedding-based filter can come later if recall is too
low.

## Per-prompt gold call sourcing

For each pairable HelpSteer-2 prompt, need ONE gold tool call:

1. **Cheapest**: random Hermes call whose schema mentions a keyword
   from the prompt → noisy but free
2. **Better**: LLM (Qwen3-4B / Nemotron-base) given prompt + Hermes
   schema, produce gold call → moderate cost, much better signal
3. **Best**: human label small validation set, train classifier →
   highest cost, M2 territory

Session 1 design picks one. Likely (1) for v0 with (2) as Session 5+
follow-on.

## Decontamination plan

`m0_helpsteer2_pref` already has `contamination_against: [MT-Bench,
HelpSteer1]`. For task068's paired output, ALSO exclude:

- BFCL prompts (task020 eval basket)
- TauBench airline prompts (task019 eval basket)
- MCP-Mark prompts (task020 eval basket)

The contamination_audit (task030 Session 7) catches these at write
time if the converter adds them to its output's `contamination_against`
list.

## Plan-side reference

Plan §5.6 RLHF acceptance:
> ...verify tool-call validity still passes per plan §5.6 note

`stage3_rlhf/config/default.yaml` lines 124-145 declare the two envs;
this task's job is producing M0 data for the second one.

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` pyarrow ImportError —
pre-existing, run sandbox tests with `--ignore` flag.
