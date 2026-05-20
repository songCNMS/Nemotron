# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task057_m0_tier2_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task057_m0_tier2_expansion |
| PR | pending push |
| Session | 97 |

正在做：task057 Session 4 — `terminal_basic_shell` tier-2 extension
via `epinnock/intercode-nl2bash-curated`. Different from Sessions 1-3
in that it ADDS to an existing env rather than creating a new one.

## What's in this PR

### 新 converter `transform_intercode_nl2bash`

Tier-2 source for the EXISTING `terminal_basic_shell` env (no new
env / verifier needed). Differences from tier-1 `transform_bash_command`:

- Accepts intercode-native field aliases: `nl` / `instruction` /
  `prompt` for instruction; `cmd` / `bash` / `command` / `response`
  for gold command
- `INTERCODE_NL2BASH_MAX_CMD_CHARS = 200` smoke cap: rows above cap
  rejected (per README guidance — drop nightmare rows rather than
  truncate; truncation changes shell semantics)
- Tags `extra_env_info.source_dataset_kind = intercode_nl2bash_tier2`
  for downstream tier-1 vs tier-2 stratification
- Records `extra_env_info.cmd_length_chars` for length-distribution
  telemetry

### `normalize_command_text` enhancement

Added double-quote → single-quote canonicalization. Shell-equivalent
quotes (`"*.txt"` vs `'*.txt'`) now compare equal under the
`command_substring_match` verifier so tier-2 stylistic differences
don't false-negative the oracle baseline.

Back-compat verified: existing fenced-code-block extraction +
whitespace collapsing unchanged; tier-1 tests pass.

### data_registry row 故意延后

`m0_terminal_intercode` data_registry row deferred to Session 4.5
pending real intercode-nl2bash commit SHA pin. Locked-in test asserts
the row is NOT in registry yet.

### Tests (`test_intercode_nl2bash.py`, 26 cases)

- Module surface 3: MAX_CMD_CHARS=200 / CONVERTERS / existing bash_command preserved
- Happy path 3: emits record / source_dataset_kind tagged /
  cmd_length_chars telemetry
- Alternate column conventions 7 (parametric × 3 + 4): nl-key
  parametrized over [nl,instruction,prompt]; cmd-key parametrized over
  [cmd,bash,command,response]
- M0 smoke cap 2: rejects > cap / accepts exactly at cap (strict >)
- Error surfaces 2: missing instruction / missing command
- normalize_command_text 5: double → single quote canonicalization /
  whitespace still collapsed (back-compat) / fenced code block still
  extracted (back-compat) / score_command passes mixed-quote / score_record
  dispatch
- Registry integration 3: validate_registries clean / system_prompts
  unchanged / data_registry row deferral lock
- Back-compat 1: existing tier-1 `m0_terminal_bash_commands` row preserved

Sandbox 测试基线 721 → **747 passed + 7 skipped** (26 new).

## task057 状态

- Session 1 ✓ (PR #108) — multilingual_instruct
- Session 2 ✓ (PR #118) — long_context_qa_smoke
- Session 3 ✓ (PR #120) — sql_text_to_query
- Session 4 ✓ (this PR) — terminal-tier2 (intercode-nl2bash)
- Sessions 1.5/2.5/3.5/4.5 ☐ — pin HF SHAs + add data_registry rows
- Sessions 5-6 ☐ — safety_reasoning_smoke / math_with_tools

Roadmap §5b 更新.
