# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### env_registry telemetry 与运行时 emitter 的边界

`environment_registry.yaml` 每个 env 的 `telemetry: [...]` 列表是
**契约声明**：runtime 应当 emit 这些名字。task021 Session 1 之前没有
任何 emitter；Session 1 让 M0 oracle health-baseline 成为第一个
emitter。

Runtime 边界：

- **M0 baseline emitter (Session 1 之后存在)**: scorer 层包 timing +
  把 verifier-specific 信号挂到 diagnostics dict。值在 oracle 阶段
  几乎全部 trivial (latency ≈ 0、oracle 总是正确，所以 `argument_match`
  / `invalid_tool_call` / `returncode` 都是 happy-path)。Shape 即合约。
- **stage2_rl runtime emitter (未来)**: NeMo-Gym rollout 时调一次
  `score_record(model_candidate, record)`，同样的 telemetry 名字
  直接装上真值 — model 错的时候 `argument_match=False`、code-exec
  失败时 `returncode != 0`、超时时 `timeout=True`。下游 W&B /
  Grafana 不需要再改 schema。

加新 env / 新 verifier 时记得：

1. 在 env_registry 把名字声明出来。
2. 在 `score_record` 对应的 verifier 分支里把名字真 emit (用
   `_record_telemetry(name, value, kind)` 这种 helper，task021
   Session 1 期间引入)。
3. `summarize_health` 会 cross-check 声明 vs 真 emit，任何漂移会以
   `telemetry_gap` 字段写进 status。

### Verifier latency 含义

`latency_ms` 是 verifier 本身的执行时间，不是 model 的推理时间。在
M0 baseline 里只有 `python_unit_tests` 有真实的耗时 (subprocess
fork + python startup ~50-200 ms)；其他 string-match 类的 verifier
都在亚毫秒级。

到 RL runtime 时，"latency_ms" 字段含义会扩展为 `verifier_latency_ms`
+ `rollout_latency_ms` 拆开，避免把 model gen 时间和 verifier 时间
混在一起。Session 2+ 的 runtime emitter 应该 emit 两个字段。

### Session 1 不动 `score_record` 返回签名

为了不破现有 test (test_m0_health_baseline 里有 ~17 个 case 直接
解构 `score, detail = score_record(...)`)，Session 1 把 telemetry
**塞进 detail dict** 而不是改成 `(score, detail, telemetry)` 三元组。
未来想拆字段时，加一个 `score_record_v2` 返回三元组，旧的留 deprecation
alias 即可。
