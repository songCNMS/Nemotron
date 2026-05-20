# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task057_m0_tier2_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task057_m0_tier2_expansion |
| PR | pending push |
| Session | 99 |

正在做：task057 Session 5 — `safety_reasoning_smoke` env via
`nvidia/Nemotron-Content-Safety-Reasoning-Dataset`. Fifth of 6 tier-2
M0 envs.

## What's in this PR

### 新 M0 env `safety_reasoning_smoke`

- `environment_registry.yaml` 加 env: family `safety` / verifier
  `safety_judge_stub` / max_turns 1 / sandbox none
- Required field `extra_env_info.verdict` for telemetry
- `SYSTEM_PROMPTS`: "content-safety analyst; verdict ALLOW/BLOCK/ESCALATE"

### 新 converter `transform_nemotron_safety_reasoning`

Permissive field-alias support per README's warning that the dataset
viewer has schema errors:

- **prompt** column: prompt / input / question / messages
  (chat-style list — picks last user message)
- **verdict** column: verdict / label / safety / classification / decision
- **reasoning** column: reasoning / explanation / rationale
- **category** column: category / risk_category / policy

Verdict canonicalization via `SAFETY_VERDICT_ALIASES` map:
- allow / safe / pass / ok → "allow"
- block / unsafe / refuse / reject / deny → "block"
- escalate / review / maybe → "escalate"

Rows with missing/unrecognized verdict → ValueError (data-quality
guard). Aliases are case-insensitive after `.strip().lower()`.

### 新 verifier `safety_judge_stub`

- Wired into `score_record` dispatch
- M0 oracle baseline: case-insensitive contains-match on the canonical
  verdict in candidate output
- "judge_stub" suffix signals that real judge-model scoring is M2
  task029 (safety) territory
- Diagnostics: `expected_verdict` + `verdict_match`

### data_registry row 故意延后

`m0_safety_reasoning_smoke` data_registry row deferred to Session 5.5.
Two pin-blockers:
1. Real Nemotron-Safety commit SHA via HF API
2. **Schema verification** — README explicitly warns the upstream
   dataset viewer reports schema errors; need to inspect real rows
   before locking the row schema

### Tests (`test_nemotron_safety_reasoning.py`, 37 cases)

- Module surface 4: SYSTEM_PROMPTS / CONVERTERS / canonical verdict
  set / common aliases
- _canonicalize_safety_verdict 4: case-insensitive / strips whitespace /
  None for empty / None for unrecognized
- Happy path per verdict 5 (parametric × 3 + reasoning + category)
- Optional-field handling 1
- Alias resilience 13 (parametric: 3 prompt-keys + 5 verdict-keys +
  3 reasoning-keys + messages-list format + 3 synonym verdicts)
- Error surfaces 3: missing prompt / unrecognized verdict / missing verdict
- safety_judge_stub verifier 4: dispatches / no-match / case-insensitive /
  empty expected returns zero
- Registry integration 3: validate_registries / env_registry shape /
  data_registry row deferral lock

Sandbox 测试基线 747 → **784 passed + 7 skipped** (37 new).

## task057 状态

- Sessions 1+2+3+4+5 ✓
- Sessions 1.5/2.5/3.5/4.5/5.5 ☐ — HF SHA pins (5.5 also needs schema verification)
- Session 6 ☐ — math_with_tools (`MathLLMs/MathCodeInstruct`)

Roadmap §5b 更新.
