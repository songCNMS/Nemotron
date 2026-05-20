# task068 Session 1 design doc — RLHF tool-call pairing harness

**Status**: design — no code yet. This doc decides the strategy
parameters Session 2 implements.

**Plan reference**: plan §5.6 RLHF acceptance note —

> tool-call-validity check still passes per plan §5.6 note

`stage3_rlhf/config/default.yaml` loads two NeMo-Gym envs in parallel:

- `genrm_compare` — preference judge (M0 data landed via task018 Session 2)
- `single_step_tool_use_with_argument_comparison` — parallel tool-call
  validity check (THIS task lands its M0 data)

The harness produces M0 rows for the second env so the RLHF policy is
checked at every preference-optimization step for whether it can still
emit well-formed tool calls. Without it the policy can learn to please
the GenRM judge via eloquent prose while regressing on tool-call
competence — a known reward-hacking failure mode for non-verifiable
preference RL.

---

## Problem statement

Source corpora:

- **HelpSteer-2 prompts** (task018 Session 2 ✓): ~7K human-written
  prompts. Each row carries `prompt` plus paired responses + rating
  attributes. The PROMPT is the tool-call surface; the responses are
  GenRM judge input only.
- **Hermes function-calling** (task005 ✓): ~30K M0 rows with `prompt`
  + tool schema + gold tool call. Each row already has a verified
  argument_match shape.

A naïve cross-product (HelpSteer-2 × Hermes) is ~210M candidate pairs.
Even with K=20 sampling cap per HelpSteer-2 prompt that's 140K rows —
larger than the M0 Hermes corpus itself. The right shape needs:

1. A **relevance filter** that keeps only HelpSteer-2 prompts whose
   semantic shape admits a tool-call follow-up.
2. A **per-prompt gold call sourcing** strategy that's cheap, deterministic,
   and produces high-signal pairs.
3. A **sampling cap** that keeps the corpus tractable while preserving
   coverage.
4. A **decontamination filter** vs M1/M2 eval baskets.

---

## Decisions

### 1. Relevance filter — keyword + Hermes-template match

**Picked**: combine a cheap keyword heuristic with template matching
against the Hermes prompt distribution.

**Algorithm**:

```python
def is_toolcall_eligible(prompt: str) -> bool:
    # (1) Keyword heuristic — any prompt mentioning one of these
    # primitives implies an actionable, tool-able task. Case-insensitive.
    KEYWORDS = (
        "look up", "find out", "search for", "compute", "calculate",
        "convert", "translate", "schedule", "lookup", "fetch",
        "what is the", "how many", "which",
    )
    text = prompt.lower()
    if any(kw in text for kw in KEYWORDS):
        return True
    # (2) Template match — if the prompt structurally matches a Hermes
    # prompt pattern (e.g., "Get the weather for X", "Find me a Y in
    # Z"), it's tool-call eligible by construction.
    return _matches_any_hermes_template(prompt)
```

**Why this**:

- Keyword heuristic is cheap (single string scan per prompt), deterministic,
  and good enough for Session 1.
- Template match catches paraphrases of Hermes patterns that the keyword
  list misses.
- Skips embedding-based filter for Session 1 (would need an embedding
  model + cluster ops); revisit if recall is too low after Session 2
  smoke.

**Expected yield**: ~30% of HelpSteer-2 prompts pass (rough estimate;
real number measured during Session 2). So ~2K eligible prompts out of
~7K HelpSteer-2 rows.

### 2. Per-prompt gold call sourcing — function-name match heuristic

**Picked**: for each eligible HelpSteer-2 prompt, find the Hermes row
whose gold call's `function.name` appears (as a substring or
templated keyword) in the HelpSteer-2 prompt. If multiple Hermes rows
match, pick the one with the most overlapping schema words. If none
match, drop the HelpSteer-2 prompt from the corpus (it's "eligible"
but has no good Hermes pair).

**Algorithm**:

```python
def find_gold_call(prompt: str, hermes_rows: Sequence) -> dict | None:
    text = prompt.lower()
    candidates = []
    for hrow in hermes_rows:
        gold = hrow["expected_answer"]["tool_calls"][0]
        name = gold["function"]["name"].lower()
        # Match if function name OR any required argument name appears
        # in the prompt. e.g., `get_weather` matches "weather", "get
        # the weather".
        if name.replace("_", " ") in text or name in text:
            candidates.append(hrow)
    if not candidates:
        return None
    # Tie-break: prefer the candidate whose required-arg names also
    # appear in the prompt (more grounded to the user intent).
    def score(hrow):
        gold = hrow["expected_answer"]["tool_calls"][0]
        arg_names = gold["function"]["arguments"].keys()
        return sum(1 for a in arg_names if a.replace("_", " ") in text)
    candidates.sort(key=score, reverse=True)
    return candidates[0]
```

