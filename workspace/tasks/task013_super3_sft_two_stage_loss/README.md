# task013_super3_sft_two_stage_loss

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #44 / 10e1393 on 2026-05-18 -->

## 背景

REVIEW_v0.md #9 / plan §5.1：

> 先 token-level，再 sample-level

今天 SFT 走 `megatron.bridge.training.gpt_step.forward_step`，loss 在所有
unmasked token 上算 mean — 长 assistant turn 占主导，每个样本的有效权重
跟长度成正比。Plan §5.1 要求第二段 optimizer pass 用 sample-level loss
(per-sequence mean → batch mean)，让每个样本权重相同。

整 task 拆 Sessions (Session 2 拆 sandbox / cluster two parts per 2026-05-19 roadmap refinement)：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | `forward_step` dispatch (`_STEP_FUNCTIONS` 像 omni3) + `sample_level_loss` 纯 torch helper + `sample_level_step` adapter | yes (math + dispatch；adapter cluster verify 等 Session 2b) | ✓ Done (PR #44) |
| 2a | 两阶段 driver (`run_two_stage_finetune`) + stage-a/stage-b YAML 链 — sandbox 验 driver 派发 + YAML 加载 + stage A checkpoint path resolution | yes | Todo |
| 2b | Cluster verify (真训 stage A → stage B) | no — 需 CUDA + nvcr Megatron-Bridge container | Todo |

## Session 1 目标

镜像 omni3 dispatch 模式但用单独 module 让 sandbox 可测：

1. **`sample_level_loss.py`** — 纯 torch helper:
   - `compute_token_level_loss(loss_per_token, loss_mask)` — baseline，跟今天行为对照
   - `compute_sample_level_loss(loss_per_token, loss_mask)` — per-sequence mean → batch mean over non-empty samples
   - `loss_aggregations_diverge(...)` — sanity diff helper for tests
   - 边界：fully-masked batch → 0 (不是 NaN)；mismatched shape → ValueError
   - bf16 input 自动 promote 到 float32 防 overflow

2. **`sample_level_step.py`** — Megatron-Bridge `forward_step` adapter:
   - `sample_level_loss_func(loss_mask, output_tensor)` 跟 gpt_step.loss_func 同款签名
   - `forward_step(data_iterator, model)` 委派 upstream gpt_step.forward_step
     拿 `(output_tensor, partial(loss_func, loss_mask))`，从 partial.args 把
     loss_mask 抠出来，包一层 `partial(sample_level_loss_func, loss_mask)` 返回
   - 不带 cluster verify — Session 2 拿 nvcr container 跑过再说

3. **`step_dispatch.py`** — 独立模块（不引 megatron / torch / omegaconf）:
   - `_STEP_FUNCTIONS: dict[str, str]` 起步两行 (gpt_step + super3_sample_level_step)
   - `_load_forward_step(name)` 支持 short name OR `module:attr` spec
   - sandbox 可直接测，不需 stub heavy deps

4. **`train.py` 接入**:
   - 从 `step_dispatch` import 三个符号
   - 保留 `forward_step = _gpt_step_forward_step` 向后兼容 export
   - `finetune(...)` 前读 `OmegaConf.select(config, "step_function", default=None)
     or "gpt_step"`，用 dispatch 派出 callable
   - 默认 `gpt_step` → 现有 YAML 一行不改 byte-for-byte 同行为

## Session 1 验收

- [x] `sample_level_loss.py` + 7 个 pytest case (equal-length / uneven-length / fully-masked row / all-masked batch / shape validation / dtype promotion)
- [x] `sample_level_step.py` 写完 (cluster verify 留 Session 2)
- [x] `step_dispatch.py` 独立模块 + 5 个 pytest case (registry shape / module:attr spec / unknown name / gpt_step 路由 / sample-level 路由)
- [x] `train.py` 接入 dispatch；默认 `gpt_step` 保持向后兼容
- [x] 至少 11 个 pytest case
- [x] Roadmap §1.2 / §5 critical-path REVIEW #9 状态从 ✗ → ⚠ (Session 1 ✓)

## 依赖

- 不依赖 cluster / GPU / W&B
- pure-torch helper 在 sandbox 可独立测（即使 torch 缺则 importorskip
  跳过；非 sandbox 环境正常跑）
- 不依赖 task014/15/16/17/18 等 critical-path

## Session 2a (sandbox part) 目标 — pickable as next sandbox-runnable session

Per 2026-05-19 roadmap refinement: Session 2 was originally bundled
("driver + YAML chain + cluster verify"), but the driver function +
YAML chain CAN be sandbox-tested:

1. **`run_two_stage_finetune(config_path_a, config_path_b)` driver** —
   stub the actual training call; verify the driver:
   - Loads `config_path_a` → calls `finetune()` with `step_function=gpt_step`
   - Captures the stage A checkpoint path from config / cli override
   - Loads `config_path_b`, resolves `${stage_a_checkpoint_path}` to the
     stage A output, calls `finetune()` with `step_function=super3_sample_level_step`
   - Sandbox tests inject a fake `finetune` that records the calls
2. **`config/stage_a_default.yaml`** — token-level, copy of today's
   default (sandbox test: yaml load + omegaconf resolution + `step_function`
   field defaults to `gpt_step`)
3. **`config/stage_b_default.yaml`** — sample-level:
   ```yaml
   step_function: super3_sample_level_step
   recipe:
     _target_: megatron.bridge.recipes.nemotronh.nemotron_3_super.nemotron_3_super_sft_config
   checkpoint:
     pretrained_checkpoint: "${stage_a_checkpoint_path}"
   ```
   (sandbox test: yaml load + step_function == sample_level + checkpoint
   field references stage_a path)
4. **Tests** (~10): driver dispatch / checkpoint path resolution / both
   yaml load clean / yaml + dispatch cross-walk

## Session 2b (cluster part) 不在本 PR

集群上一次端到端跑：验 stage A 出 checkpoint → stage B 拾起 → loss
曲线收敛 + W&B 上 `lm loss` 跟 stage A 比 (期望相近，但 sample 权重均
匀让方差降)。在 nvcr Megatron-Bridge container 里跑；sandbox 不行。

## 参考文件

- `src/nemotron/recipes/super3/stage1_sft/` — 本 task 改动
  - `sample_level_loss.py` (新)
  - `sample_level_step.py` (新)
  - `step_dispatch.py` (新)
  - `train.py` (改：接入 dispatch)
- `src/nemotron/recipes/omni3/stage0_sft/train.py` — dispatch 模板源头 (lines 103-135)
- `src/nemotron/recipes/super3/stage1_sft/README.md` — SFT stage 文档
- REVIEW_v0.md #9 + plan §5.1 + roadmap §1.2
