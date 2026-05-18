# task015 - task_knowledge

## NeMo-Gym envs in stage1_rlvr/config/default.yaml (21 unique servers)

`nemo_gym.config_paths` (lines 327-352) 加载这些 server config:

```
math_with_judge
code_gen
workplace_assistant
mcqa
instruction_following
structured_outputs_json
equivalence_llm_judge (3 configs: lc_judge, nl2bash-equivalency, equivalence_llm_judge — 同一个 server)
calendar
genrm_compare
single_step_tool_use_with_argument_comparison
reasoning_gym
terminal_pivot
ns_tools
math_formal_lean_multi_turn
swerl_gen
jailbreak_detection
over_refusal_detection
multichallenge
inverse_if
search_pivot_single_step_tool_use_with_argument_comparison
toolcall_schema_single_step_tool_use_with_argument_comparison
```

注意：`search_grounded_qa` 和 `general_tool_calling` **不在这个列表里**。
task014 Session 1 的 `RLVR1_ENV_MAP` 引用了这两个不存在的名字，
task015 Session 1 修正了。

## Status state machine

```
m0_missing ─────────────── (task057 加 M0 env) ──────────→ active OR verifier_mismatch
                                                              ↓
verifier_mismatch ──── (task NeMo-Gym 侧调 verifier OR 加 --include-mismatched flag) ──→ active
                                                              ↓
blocked_external ────── (cluster ops 部署 judge model) ──────→ active

active ←————— state we want every row to be in
```

`active`：M0 emit rows + verifier 语义双侧一致。Bridge 默认包含。
`m0_missing`：没 M0 源。task057 加上就 unblock 一行。
`verifier_mismatch`：有 M0，但双侧 reward 信号方向不一致。如：
- `tool_call_repair_negative` (M0 reward 识别 malformed call) vs
  `toolcall_schema_single_step_tool_use_with_argument_comparison`
  (NeMo-Gym reward emit 正确 schema) — 同 family，方向相反
- `swe_pivot_patch_supervision` (M0 diff text 匹配) vs `swerl_gen`
  (NeMo-Gym apply diff + run tests) — 同数据，不同信号
- `terminal_basic_shell` (M0 command substring match) vs `terminal_pivot`
  (NeMo-Gym tool-use agent loop) — 同 family，不同 shape

`blocked_external`：cluster judge model / 法务 / 上游服务问题。
- `multichallenge` / `inverse_if` / `equivalence_llm_judge` — 需要
  `nl2bash_judge_model` (Qwen3-235B FP8) 部署
- `jailbreak_detection` / `over_refusal_detection` — 需要
  `nvidia/Nemotron-Content-Safety-Reasoning-4B` 部署
- `genrm_compare` — pref-data env，真应该是 task018 RLHF 范围
- `math_formal_lean_multi_turn` — 等 share-alike clearance (`nvidia/Nemotron-Math-Proofs-v1` CC-BY-SA-4.0)

## Mix 分配判断

Plan §5.3 没有给死哪个 env 进哪个 mix。Registry 这里的 mix 分配按 family：

| Mix | Family | 包含 |
|---|---|---|
| rlvr1 | foundations | math (gsm8k via math_with_judge), code (mbpp via code_gen), 单步 tool/search |
| rlvr2 | instruction following + structured + reasoning | math (NuminaMath via math_with_judge), structured outputs JSON, workplace_assistant, mcqa, instruction_following, calendar, reasoning_gym, multichallenge, inverse_if |
| rlvr3 | safety + advanced reasoning + tools | swerl_gen, terminal_pivot, ns_tools, math_formal_lean, jailbreak/over_refusal, equivalence_llm_judge, genrm_compare |

注意 `math_with_judge` 在 rlvr1 + rlvr2 都有行 (不同 M0 source: gsm8k vs
NuminaMath)。`derive_env_map(mix='rlvr2')` 只看自己那行；不冲突。

## RLVR1 audit table (task015 Session 1 correction)

| M0 env | task014 mapping | task015 mapping | 原因 |
|---|---|---|---|
| `math_reasoning_numeric` | `math_with_judge` | `math_with_judge` ✓ | 一致 |
| `code_execution_python` | `code_gen` | `code_gen` ✓ | 一致 |
| `general_tool_calling` | `general_tool_calling` ✗ | `single_step_tool_use_with_argument_comparison` | NeMo-Gym 没 `general_tool_calling`；verifier 都比对 args vs schema |
| `search_grounded_qa` | `search_grounded_qa` ✗ | (removed; registered as `m0_missing` for rlvr1 search_pivot) | NeMo-Gym 没 `search_grounded_qa`；HotpotQA single-hop ≠ search_pivot |

## Coverage 报告字段

每个 manifest 都带 `coverage` 块：
```json
{
  "mix": "rlvr2",
  "total_target_envs": 9,
  "counts": {"active": 2, "m0_missing": 5, "verifier_mismatch": 0, "blocked_external": 2},
  "active": ["math_with_judge", "structured_outputs_json"],
  "m0_missing": ["calendar", "instruction_following", "mcqa", "reasoning_gym", "workplace_assistant"],
  "verifier_mismatch": [],
  "blocked_external": ["inverse_if", "multichallenge"]
}
```

运维读 manifest 一眼就知道 "解锁 RLVR2 还差哪些 task057 envs + cluster ops"。

## Bridge 自动 pickup 机制

未来流程：

1. task057 在 M0 落 e.g. `reasoning_gym` env (M0 transform + registry + verifier)
2. 来 task015 这边修一行 registry：
   ```yaml
   - nemo_gym_env: reasoning_gym
     mix: rlvr2
     m0_env_id: reasoning_gym       # 之前 null
     status: active                  # 之前 m0_missing
     m0_verifier: reasoning_gym_programmatic
     license: ...
     hf_revision: ...
   ```
3. Bridge import 时自动把这行加进 RLVR2_ENV_MAP。下一次 `prepare()` 跑 rlvr2
   就会 emit reasoning_gym 行。
4. 测试 `test_registry_loads_with_expected_shape` 不需要改 — 它只看 ≥ 21
   总数。

不需要改 Python 代码，不需要改测试。这就是 registry-driven 的好处。

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，main 一样复现，pre-existing；非 sandbox 环境正常跑。不在
本 PR 范围。

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| `rlvr_env_registry.yaml` + `prepare_m1_rlvr_jsonl.py` + pytest | yes |
| rlvr1/rlvr2 prepare 跑出 manifest + JSONL + coverage | yes |
| 真集群上 NeMo-Gym router 把 nemo_gym_env 名字解析到 server | no — 这是 task014 Session 2 cluster verify 的 job |
| judge model 部署 + verifier 真出 reward | no — task018 / cluster ops |
