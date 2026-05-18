# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### `load_difficulty_signal` 三种 quiet-failure 模式

修复前函数对以下三种情况都 `return {}` 而不发任何信号，结果 manifest 里每条 row 都变成 `difficulty_bucket=unknown`，operator 看不出来是配置错了还是数据真的没标注：

1. **文件不存在**：path 指向不存在的文件 / auto-resolve 落空。
2. **JSON 解析失败**：truncated 或 hand-edit 时引号写错。
3. **shape 错误**：`baselines.environments` 不是 mapping（手写测试数据常见）。

task010 之后每条路径都 `logger.warning` 命名 underlying exception。新增 3 个回归用例覆盖（gate by ability to import path module）。

### `_difficulty_for` 的 split tag rewriting 发生在 manifest summary 层

虽然 manifest `counts` / `difficulty_buckets` 用 `"val_shadow"` 当 key，但实际 `convert_split` 给 `convert_m0_record` 传的 split 一直是 M0 原始 split name `"train"` / `"val"`。所以 `_difficulty_for` 里面写 `"val_shadow" → "val"` 翻译是死代码 —— signal map 也是 M0 split keyed，直接 verbatim 查就行。

### omegaconf 在 test env 是 optional

NemTron 上 omegaconf 是 megatron-bridge / nemo_runspec 的传递依赖，所以装环境时一定在。但本地 sandbox / 简化 CI 容器里不一定有。pre-task010 三个 test (`m1_agentic_smoke_yaml_pretrained_checkpoint_resolves_without_env`、`qwen_local_train_*`) 在 import 阶段就 fail。

task010 之后所有依赖 omegaconf 的测试都走 `pytest.importorskip("omegaconf")`，跟 cosmos_xenna / megatron.bridge gate 同 pattern。这条约定也适用于将来加新的 SFT 相关测试 —— 如果只是 import 路径会触发 omegaconf import，gate 应该写在 test body 顶部，而不是 module top。
