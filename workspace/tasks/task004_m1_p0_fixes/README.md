# task004_m1_p0_fixes

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

`src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md` 列出的 P0 两条仍未解决：

- **#2 GBS×DP×MBS guard**：`plan_m1_agentic_sft_training.py` 默认 `--global-batch-size 4` × `--gpus-per-node 8` × `--micro-batch-size 1` 不满足 `GBS ≥ DP × MBS`。Megatron 在 setup 阶段 assert，训练起不来。planner 只加了 `nodes != 1` guard，没加 GBS/DP guard。
- **N2 smoke yaml regression**：PR #10 把 `m1_agentic_smoke.yaml` 的 `pretrained_checkpoint` 改成 `${oc.env:SUPER3_M1_PRETRAINED_CHECKPOINT}`（无 default），但 smoke 路径是 `finetune: false`（random init）。`train.py:367` 无条件 log `cfg.checkpoint.pretrained_checkpoint` 触发 OmegaConf `MissingMandatoryValue`，offline smoke 跑不起来。

## 目标

修这两条 P0 + 加回归测试 + 在 REVIEW_v0.md 标 ✓ Fixed。

## 验收

- [ ] `plan_m1_agentic_sft_training.build_plan` 在 `global_batch_size < dp_size * micro_batch_size`（取 `dp_size = gpus_per_node * nodes`）时显式 `raise ValueError`，错误信息说明应取的最小 GBS。
- [ ] `--global-batch-size` 默认从 4 改为 8（与默认 `--gpus-per-node 8 * --micro-batch-size 1` 匹配）。
- [ ] `m1_agentic_smoke.yaml` 的 `pretrained_checkpoint` 改回 YAML literal `null`，让 `finetune: false` 不强制要求 env var。
- [ ] `tests/recipes/super3/test_m1_agentic_sft.py` 新增 2 个 regression case：
  - 默认 GBS=8 / GPUs=8 / MBS=1 通过；GBS=4 / GPUs=8 / MBS=1 抛 ValueError
  - smoke yaml 的 `pretrained_checkpoint` 在没设 env var 时被 OmegaConf 解析为 `None` 而不是 raise
- [ ] REVIEW_v0.md 加 v3 状态行（或更新 v2 表格），把 #2 与 N2 标 ✓ Fixed by task004。
- [ ] `PYTHONPATH=src pytest tests/recipes/super3/` 全绿。
