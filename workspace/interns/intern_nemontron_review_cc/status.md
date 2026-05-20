# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task057_m0_tier2_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task057_m0_tier2_expansion |
| PR | pending push |
| Session | 83 |

正在做：task057 Session 1 — M0 tier2 expansion 第一个 env
(`multilingual_instruct` via `CohereLabs/aya_dataset`). 整 task 拆 6
sessions (一 session 一 env)；这是 Session 1。

## What's in this PR

### 整 task scaffold 拆 sessions

`workspace/tasks/task057_m0_tier2_expansion/README.md` 加 sessions
table — 6 envs (multilingual / long_context / sql / terminal / safety /
math_with_tools) 各自 session。Session 1 落 `multilingual_instruct`
作为 baseline pattern (源最干净，无 contamination overlap)；后续 5 个
按这个 pattern adapt。

### 新 M0 env `multilingual_instruct`

- `environment_registry.yaml` 加 env: family `multilingual` / verifier
  `multilingual_exact_or_contains` / max_turns 1 / sandbox none /
  required field `extra_env_info.language`
- `prepare_m0_assets.SYSTEM_PROMPTS` 加 prompt

### 新 converter `transform_aya_multilingual`

- 支持 `inputs/targets` (Aya 默认) + `instruction/response` (snapshot 别名)
- Language-scope filter：`AYA_TARGET_LANGUAGES` (full names: German /
  Spanish / French / Italian / Japanese / Chinese 含 zh-Hans/Hant) +
  `AYA_TARGET_LANGUAGE_CODES` (ISO: de/es/fr/it/ja/zh +ariants)
- 接受 `language` (full name) 或 `language_code` (ISO) 任一字段
- Out-of-scope 语言 → ValueError (M0 smoke 6 lang only；65-lang full
  set 留 M2 task027)
- Output: `extra_env_info.language` + `extra_env_info.language_code`

### 新 verifier `multilingual_exact_or_contains`

- `normalize_multilingual_text` — Unicode NFC + `str.casefold()` (handles
  German ß / Turkish İ / decomposed-vs-composed)
- **DOES NOT strip punctuation** (CJK meaning depends on it)
- **DOES NOT strip articles** (English-only assumption broken for
  German "die" / "der")
- `score_multilingual_text` — exact-or-contains over normalized text
- `score_record` dispatch wired with `exact_match` + `contains_match` +
  `normalized_answer` diagnostics

### data_registry row 故意延后

`m0_multilingual_aya` data_registry row deferred to Session 1.5 — adding
the row requires pinning a real Aya commit SHA via HF API (`HfApi().dataset_info`)
which needs network + HF access this PR doesn't have. Audit pre-commit
hook would reject any unpinned/TBD revision (task065 ✓ closed that gap).

Schema documented in YAML comment so the future PR adding the row
just copies it. A locked-in test verifies the row is NOT in the
registry yet — catches accidental re-add without real pin.

### Tests (`test_aya_multilingual.py`, 28 cases)

- Module surface 3: SYSTEM_PROMPTS / CONVERTERS / target language sets
- Happy path 9: 6 languages × parametric + alternate aliases + only
  `language_code`
- Language scope 2: out-of-scope rejected / no signal rejected
- Error surfaces 2: missing inputs / missing targets
- normalize_multilingual_text 4: German ß casefold / NFC compose /
  CJK punctuation preserved / English articles NOT stripped
- score_multilingual_text 4: exact / contains / no match / empty expected
- score_record dispatch 2: dispatches multilingual verifier / no-match
  emits correct diagnostics
- Registry integration 2: validate_registries clean / env_registry row
  shape
- Row deferral lock 1: data_registry does NOT yet contain m0_multilingual_aya

Sandbox 测试基线 592 → **620 passed + 7 skipped** (28 new)。三个
data-registry audit 全 clean。

## task057 状态

- Session 1 ✓ (this PR) — multilingual_instruct env + converter + verifier
- Session 1.5 ☐ — pin Aya SHA + add data_registry row (needs HF access)
- Sessions 2-6 ☐ — 其余 5 envs (long_context_qa_smoke / sql_text_to_query /
  terminal_basic_shell tier-2 / safety_reasoning_smoke / math_with_tools)
