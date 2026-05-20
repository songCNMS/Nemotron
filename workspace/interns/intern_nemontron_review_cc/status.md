# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task057_m0_tier2_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task057_m0_tier2_expansion |
| PR | pending push |
| Session | 95 |

正在做：task057 Session 3 — `sql_text_to_query` env via BIRD-SQL.
Third of 6 tier-2 M0 envs.

## What's in this PR

### 新 M0 env `sql_text_to_query`

- `environment_registry.yaml` 加 env: family `structured_query` /
  verifier `sql_execution_match` / max_turns 1 / sandbox none
- Required field `extra_env_info.db_id` for cross-schema stratification
- `SYSTEM_PROMPTS` prompt: "text-to-SQL assistant; return ONLY the SQL"

### 新 converter `transform_bird_sql`

BIRD rows carry gold SQL under varying keys per snapshot — converter
accepts `SQL` / `sql` / `query` / `gold_sql`. Output:

- User message embeds `Database: {db_id}\n\nQuestion: {q}\n\nEvidence: {e}`
- Evidence section conditional (BIRD optional column)
- `extra_env_info.db_id` + `question_id` + `difficulty` +
  `has_evidence` preserved for downstream stratification
- BIRD schema itself NOT embedded — schemas are large; model is
  expected to know schemas at training time (oracle passthrough) and
  to query DB introspection at runtime

### 新 verifier `sql_execution_match`

- `normalize_sql()`: lowercase + collapse whitespace + strip backticks
  + strip trailing semicolon
- `score_sql_execution_match()`: exact-or-contains on normalized SQL
- Wired into `score_record` dispatch
- "execution_match" name signals INTENT for the future verifier (real
  DB sandbox execution = M2 task024 territory); today's M0 oracle
  baseline is normalized string match

### data_registry row 故意延后

`m0_bird_sql` data_registry row deferred to Session 3.5 (same pattern
as Sessions 1.5 / 2.5). Two pin-blockers:

1. Real BIRD commit SHA via HF API
2. **CC-BY-SA-4.0 share-alike license** — task058 license cascade
   audit will flag this at row-add time; the row needs explicit
   contamination_against [BIRD mini_dev, Spider] + use_stage note
   confirming eval-time-only use does not cascade

### Tests (`test_bird_sql.py`, 29 cases)

- Module surface 2: SYSTEM_PROMPTS / CONVERTERS
- Happy path 4: emits record / Database+Question in user / Evidence
  conditional / has_evidence flag
- Alternate gold-SQL keys 4: SQL / sql / query / gold_sql (parametric)
- Cross-schema metadata 3: db_id preserved / question_id +
  difficulty preserved / difficulty=None handled
- normalize_sql 4: lowercase+whitespace / trailing semicolon / strip
  backticks / None+empty handling
- score_sql_execution_match 4: exact / contains / no match / empty
  expected
- score_record dispatch 2: sql_execution_match wired / no-match diagnostics
- Error surfaces 3: missing question / missing gold SQL / missing db_id
- Registry integration 3: validate_registries clean / env_registry row /
  data_registry row deferral lock

Sandbox 测试基线 692 → **721 passed + 7 skipped** (29 new).

## task057 状态

- Session 1 ✓ (PR #108) — multilingual_instruct (Aya)
- Session 2 ✓ (PR #118) — long_context_qa_smoke (LongAlpaca-12k)
- Session 3 ✓ (this PR) — sql_text_to_query (BIRD-SQL)
- Sessions 1.5/2.5/3.5 ☐ — pin HF SHAs + add data_registry rows
- Sessions 4-6 ☐ — terminal-tier2 / safety_reasoning_smoke /
  math_with_tools

Roadmap §5b 更新.