**Why this**:

- Cheaper than LLM zero-shot (no inference call per prompt).
- Higher signal than random sampling (the function name actually
  matches the prompt's intent).
- Deterministic — no randomness in row selection.
- Drops prompts with no Hermes match, keeping the corpus high-signal.

**Rejected alternatives**:

- Random Hermes call (high noise; teaches policy that any tool call is
  fine regardless of intent)
- LLM-generated gold (requires inference at corpus build time; needs
  cluster + judge model; quality depends on judge model that's also
  being trained against this data — feedback loop risk)

**Expected yield**: ~50-70% of eligible prompts find a Hermes match.
So ~1.0-1.4K paired rows out of ~2K eligible prompts (from ~7K
HelpSteer-2 input rows).

### 3. Sampling cap — K=1 per HelpSteer-2 prompt

**Picked**: one paired row per HelpSteer-2 prompt. The function-name
match strategy picks the BEST single Hermes pair, not a list.

**Why this**:

- Smallest possible corpus that still covers the breadth of the
  HelpSteer-2 prompt distribution.
- The verifier (argument_match) is per-call; redundant pairs for the
  same prompt don't add signal, they just inflate the corpus.
- High diversity per row → curriculum / RL sampling doesn't waste
  gradient on duplicates.
- Easy to verify: total row count = # HelpSteer-2 prompts that pass
  both filters.

**Rejected alternatives**:

- K=5 (would balance prompt diversity vs Hermes diversity, but the
  diversity gain plateaus quickly given the function-name match
  bottleneck)
- K=20 (corpus dominated by "hub" prompts that match many Hermes
  templates — bad for diversity)

### 4. Decontamination — exclude prompts matching eval-basket templates

**Picked**: for each paired row, run a contamination check against the
M1 eval-basket prompt corpora. Exclude any HelpSteer-2 prompt whose
normalized form (lower + strip punctuation) overlaps with:

- **BFCL** (task020 Session 1 row)
- **TauBench airline** (task019 Session 1 row)
- **MCP-Mark** (task020 Session 1 row)
- (HelpSteer1 already decontaminated via task018 Session 2's
  m0_helpsteer2_pref contamination_against entry)

**Algorithm**:

```python
def is_contaminated(prompt: str, eval_prompt_set: frozenset[str]) -> bool:
    normalized = _normalize_for_contam_check(prompt)
    if normalized in eval_prompt_set:
        return True
    # Also check n-gram overlap: if a 5-gram from the prompt appears
    # verbatim in any eval prompt, treat as contaminated.
    five_grams = _five_grams(normalized)
    return any(g in _ALL_EVAL_FIVEGRAMS for g in five_grams)
```

The eval prompt corpora ship in the task019/020 registries; loading
them at conversion time is what the contamination_audit module already
does (task030 Session 7 ✓), so reuse that loader.

**Row-level marker**: every output row carries:

```yaml
metadata:
  contamination_against:
    - BFCL
    - TauBench airline
    - MCP-Mark
    - HelpSteer1
```

This way task030's contamination_audit can audit the output rows the
same way it audits M0 data rows.

---

## Reference output row shape

Each paired row the Session 2 converter emits:

```json
{
  "environment": "single_step_tool_use_with_argument_comparison",
  "milestone": "M0",
  "use_stage": ["M0 data_env_foundation", "M1 RLHF tool-call validity"],
  "question": "Look up the current weather in Tokyo.",
  "expected_answer": {
    "name": "get_weather",
    "arguments": {"location": "Tokyo"}
  },
  "responses_create_params": {
    "input": [
      {"role": "system", "content": "<tool-call system prompt>"},
      {"role": "user", "content": "Look up the current weather in Tokyo."}
    ],
    "tools": [<Hermes tool schema for get_weather>]
  },
  "reward_config": {
    "verifier": "argument_match",
    "max_score": 1.0,
    "match": ["name", "arguments"]
  },
  "extra_env_info": {
    "source_helpsteer2_id": "<id>",
    "source_hermes_id": "<id>",
    "match_strategy": "function_name_overlap"
  },
  "metadata": {
    "source_dataset": "rlhf_toolcall_pairing",
    "source_helpsteer2_id": "<id>",
    "source_hermes_id": "<id>",
    "contamination_against": ["BFCL", "TauBench airline", "MCP-Mark", "HelpSteer1"]
  }
}
```

---

## Worked examples

### Example 1 — clear match

HelpSteer-2 prompt: "Look up the current weather in Tokyo."

- Relevance filter: keyword "look up" → ✓
- Function-name match: Hermes row with `get_weather` (name appears in
  prompt as "weather"; required arg `location` matches "Tokyo" with
  a city heuristic)
- Output: paired row above

### Example 2 — eligible but no Hermes match

HelpSteer-2 prompt: "Compose a haiku about cherry blossoms."

- Relevance filter: no keyword match; no Hermes template match → ✗
- Output: dropped before reaching gold-call sourcing

### Example 3 — eligible, found match, but contaminated

HelpSteer-2 prompt: "Translate 'Hello' to French."

- Relevance filter: keyword "translate" → ✓
- Function-name match: Hermes row with `translate` → ✓
- Decontamination: matches a TauBench airline prompt fragment ("translate
  passenger announcement") → ✗
- Output: dropped during contamination step

### Example 4 — kept after all filters

HelpSteer-2 prompt: "Find me a restaurant near Times Square."

- Relevance filter: keyword "find me" + "near" → ✓
- Function-name match: Hermes row with `search_restaurant` (name's "search" 
  appears via "find me a"; required arg `location` matches "Times Square") → ✓
- Decontamination: no overlap with eval baskets → ✓
- Output: paired row kept

---

## Corpus size estimate

Starting corpus: HelpSteer-2 train (~7K rows; M0 smoke filter at
task018 Session 2 cuts to ~500 rows for the smoke train split). For the
full HelpSteer-2 train we estimate:

| Stage | Rows | Cumulative drop |
|---|---:|---:|
| HelpSteer-2 train (raw) | 7,000 | — |
| After relevance filter (~30% pass) | ~2,100 | 70% drop |
| After function-name match (~60% of eligible) | ~1,260 | 82% drop |
| After decontamination (~5% drop of remaining) | ~1,200 | 83% drop |

So the **final tool-call validity corpus is ~1,200 paired rows from a
full HelpSteer-2 train pass**. M0 smoke variant (500-row input) yields
~85 paired rows — enough to wire the env and verify the verifier path,
not enough to converge a policy.

This is small enough to be tractable, large enough to provide
meaningful per-step validity signal during RLHF. Operators wanting
more breadth can lower the function-name match threshold (currently
"name appears in prompt" — could relax to "any required arg name
appears in prompt") in Session 2's converter.

---

## Converter interface contract (Session 2 will implement)

```python
def transform_rlhf_toolcall_pairing(
    helpsteer2_rows: Iterable[Mapping[str, Any]],
    *,
    hermes_corpus: Sequence[Mapping[str, Any]],
    eval_prompt_set: frozenset[str],
    relevance_filter: Callable[[str], bool] = default_relevance_filter,
    gold_call_finder: Callable[[str, Sequence], Mapping | None] = default_gold_call_finder,
) -> Iterator[JsonDict]:
    """Stream-yield paired rows (Helpsteer-2 prompt + Hermes gold call).

    Unlike the per-row converters in prepare_m0_assets.py, this one is
    a STREAM operation — needs the full Hermes corpus in memory to do
    function-name match. Caller threads it into the M0 prep pipeline
    via a new dispatch path.
    """
```

Session 2 wires this into `prepare_m0_assets.py`'s converter registry
and adds a new env in `environment_registry.yaml`:
`single_step_tool_use_with_argument_comparison_rlhf`.

Session 3 flips the row in `rlhf_env_registry.yaml` to active.

Session 4 (cluster) verifies end-to-end RLHF with both `genrm_compare`
and tool-call validity envs lit up.

---

## Open questions (for product/lead input)

1. **K=1 vs K=3** — does product care about prompt diversity over
   Hermes call coverage? K=1 is the design's pick; K=3 would let
   the same prompt pair with three different Hermes calls if they
   all match the function-name heuristic. Not picked because the
   gradient signal from "same prompt, different tools" is weak.
2. **LLM-generated gold call as Session 5** — once a judge model is
   live (task018 Session 3), we can use it to generate higher-quality
   gold calls instead of the function-name heuristic. Worth scoping
   as a follow-up.
3. **Multilingual** — HelpSteer-2 is English-only; if we want
   multilingual tool-call validity, that's task027 (M2) territory.
   Tracked for completeness; not in task068 scope.

---

## Acceptance for Session 1 (THIS design doc)

- [x] Design doc captures filter / gold-call / sampling / decontamination
- [x] Reference paired-row shape with 4 worked examples
- [x] Corpus size estimate from 7K → ~1,200 paired rows
- [x] Contamination plan vs M1 eval basket (task019 + task020)
- [x] Converter interface contract for Session 2
- [x] Open questions section for product/lead alignment
