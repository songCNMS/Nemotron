# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 REVIEW_v0.md #9 / plan §5.1 派生。task013 整 task：plan §5.1 两阶段 SFT
loss schedule (先 token-level 再 sample-level)，需要在 SFT 训练路径上加一
个第二轮 optimizer pass，aggregation 换成 per-sample mean。task013 是
roadmap §5 critical-path 第 9 条 (并列 task019/020 之前)，REVIEW #9 在
critical-path 八条 Session 1 都落地后仍 ✗ — 这次开掉。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 forward_step dispatch + sample-level loss helper + adapter skeleton。
设计：

- 这跟 task014-018 的 bridge 模式完全不同 — 没 registry，是训练循环里
  的 loss aggregation 修改。审计 omni3/stage0_sft/train.py:103-135 发
  现已有 `_STEP_FUNCTIONS` dispatch 模式，**这就是 roadmap 提到的 "需要
  Megatron-Bridge hook research first" 的那条路**：把 forward_step 改成
  通过 dispatch 表选，按 YAML `step_function:` key 拿不同实现。
- 新增 4 个模块：
  - `sample_level_loss.py`：纯 torch helper (compute_token_level_loss /
    compute_sample_level_loss / loss_aggregations_diverge)。处理边界
    case fully-masked batch → 0、bf16 → float32 promote、shape 校验。
  - `sample_level_step.py`：Megatron-Bridge `forward_step` adapter。委派
    upstream gpt_step 拿 (output_tensor, partial(loss_func, loss_mask))，
    从 partial.args 抠 loss_mask 包一层 sample-level 版返回。Cluster
    verify 留 Session 2。
  - `step_dispatch.py`：独立模块只 `import importlib`，注册表 + 解析器。
    放在独立模块的关键原因是 `train.py` import 大量 megatron-bridge /
    omegaconf / torch，sandbox 测不进去；dispatch 抽出来后单独可测。
  - `train.py` 接入：`forward_step = _gpt_step_forward_step` 保留向后兼
    容，`finetune(...)` 前 `OmegaConf.select(config, "step_function",
    default=None) or "gpt_step"` 派出 callable。默认 `gpt_step` →
    现有 YAML byte-for-byte 同行为。
- 测试 12 case 跨两个文件：
  - `test_sample_level_loss.py` 7 case (torch importorskip; sandbox 跳；
    cluster + 非 sandbox 跑过)
  - `test_sft_forward_step_dispatch.py` 5 case (sandbox 全跑)
- Sandbox 基线 125 → 130 (实际 collected 130 / 129 passed / 2 skipped；
  torch 缺把 sample_level_loss 整文件跳，dispatch 里的"resolve sample-
  level adapter"那条因为加载 sample_level_step 需要 torch 也跳)。
- `test_m1_agentic_sft.py` pyarrow collect-error pre-existing。
- Roadmap §1.2 REVIEW #9 状态 ✗ → ⚠ (Session 1 ✓)。§5 critical-path 加
  task013 作为第 9 条 ("Then in parallel" 段开头)。

数学的关键 case 拼 (`uneven_length_batch_diverges`)：

```
loss_per_token = [[1, 2, 3], [10, 0, 0]]
loss_mask      = [[1, 1, 1], [1, 0, 0]]
token-level    = (1+2+3+10) / 4         = 4.0   (sample 1 占 1/4 权重)
sample-level   = ((1+2+3)/3 + (10)/1) / 2 = 6.0 (两个 sample 各占 1/2 权重)
```

这一条把 plan §5.1 想表达的"长样本不再 dominate"的直觉落到具体数值，
任何人未来改 aggregation 都不会绕过它。

Session 2 (driver + YAML + cluster verify) 不在本 PR — 需 nvcr
Megatron-Bridge container 跑真训练。

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #44 已 squash-merge 为 `10e1393` 进 main — sample_level_loss
+ sample_level_step + step_dispatch + train.py 接入 + 12 个 pytest case
都进了 main。intern status 回 Idle (Session 32)。task013 整 task 仍
InProgress：Session 2 (run_two_stage_finetune driver + stage-a/stage-b
YAMLs + cluster verify) 没启动 — 需 nvcr Megatron-Bridge container 跑
真训练。

**里程碑**: roadmap §5 critical-path 9 条全部 Session 1 落地 ✓。下一个
候选：task017 Session 4 (`_bridge_base.py` 抽取，4 个 bridge module 都摆
稳) 或 task030 (unified data registry) 或之前 task 的 Session 2+ (大都
要 cluster)。

