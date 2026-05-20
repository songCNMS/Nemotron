# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task057_m0_tier2_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task057_m0_tier2_expansion |
| PR | pending push |
| Session | 6 (last) |

正在做：task057 Session 6 — `math_with_tools` env via
`MathLLMs/MathCodeInstruct`. Final tier-2 M0 env (6 of 6).

## What's in this PR

### 新 M0 env `math_with_tools`

- `environment_registry.yaml` 加 env: family `reasoning` / verifier
  `math_with_tools_match` / max_turns 1 / sandbox none
- Required fields `extra_env_info.reference_solution` +
  `extra_env_info.has_code_block` for the health gate
- `SYSTEM_PROMPTS`: "tool-using math assistant; use Python where
  helpful; put final answer in \\boxed{}"

### 新 converter `transform_mathcode_instruct`

Permissive field-alias support (upstream snapshots vary):

- **problem** column: problem / question / instruction / input
- **solution** column: solution / response / output / answer

Preserves full solution text in `extra_env_info.reference_solution`
so SFT supervision keeps the code-block trace verbatim. Extracts
final `\\boxed{...}` answer using the existing `extract_boxed_answer`
helper. Detects Python code blocks via new `PYTHON_CODE_BLOCK_RE`
matching both fenced ` ```python ... ``` ` and `<python>...</python>`
tagged forms.

Rows without problem / solution / `\\boxed{}` final answer → ValueError
(data-quality guard).

### 新 verifier `math_with_tools_match`

- Wired into `score_record` dispatch via local import (same pattern as
  `sql_execution_match`)
- M0 oracle behaviour: extract candidate's last `\\boxed{...}`,
  normalize (lowercase + whitespace-collapsed + strip_punctuation),
  contains-match against gold boxed answer
- Fallback: when candidate omits `\\boxed{}`, fall back to whole-
  candidate contains-match
- "_match" suffix signals real Python-execution + math-judge scoring
  is M1 task011 territory
- Diagnostics: `boxed_answer_extracted`, `has_code_block_in_candidate`,
  `normalized_answer`, `malformed_final_answer`

### 新 helper `is_numinamath_source_id` (dedup pre-wire)

Pure-function dedup helper for the cross-dataset overlap between
MathCodeInstruct and NuminaMath. Per task README the policy is
"重的全部移到 math_with_tools (因为它的代码块更有信息)" — drop
NuminaMath rows whose source_id appears in MathCodeInstruct. The
actual index construction is Session 6.5 territory (needs the SHA-
pinned NuminaMath snapshot); this PR ships the building block + locked-
in tests.

### data_registry row 故意延后

`m0_math_with_tools` data_registry row deferred to Session 6.5.
Two pin-blockers:
1. Real MathCodeInstruct commit SHA via HF API
2. **NuminaMath source_id index** — need to enumerate the SHA-pinned
   NuminaMath snapshot to build the dedup index before the bridge
   can drop overlapping rows

### Tests (`test_mathcode_instruct.py`, 45 cases)

- Module surface 4: SYSTEM_PROMPTS / CONVERTERS / fenced regex /
  tagged regex
- count_python_code_blocks 6: zero / None / fenced single / tagged
  single / multiple / non-python fences ignored
- Happy path 7: boxed extracted / reference solution preserved /
  has_code_block detection (fenced + tagged + absent) / last-boxed-
  when-multiple / system prompt injection
- Field-alias resilience 8 (parametric × 4 problem keys + × 4 solution
  keys)
- Error surfaces 4: missing problem / empty problem / missing solution
  / solution without boxed
- math_with_tools_match verifier 6: dispatches with boxed / no-match
  / fallback contains-match / whitespace normalize / diagnostics shape
  lock / candidate code-block detection
- is_numinamath_source_id 5: in / not in / empty source_id / empty
  index / iterable input
- Registry integration 5: validate_registries / env_registry shape /
  telemetry list lock / data_registry row deferral lock /
  extract_boxed_answer round-trip

Sandbox 测试基线 784 → **829 passed + 7 skipped** (45 new).

## task057 状态

- Sessions 1+2+3+4+5+6 ✓ — **all tier-2 envs landed**
- Sessions 1.5/2.5/3.5/4.5/5.5/6.5 ☐ — data_registry rows pending
  HF SHA pins (cluster-bound)
- Session 6.5 additionally needs the NuminaMath source_id dedup index

Roadmap §5b + Current state snapshot updated.
