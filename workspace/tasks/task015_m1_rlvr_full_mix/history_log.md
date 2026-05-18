# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 roadmap §5 critical-path 第 5 条派生。task015 整 task：把 RLVR mix
从 task014 Session 1 的 4 envs (实际只有 2 个 NeMo-Gym 名字对得上) 扩展
到 21 envs (`default.yaml::nemo_gym.config_paths`)。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 registry-driven RLVR mix derivation。设计选择 + 实现要点：

- 新文件 `rlvr_env_registry.yaml` 全量声明 21 NeMo-Gym envs (一个 mix 列 +
  m0_env_id + status + 元信息)。Mix 分配按 family：
  - rlvr1 = math + code + 单步 tool/search 基础
  - rlvr2 = instruction following + structured output + reasoning
  - rlvr3 = safety + advanced reasoning + tools
- Status 4 值：`active` / `m0_missing` / `verifier_mismatch` / `blocked_external`
  - `active`: M0 有数据 + 双侧 verifier 语义对得上，bridge 默认包含
  - `m0_missing`: 没 M0 源，bridge 跳过，coverage 报缺口（task057 territory）
  - `verifier_mismatch`: 有 M0 但双侧 reward 信号不一致；bridge 跳过，给一个
    将来的 `--include-mismatched` flag 留口（Session 2+）
  - `blocked_external`: cluster judge 模型 / 法务 / 上游服务问题 —
    bridge 不管，coverage 标出来给运维
- `prepare_m1_rlvr_jsonl.py` 改造：`MIX_PROFILES` import-time 由
  `build_mix_profiles(load_rlvr_env_registry())` 算出来；RLVR{1,2,3}_ENV_MAP
  保留为 backward-compatible 模块常量但内容跟 registry 同步。
- Manifest 加 `coverage` 块 (mix counts + per-status env lists)；report.md 也
  加 Coverage section。这样运维看 manifest 一眼就知道 "rlvr2 active=2，
  m0_missing=5，task057 加进 workplace_assistant / mcqa / ... 就能涨"。
- rlvr3 没 active 行 → prepare() raise ValueError 里直接把 coverage 字典塞
  进去，错误信息自己解释为什么 + 解锁路径。

**关键 correction (task014 Session 1 后的 bug fix)**：

task014 Session 1 ship 的 `RLVR1_ENV_MAP` 里两个 NeMo-Gym 名字在
`default.yaml` 找不到：

| M0 env | task014 mapping | 实情 | Session 1 修正 |
|---|---|---|---|
| `general_tool_calling` | `general_tool_calling` | NeMo-Gym 没这个名字；最近的是 `single_step_tool_use_with_argument_comparison`，verifier 语义都比对 emitted tool-call args vs gold schema | rename to `single_step_tool_use_with_argument_comparison` |
| `search_grounded_qa` | `search_grounded_qa` | `default.yaml` 没这个 server；HotpotQA 是 single-hop 检索 QA，跟 `search_pivot_single_step_tool_use_with_argument_comparison` (pivot tool-use) shape 不匹配 | 从 active rlvr1 移除；登记 `m0_missing` 给 coverage |

错误如果走到集群 Session 2 才发现，Ray 起 server 会 fail or env router 死路。
现在 registry 派生 + Sandbox 测试覆盖了 audit。

测试 `tests/recipes/super3/test_m1_rlvr_data_bridge.py` 从 9 → 18 case：
新增 registry 加载、status 校验、`derive_env_map` 过滤、coverage 计数、
conflicting active rows 拒绝、rlvr2 active 含 math_competition + structured，
rlvr3 raise coverage-aware error，manifest 有 coverage 块。

Live coverage（main + 本 PR）：
- rlvr1: active=3 (math_with_judge, code_gen, single_step_tool_use_with_argument_comparison) / m0_missing=1 (search_pivot) / verifier_mismatch=1 (toolcall_schema)
- rlvr2: active=2 (math_with_judge[NuminaMath], structured_outputs_json) / m0_missing=5 / blocked_external=2 (multichallenge, inverse_if)
- rlvr3: active=0 / m0_missing=2 (ns_tools, swerl_gen[R2E]) / verifier_mismatch=2 (swerl_gen[SWE-bench-Lite], terminal_pivot) / blocked_external=5

测试基线推到 75 passed (52 baseline + 8 lineage + 9 chat + 6 telemetry +
增量 task014 + task015 = 75)。`test_m1_agentic_sft.py` 在 sandbox 仍因
缺 pyarrow collect-error，pre-existing。

Session 2+ 不在本 PR：bridge 这边不需要再改代码，等 task057 / task016 /
task056 Session 2 / cluster ops 把 m0_missing / verifier_mismatch /
blocked_external 一行一行翻成 active。Bridge 派生表自动 pickup。
