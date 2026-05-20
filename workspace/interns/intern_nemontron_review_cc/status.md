# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task068_rlhf_toolcall_pairing_harness -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task068_rlhf_toolcall_pairing_harness |
| PR | pending push |
| Session | 87 |

正在做：task068 Session 2 — implement `transform_rlhf_toolcall_pairing`
converter per Session 1 design doc (PR #110).

## What's in this PR

### 新 module `m0_data_env/rlhf_toolcall_pairing.py`

Pure-Python stream converter implementing Session 1's 4-filter design:

- `RELEVANCE_KEYWORDS` — 16 keywords ("look up", "find me", "compute",
  "translate", "weather", "near", etc.)
- `default_relevance_filter(prompt)` — case-insensitive keyword match
- `default_gold_call_finder(prompt, hermes_corpus)`:
  - Function-name match heuristic (name + underscored variants +
    trailing fragment)
  - Required-arg tiebreak: prefer the Hermes row whose arg names
    also appear in the prompt
  - Deterministic — sorted stable
- `_extract_function_call(hermes_row)` handles two Hermes formats:
  newer (`expected_answer.tool_calls[0].function`) + older direct
  `{name, arguments}`
- `is_contaminated(prompt, eval_prompt_set)`:
  - Tier 1: exact normalized prompt match (lowercase + punctuation-stripped)
  - Tier 2: any 5-gram overlap (catches paraphrases sharing verbatim
    phrasing)
- `build_eval_prompt_set(eval_prompts)` helper for callers to assemble
  the eval-prompt 5-gram set
- `transform_rlhf_toolcall_pairing(helpsteer2_rows, *, hermes_corpus,
  eval_prompt_set, relevance_filter, gold_call_finder)`:
  - Stream-yields paired rows in NeMo-Gym
    `single_step_tool_use_with_argument_comparison` shape
  - Filter order: relevance → gold-call match → contamination (3 drop
    points)
  - Output: argument_match verifier; tool schema attached from Hermes
    row or synthesized minimally if missing
  - Both filter functions injectable for operator customization
- `PAIRED_CONTAMINATION_AGAINST` = (BFCL, TauBench airline, MCP-Mark,
  HelpSteer1) — every output row carries these so task030 Session 7's
  contamination_audit module can audit downstream consumers

### Tests (`test_rlhf_toolcall_pairing.py`, 31 cases)

- Constants 2: PAIRED_CONTAMINATION_AGAINST tuple / RELEVANCE_KEYWORDS
  covers design-doc primitives
- Relevance filter 3: keyword match / no match / case-insensitive
- _extract_function_call 3: newer `tool_calls` format / older direct /
  None for missing
- Gold-call finder 5: function-name match / required-arg tiebreak /
  underscore handling / no-match → None / skips malformed rows
- Contamination 5: exact normalized / 5-gram overlap / clean passes /
  empty eval-set / empty prompt
- build_eval_prompt_set 1: normalized + 5-grams included
- Orchestrator 11: clean match yields row / drops by relevance / drops
  by no match / drops by contamination / yields-after-all-filters /
  skips empty prompts / source IDs propagated / tool schema attached /
  synthesizes minimal schema when missing / custom relevance filter
  injection / custom gold-call finder injection / match_strategy
  metadata lock

Sandbox 测试基线 620 → **651 passed + 7 skipped** (31 new)。

## 跟 Session 1 design doc 对齐

Session 2 实现严格按 Session 1 design 写：

- ✓ Relevance filter: keyword heuristic (Hermes template match left as
  Session 3+ hook; design doc said "leave as a hook")
- ✓ Gold-call sourcing: function-name match + required-arg tiebreak
- ✓ K=1 (one row per HelpSteer-2 prompt via stream)
- ✓ Decontamination: exact + 5-gram check; eval-prompt set built via
  `build_eval_prompt_set`
- ✓ Output row shape matches design doc reference JSON

## task068 状态

- Session 1 ✓ (PR #110) — design doc
- Session 2 ✓ (this PR) — converter implementation
- Session 3 ☐ — flip RLHF env registry's tool-call row to active; wire
  CLI dispatch path that calls this converter
- Session 4 ☐ — cluster smoke (needs task018 Session 3 judge service)

Roadmap §5b 更新.
