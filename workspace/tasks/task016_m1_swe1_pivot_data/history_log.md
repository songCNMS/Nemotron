# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 roadmap §5 critical-path 第 6 条派生。task016 整 task：M0 → SWE1 数据
bridge + 真 SWE pivot 数据 converter + cluster smoke。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 SWE1 bridge skeleton。设计选择 + 实现要点：

- 新模块 `src/nemotron/recipes/super3/milestones/m1_swe1/`，跟 m1_rlvr/
  并列。Registry-driven shape 完全镜像 task015 Session 1 的模式：
  - `swe1_env_registry.yaml` 起步两行（一个 m0_missing 槽 + 一个
    verifier_mismatch 行）
  - `prepare_m1_swe1_jsonl.py` import-time 派生 `SWE1_PROFILE` /
    `SWE1_ENV_MAP`，今天 active=0
- **SWE1 简化点**：只有一个 NeMo-Gym env (`swe_pivot_single_step_tool_use_with_argument_comparison`)，所以不需要 `MIX_PROFILES` dict —
  单个 `SWE1_PROFILE`。`MIX_NAME = "swe1"` 在 registry 校验里被要求。
- `prepare()` 今天 raise coverage-aware ValueError（"no active M0 → NeMo-Gym
  mappings yet" + 列出 m0_missing/verifier_mismatch/blocked_external 给运维）。
  Session 2 落了 M0 SWE pivot env，registry 翻一行就 active；bridge 不需要
  Python 改动。
- 跟 m1_rlvr 的代码重复大约 80% — `_bridge_base.py` 抽取留给 task017 SWE2
  落第三版时做。
- 测试 `tests/recipes/super3/test_m1_swe1_data_bridge.py` 13 case：
  registry shape / 拒非-swe1 mix / 拒 unknown status / derive_env_map /
  conflict / coverage_report / SWE1_PROFILE artifact / env_map empty
  today / tag_record / prepare 今天 raise / prepare happy path
  (monkeypatch 注 active 行) / 非-swe1 env 过滤。

测试基线推到 88 passed (75 baseline + 13 swe1). `test_m1_agentic_sft.py`
在 sandbox 仍因缺 pyarrow collect-error pre-existing。

Roadmap §1.4 task016 + §5 critical-path 加 Session 1 ✓ + Session 2/3 ☐ 切片。

Session 2 (M0 SWE pivot 数据 converter) 不在本 PR：要看 SWE-Gym-Lite /
R2E-Gym 真实数据 shape，再决定从 agent trajectory 里怎么抽 "gold first
tool call"。
