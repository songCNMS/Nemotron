# task_knowledge

<!-- METADATA:SESSION=0 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### Plan §8 vs 现状映射

`docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §8 把 Agentic SFT v0 切成 6 项；M0 + task001-004 落地了 search / tool call / reasoning / code，余下 4 项（terminal、structured output、short SWE traces、负例）在 M1 现有数据流里完全缺失。

### 负例数据合成路径

Hermes `func_calling_singleturn` 已经是合规的 baseline。task005 D 项的两种负例可以从这里派生：

- `malformed tool call`: 在已校验过的 `<tool_call>{...}</tool_call>` 里制造可恢复错误（缺逗号、错 key、值类型不符），保留 ground-truth 修复版供 SFT 学习 "识别 + 修复"。
- `hallucinated tool output`: 替换 tool turn 为 schema-相邻但语义错误的 JSON，要求 assistant 不要直接采信。

合成时务必同时写出 `metadata.negative_kind` / `metadata.repair_target`，否则 M1 RL repair 阶段无法消费。

### 新环境 verifier 与 health gate 的关系

`run_m0_health_baseline.py` 的 `score_record` 是 verifier dispatcher。新增 environment 时若没注册 verifier，oracle baseline 会落到 `return 0.0, {"error": f"unsupported verifier: ..."}` 分支，整张表会被 `overall_status` 判 fail。新加 supervision 数据之前必须先在 dispatcher 里加 stub（哪怕只是 substring match），否则会推不动 M0 health gate。

### Structured output 最稳数据源

Hermes `json_mode_singleturn` 与当前 `general_tool_calling` 使用同一个 HF dataset/revision/license：`NousResearch/hermes-function-calling-v1@dae3e1d28cfbcf4b915c04ea1e072030529b4bda`，license `apache-2.0`。样本字段包括 `conversations`、`schema`、`category`、`subcategory`，assistant turn 是 JSON 字符串；适合直接转成 `structured_outputs_json`，verifier 用解析后的 JSON value exact match。
