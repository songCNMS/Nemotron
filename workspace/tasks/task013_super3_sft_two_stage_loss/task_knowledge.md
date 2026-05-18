# task013 - task_knowledge

## Plan §5.1 两阶段 SFT loss

> 先 token-level，再 sample-level

读这条 plan note 的语义：

1. **Stage A** = 标准 token-level cross-entropy SFT。一个 epoch 的 packed
   parquet，每个 unmasked token 等权重进 loss。今天 SFT 路径就是这样。
2. **Stage B** = 第二个 optimizer pass，从 Stage A 的 checkpoint 拾起，跑
   同一份数据 (或 sub-set)，但 loss 改成 **per-sequence mean → batch mean**。
   每个 sample 一票，跟它的 length 无关。

为什么要分两阶段而不一阶段就 sample-level?
- 早期收敛靠 token-level 信号密度高、每 step 更新方差小
- 收敛后再 sample-level 校准模型对长 vs 短 prompt 的均匀偏好
- 这就是 NemoTron / NeMo-RL 团队的工程直觉，roadmap §1.2 没明文写为什么但
  历史上 nano-2 RLHF 那一篇有提

## 今天 SFT loss 路径

`src/nemotron/recipes/super3/stage1_sft/train.py:372`：
```python
finetune(config=cfg, forward_step_func=forward_step)
```

`forward_step` 直接从 `megatron.bridge.training.gpt_step` 导入。Megatron-
Bridge 内部 `gpt_step.forward_step` 大致是：

```python
def forward_step(data_iterator, model):
    tokens, labels, loss_mask, attention_mask, position_ids = get_batch(data_iterator)
    output_tensor = model(tokens, position_ids, attention_mask, labels=labels)
    return output_tensor, partial(loss_func, loss_mask)

def loss_func(loss_mask, output_tensor):
    losses = output_tensor.float()           # (batch * seq_len,) per-token loss
    loss_mask = loss_mask.view(-1).float()
    loss = (losses * loss_mask).sum() / loss_mask.sum()  # ← token-level mean
    return loss, {"lm loss": loss.detach()}
```

Sample-level 改：

```python
def sample_level_loss_func(loss_mask, output_tensor):
    # reshape both back to (batch, seq_len)，调用 compute_sample_level_loss
    loss = compute_sample_level_loss(output_tensor, loss_mask)
    return loss, {"lm loss": loss.detach()}
```

## Dispatch 模式 (omni3 既有)

`omni3/stage0_sft/train.py:103-135` 已经有：
```python
_STEP_FUNCTIONS = {
    "audio_lm_step": "megatron.bridge.training.audio_lm_step:forward_step",
    "gpt_step": "megatron.bridge.training.gpt_step:forward_step",
    "vlm_step": ...,
}

def _load_forward_step(name): ...   # short name OR module:attr spec
```

super3/stage1_sft 没有这个表 — task013 抄过来 + 加一行：
```python
"super3_sample_level_step": (
    "nemotron.recipes.super3.stage1_sft.sample_level_step:forward_step"
),
```

放在独立的 `step_dispatch.py` 而不是 `train.py` 里的关键原因：
`train.py` 模块 top import 一大堆 (`torch`, `megatron.bridge.*`,
`omegaconf`)，sandbox 没装这些；dispatch 抽出来后单独可测，不用 stub 所有
重 deps。

## Adapter 的 loss_mask 抠法

Megatron-Bridge `gpt_step.forward_step` 返回:
```python
(output_tensor, partial(loss_func, loss_mask))
```

Adapter 这么拿 mask：
```python
output_tensor, bound_loss_func = upstream_forward_step(data_iterator, model)
loss_mask = bound_loss_func.args[0]  # partial 第一个位置参数
return output_tensor, partial(sample_level_loss_func, loss_mask)
```

这条**没在 sandbox 验过**（gpt_step 是 nvcr container 里的 closed-source
upstream），Session 2 cluster 第一次跑可能要调。`functools.partial.args`
访问 fallback 路径 raise 一条建议"pin megatron-bridge to the tested
version"的错误，方便 ops 排错。

## 边界 case (loss helper)

| 输入 shape | 处理 |
|---|---|
| (batch, seq_len) — 标准 | 直接算 |
| (batch * seq_len,) flat — adapter 路径 | adapter 重 reshape 回 (batch, seq_len) 再传 helper |
| 1D 不是 batch * seq_len 倍数 | adapter 做 single-sample fallback（degenerates 到 token-level；Session 2 cluster 看实际 shape 调） |
| 形状不一致 | `ValueError("share shape")` |
| `loss_mask.sum(-1) == 0` 某些 row | `clamp(min=1)` 避免 div0，然后 `has_signal` mask 过滤 |
| 整 batch fully masked | 返 0.0，**不要 NaN** (NaN 会 propagate 进 optimizer 把 run 杀掉) |
| bf16 输入 | 自动 `.to(float32)` 防长 seq overflow |

## Why 这个 helper 不能直接挂 gpt_step?

`compute_sample_level_loss` 只是数学。挂上 gpt_step 需要：
1. 知道 gpt_step 返回的 loss tensor shape 到底是 (batch, seq_len) 还是
   flat (batch * seq_len,)
2. loss_mask 是不是同样的 shape
3. 数据 iterator 里 batch_size 是不是 micro_batch_size 还是 global

这些都得在 nvcr container 里跑一遍才能确定。Session 1 的契约就是：
**math 稳了 (pytest 卡死)，wiring 写好 (sample_level_step.py 占位)，配置
打通 (dispatch + YAML key)；cluster 接 Session 2 跑过再调 shape 处理**。

## Session 2 driver 草图

```python
def run_two_stage_finetune(
    stage_a_config: Path,
    stage_b_config: Path,
    *,
    cli_overrides: list[str] | None = None,
) -> None:
    """Stage A token-level → checkpoint → Stage B sample-level."""
    run_finetune(stage_a_config, _default_recipe_builder, cli_overrides, tags=["stage-a"])
    stage_a_ckpt = _resolve_stage_a_checkpoint(stage_a_config)
    
    # Override Stage B's pretrained_checkpoint to point at Stage A output
    extra = [f"checkpoint.pretrained_checkpoint={stage_a_ckpt}"]
    run_finetune(stage_b_config, _default_recipe_builder,
                 (cli_overrides or []) + extra, tags=["stage-b"])
```

Test plan: mock `run_finetune` + 验证 driver 调两次 + 第二次带 stage-a 的
checkpoint override。Driver 不在本 PR — Session 2 一并落 YAML configs。

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| `sample_level_loss` math | yes (CPU torch；sandbox 缺 torch 时 importorskip 跳过) |
| `step_dispatch` 注册表 + 解析 | yes (纯 Python，无重 deps) |
| `sample_level_step` adapter 写法 | partial — 静态测能 import；运行时 cluster verify Session 2 |
| 端到端 finetune 真训 | no — 需 CUDA + nvcr Megatron-Bridge container |

## 与 task014-018 bridge 任务的区别

- task014-018 都是 *数据* bridge：M0 → NeMo-Gym JSONL，registry-driven。
  代码 80% 重复，等 task017 Session 4 抽 `_bridge_base.py`。
- task013 是 *训练循环* 修改：loss aggregation。完全不一样的 surface，
  没法跟 bridge 复用 base 模块。
- 共通：都用 import-time 派生 + sandbox importorskip 处理 missing deps。

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，pre-existing；非 sandbox 正常跑。
