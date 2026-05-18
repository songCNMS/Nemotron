# task021_m1_infra_minimum

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #30 / 09c9089 on 2026-05-18 -->

## 背景

`docs/implementation-roadmap.md` §1.8 把这个 task 标成 critical-path 前置：
"M1 infra minimum (lineage + telemetry; everything downstream depends
on this)"。四个子条目 (plan §10 M1 infra):

1. NeMo-RL / Ray / vLLM / NeMo-Gym launch path 在真集群上验证
2. Code-exec / Lean / terminal 的 SIF/Docker/Podman sandbox 构建脚本
3. W&B artifact lineage 链：`RawDataArtifact → SFTDataArtifact →
   ModelArtifact-sft → RLVR{1,2,3} → SWE{1,2} → RLHF → EvalReport`
4. Per-env telemetry emitter (reward / latency / timeout / crash /
   invalid_tool_call / overlong)；env_registry 列了名字但没人 emit

整块太大，一个 PR 装不下；拆 Session。

## Session 切片

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | M0 oracle health-baseline 加 per-env telemetry 发射 | yes | ✓ Done (PR #30 `09c9089`) |
| 2 | cross-stage lineage 模型 schema + M0 / M1 manifest 加 `lineage` 字段 | yes (schema + walker; W&B publish 留 Session 3+) | ✓ Done (this PR) |
| 3 | Sandbox container 构建脚本 (code-exec、Lean、terminal Dockerfile + CI build) | partial (脚本 yes, push 到 registry 留 ops) | Todo |
| 4 | NeMo-RL / Ray / vLLM / NeMo-Gym launch path 真集群验证 | no — 需要 cluster + ops | Todo (block on NemTron access) |

## Session 1 目标

env_registry 今天列了每个 env 的 telemetry 名字 (`latency_ms`、`timeout`、
`invalid_tool_call`、`argument_match`、`tests_passed`、`runtime_error` …)
但没有任何一行代码真的 emit 它们。把 `run_m0_health_baseline.py` 改成：

- 在 `score_record` / 各 verifier 层包一层 timing + 提取 per-verifier
  的 telemetry，落到现有的 `diagnostics` 字典 (无 schema breakage)。
- `aggregate_scored_rows` 增加 `telemetry: {<name>: {mean, max, count, …}}`
  汇总，规则按字段语义：数值字段取 mean/max/p99，bool 字段取 true_count /
  false_count。
- `build_report` 把 telemetry 加进 health_baseline_report.json + .md。
- `summarize_health` 增加 cross-check：env_registry 声明的 telemetry
  名字必须 (a) 都在本 env 的 telemetry block 出现，或 (b) 显式标记
  "not yet emitted (future emitter)"。这样 env_registry 不再"撒谎"，
  unknown 项变成已知缺口。

值在 M0 oracle 阶段几乎都是 trivial (latency ≈ 0、oracle 永远对所以
`invalid_tool_call=False`)，但是 **shape 即合约** —— stage2_rl runtime
后续用 model candidate 跑同一段 score_record 时，同样的字段名直接装上
真值，下游 (W&B / Grafana dashboard / shadow eval) 不需要再改 schema。

## Session 1 验收

- [x] `score_record` 改成返回带 telemetry 的 diagnostics dict (无 API 改动)
- [x] 每个 verifier 至少 emit `latency_ms`；针对性条目：
  - `tool_schema_and_argument_match`: `invalid_tool_call`, `argument_match`
  - `python_unit_tests`: `timeout`, `runtime_error`, `returncode`
  - `command_substring_match`: `command_match`
  - `patch_diff_match`: `patch_match`, `malformed_diff`
  - `negative_recognition`: `repair_target_match`
- [x] `aggregate_scored_rows` 汇总 telemetry block
- [x] `summarize_health` cross-check declared-vs-emitted；缺口写进 status
- [x] `health_baseline_report.{json,md}` 都展示 telemetry
- [x] 新增 ≥ 4 个 pytest case
- [x] Roadmap §1.8 + §5 critical-path 把 Session 1 标 ✓；Session 2-4 留作 InProgress
- [x] M0 expansion plan §1.1 / §5 wiring rules 不需要改 (telemetry 是 M0 内部，不影响新 env 加入流程)

## 依赖

- 不依赖任何外部服务 (cluster / W&B / Docker)
- 不依赖 task013 (two-stage SFT loss) / task056 Session 2 (Lean)

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml` — telemetry 名字源头
- `tests/recipes/super3/test_m0_health_baseline.py`
- `docs/implementation-roadmap.md` §1.8 + §5
- plan §10 M1 infra 子段
