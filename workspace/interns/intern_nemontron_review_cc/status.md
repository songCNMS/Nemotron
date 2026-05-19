# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task016_m1_swe1_pivot_data -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task016_m1_swe1_pivot_data |
| PR | pending push |
| Session | 65 |

正在做：task016 Session 2 (sandbox part) — M0 SWE-Gym-Lite → SWE pivot
tool-call converter。3 大件：

1. **新 M0 env + data row** (`swe_pivot_tool_call`):
   - `environment_registry.yaml` 加 env (verifier `argument_match`,
     max_turns 1, sandbox none)
   - `data_registry.yaml` 加 row 指 `SWE-Gym/SWE-Gym-Lite` (apache-2.0,
     contamination_against [SWE-Bench Lite, SWE-Bench Verified])

2. **新 converter** `transform_swe_gym_lite_pivot`:
   - 抽 trajectory 第一个 assistant 的第一个 tool call 当 ground truth
   - `expected_answer = {"name": ..., "arguments": <dict>}`
   - `responses_create_params.tools` 固定 4 工具 schema
   - `extra_env_info.pivot_type` ∈ {exploration, action}：view/search/
     grep/ls/find_file 标 exploration

3. **SWE1 registry 翻面**：`m0_missing` → `active`，
   `SWE1_ENV_MAP = {"swe_pivot_tool_call": "swe_pivot_single_step_tool_use_with_argument_comparison"}`

20 个新 pytest case + 修 2 个 swe1 bridge today-tests
(`test_swe1_env_map_empty_today` → 翻面 + `test_prepare_raises_coverage_aware_error_today` → monkeypatch all-inactive)。
sandbox 测试基线 421 → 441 passed + 7 skipped。

task016 整 task：Session 1 ✓ + Session 2 sandbox 部分 ✓；真 HF download
+ revision pin + cluster smoke (Session 3) 仍待。

Audit 全 clean：validate_data_registries / check-revision-pins (TBD 不
在 floating refs，技术上 pass) / check-contamination 三个都 ok。
