# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task057_m0_tier2_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task057_m0_tier2_expansion |
| PR | pending push |
| Session | 93 |

正在做：task057 Session 2 — `long_context_qa_smoke` env via
`THUDM/LongAlpaca-12k`. Second of 6 tier-2 M0 envs; follows Session 1's
multilingual_instruct pattern.

## What's in this PR

### 新 M0 env `long_context_qa_smoke`

- `environment_registry.yaml` 加 env: family `long_context` / verifier
  `long_context_qa_stub` / max_turns 1 / sandbox none
- Required field `extra_env_info.doc_length_chars` for telemetry
- `prepare_m0_assets.SYSTEM_PROMPTS` 加 prompt ("long-context
  reading-comprehension assistant; quote or paraphrase passage")

### 新 converter `transform_longalpaca_qa`

LongAlpaca-12k is Alpaca-format with optional `input` field carrying
the long document. Converter:

- Requires `instruction` + `output` + `input` (long doc) — this env
  is long-context QA; question-only rows go elsewhere
- **`LONGALPACA_MAX_DOC_CHARS = 32_000`** smoke cap (~8K tokens).
  Rows above cap → ValueError (truncation would change answer-span
  semantics). Real 256K-1M long-context is M2 task028 / task037.
- Builds user message embedding `Document:\n{doc}\n\nQuestion: {q}`
- `extra_env_info.doc_length_chars` + `doc_token_estimate` telemetry

### 新 verifier `long_context_qa_stub`

- Wired into `score_record` in `run_m0_health_baseline.py`
- M0 oracle stub: delegates to `score_text` (same contains-match as
  `normalized_exact_or_contains`)
- "stub" suffix signals that span-aware / judge-graded verifier is
  M2 task028 / task037 territory; M0 baseline just needs oracle
  passthrough
- Diagnostics: `normalized_answer` + `contains_match`

### data_registry row 故意延后

`m0_longalpaca_qa` data_registry row deferred to Session 2.5 (same
pattern as Session 1's multilingual row deferral) — needs HF access
to pin a real LongAlpaca commit SHA via `HfApi().dataset_info`. Locked-
in test asserts the row is NOT in registry yet.

### Tests (`test_longalpaca_qa.py`, 17 cases)

- Module surface 3: SYSTEM_PROMPTS / CONVERTERS / MAX_DOC_CHARS = 32K
- Happy path 3: emits record / embeds doc in user msg / doc_length
  telemetry
- M0 smoke cap 2: rejects > cap / accepts exactly at cap (strict >)
- Error surfaces 4: missing instruction / missing output / missing doc /
  empty doc
- score_record dispatch 2: long_context_qa_stub wired / no-match diagnostics
- Registry integration 3: validate_registries clean / env_registry row
  shape / data_registry row NOT yet present (deferral lock)

Sandbox 测试基线 675 → **692 passed + 7 skipped** (17 new).

## task057 状态

- Session 1 ✓ (PR #108) — multilingual_instruct env (Aya)
- Session 1.5 ☐ — pin Aya SHA + add data_registry row
- Session 2 ✓ (this PR) — long_context_qa_smoke env (LongAlpaca-12k)
- Session 2.5 ☐ — pin LongAlpaca SHA + add data_registry row
- Sessions 3-6 ☐ — 4 envs left: sql_text_to_query / terminal-tier2 /
  safety_reasoning_smoke / math_with_tools

Roadmap §5b 更新 — task057 S2 ✓; S3 (sql_text_to_query) added as next
sandbox candidate.
