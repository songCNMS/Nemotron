# task014_m1_rlvr_data_bridge

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #34 / 4a50941 on 2026-05-18 -->
<!-- SESSION 2 LANDED: PR pending on 2026-05-19 (bridge combined.jsonl + data_prep/rlvr1.yaml flip + smoke.yaml; sandbox part only —真 launch 仍走集群) -->

## 背景

`docs/implementation-roadmap.md` §1.3 / §5 critical-path 第 4 条:

> task014 — M1 RLVR data bridge (smoke-run-able from M0 in one day).

今天 `stage2_rl/stage1_rlvr/config/data_prep/{rlvr1,rlvr2,rlvr3}.yaml` 三个
都指向 `/lustre/fs1/portfolios/coreai/projects/coreai_dlalgo_nemorl/users/yifuw/...`
这条 NVIDIA 内部路径，**M0 → RLVR 完全没接起来**。M0
`prepare_m0_assets.py` 已经按 NeMo-Gym 合约 shape 输出 (`environment`、
`responses_create_params`、`reward_config`、`extra_env_info`)，所以 bridge
本质是 mapping + slicing，不是再做一次 shape 转换。

整 task 拆 Sessions：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | `prepare_m1_rlvr_jsonl.py` (M0 → RLVR1 JSONL bridge，NeMo-Gym env map，lineage 接 M0 manifest) | yes | ✓ Done (PR #34) |
| 2 | RLVR1 config wiring + smoke launcher (`nemotron super3 rl rlvr1 -c smoke`) — flip `data_prep/rlvr1.yaml` 指向 M0-derived artifact | partial (config syntax 可以验证 sandbox，真 launch 走集群) | ✓ Done sandbox part (this PR); 真 launch 仍走集群 |

## Session 1 目标

`src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py`：

- 读 M0 split (`<env>/<split>-split.jsonl`) + M0 `manifest.json`
- 按 `RLVR1_ENV_MAP` 过滤到 4 个 env (math/code/search/tool-calling)
- 每行打上 `nemo_gym_env` + `nemo_gym_mix` 字段；**保留 M0 `environment` 不变**
  以保证 health-baseline / lineage 双向 self-consistent
- 输出 `train.jsonl` / `val.jsonl` / `manifest.json` (shape 跟 `SplitJsonlDataArtifact` 兼容)
- Emit lineage block：artifact_type=`RLVR1`，单个 `manifest`-kind input 指 M0 manifest
- `MIX_PROFILES` 预留 `rlvr2` / `rlvr3` 槽 (env_map 暂空) — 等 task015 接

## Session 1 验收

- [x] 新模块 `m1_rlvr/{__init__,prepare_m1_rlvr_jsonl}.py` + 双导入路径 (package + 直跑 fallback)
- [x] `RLVR1_ENV_MAP` 4 个 mapping 严格按 roadmap §1.3
- [x] `tag_record` 不动 M0 contract 字段，只往 metadata 加 NeMo-Gym tags
- [x] `prepare()` 写 train/val.jsonl + manifest.json + report.md
- [x] `manifest.lineage.artifact_type == RLVR1`，`inputs[0].kind == "manifest"` 指 M0
- [x] `manifest.errors` 记录 missing split + missing env
- [x] 测试 ≥ 7 个 pytest case (env map 完整、tag_record 单测、prepare end-to-end、过滤、error 收集、lineage、unknown mix、rlvr2 unbuildable)
- [x] Roadmap §1.3 + §5 critical-path 加 Session 切片标记

## 依赖

- 不依赖外部集群 / W&B
- 不依赖 task013 (two-stage SFT loss) / task021 Session 3+ (sandbox containers)
- Lineage 用 task021 Session 2 落的 `RLVR1_ARTIFACT` 常量

## Session 2 不在本 PR

Session 2 要动 `stage1_rlvr/config/data_prep/rlvr1.yaml` 让 `input_path` 指
M0 artifact，加 `config/smoke.yaml`，验证 `nemotron super3 rl rlvr1 -c smoke`
能跑通。Sandbox 只能验证 YAML 合法 + `_data_prep_base.py` 的 split path，
真 launch (Ray / vLLM / NeMo-Gym 起服务) 必须上集群——所以拆 Session。

## Session 2 目标 (sandbox part)

1. **Bridge extension** — `prepare_m1_rlvr_jsonl.py` 加 `combined.jsonl`
   输出 (train + val concat，val 在最末)，让 `_data_prep_base.split_local_jsonl`
   按 `val_holdout` re-split idempotent
2. **`data_prep/rlvr1.yaml` flip** — `input_path` 从 `/lustre/.../yifuw/...`
   改成 templated `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr1/combined.jsonl`
   + 补 M0 → bridge → data_prep pipeline 注释 + `val_holdout` 操作指引
3. **`stage1_rlvr/config/smoke.yaml`** — 最小 cluster footprint training
   config (2 nodes / 8 prompts/step / 4 train batch / max_num_steps=10 /
   val_at_end=true)，inherits `default.yaml`
4. **Tests** (12 cases): combined.jsonl shape + lineage / data_prep yaml
   shape / smoke yaml shape + footprint < small.yaml

## Session 2 验收 (sandbox part)

- [x] Bridge writes combined.jsonl alongside train/val.jsonl
- [x] Combined = concat(train, val); val rows are last N
- [x] Manifest 加 `combined_path` 字段
- [x] Lineage outputs 加 `m1_rlvr_combined_jsonl` kind
- [x] `data_prep/rlvr1.yaml` 不再含 /lustre 或 yifuw 路径
- [x] `data_prep/rlvr1.yaml` `input_path` 指 combined.jsonl 且 templated
- [x] `data_prep/rlvr1.yaml` 保留 SubStageDataPrepConfig 期望的全部字段
- [x] `smoke.yaml` defaults: default.yaml; grpo + policy + cluster 全存在
- [x] `smoke.yaml` footprint < `small.yaml` (nodes / prompts / batches)
- [x] `smoke.yaml` 显式 `max_num_steps` ≤ 100 + `val_at_end=true`
- [x] 12 个 pytest case；sandbox 测试基线 409 → 421 passed + 7 skipped

## Session 2 不在本 PR (cluster part)

- 真 `nemotron super3 rl rlvr1 -c smoke` 启动 (需 Ray + vLLM + NeMo-Gym 服务)
- W&B telemetry publish
- 真 SFT base checkpoint resolve (`super3-sft-model:latest`)
- nemo_gym genrm / judge services 起来 + reward signal sanity

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py` — M0 contract shape
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` — sibling bridge 模板
- `src/nemotron/recipes/super3/stage2_rl/_data_prep_base.py` — RL data-prep loader (Session 2)
- `src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/default.yaml` — RLVR1 GRPO config
- `src/nemotron/recipes/super3/milestones/lineage.py` — RLVR1_ARTIFACT 常量
- plan §5.3 + roadmap §1.3 / §5
