# task058_production_dataset_slug_fixes

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## 背景

`docs/m0-dataset-expansion-plan.md` §4 列出 4 个跟 M0 扩展独立的生产线 bug，都跟数据集 slug / 字段命名 / 污染审计有关。每条单独都是分钟级修，但和 task056/057 的 wiring 在 review 上容易混在一起，所以拆出来。

## 修复项

### F1 — HF slug 404

`src/nemotron/recipes/super3/stage2_rl/data_prep.py`、RL 文档和 placeholder resolver 文档引用过 `nvidia/Nemotron-3-Super-RL-Training-Blends`，live HF 是 `nvidia/Nemotron-RL-Super-Training-Blends` (去掉 `-3-`)。旧 path 404。

修复：

- 全部 occurrences 改名。
- 加一个 regression test 验证 `huggingface_hub.dataset_info(...)` 走得通 (gate by `huggingface_hub` import 可用)。

### F2 — subset 命名 live HF 回归

Session 1 重新查验 live HF：`nvidia/Nemotron-Competitive-Programming-v1` 当前文件仍是 `data/competitive_coding_cpp.part_00.jsonl`、`data/infinibyte.part_00.jsonl` 等 dot stem。原先 `_part00` 判断是过期审计结论；本 task 保留可解析的 dot subset，并新增 comment + regression test 固化 live file stem。

修复：不替换 JSON 6 行 subset 名；增加 comment 说明 subset 必须跟 live HF file stem 对齐。同时把 `_missing_categories` 的 weight 口径留 comment，避免被误当成需要和公开 dataset weights 归一化的训练项。

### F3 — Skywork-OR1-RL-Data 缺许可证声明

`Skywork/Skywork-OR1-RL-Data` HF card 没明示 license。`src/nemotron/data_prep/utils/hf_placeholder.py` `SUPER3_TARGET_DATASETS` / `NANO3_TARGET_DATASETS` 把它当做合法源用了。

修复：

- 上游 HF license 查询需要带权限的 HF 账号；Session 1 环境没有 `HF_TOKEN`，因此代码先显式标记 legal-review posture。
- 临时方案：placeholder target config 加 `license: unknown_pending_legal_review` 字段；CI 加一个 lint 验所有 target config 必须有非空 `license`，把这个 special-case 排除直到答案。

### F4 — DAPO-Math-17k 污染审计缺位

`BytedTsinghua-SIA/DAPO-Math-17k` 没有 documented benchmark scrub。task058 的范围内只做 schema 工作 (不做实际去重)，但要：

- 在 `data_registry.yaml` 引入新字段 `contamination_against: list[str]` (M0 阶段 doc-only，标注 "未审计前不许进 M1 eval-relevant 数据流")。
- 给当前 11 个 M0 env 都补上 `contamination_against`，并把该字段写入 M0 metadata / manifest。
- 文档化字段：含义、由谁填、什么时候更新。

实际 decontamination pipeline 是另起一个 task (M1 RL 之前必须建)。

## 验收

- [x] F1：slug 全替换 + regression test 验 live HF slug。
- [x] F2：subset live file stem 回归测试 + comment，保留当前 HF 可解析的 dot subset。
- [x] F3：`license` 字段加 lint，Skywork target config 标记为 `unknown_pending_legal_review` 直到上游确认。
- [x] F4：`contamination_against` 字段 schema 落地 + 11 个 M0 env 补显式 targets。
- [x] `tests/recipes/super3/test_m0_data_env.py` 加 ≥ 4 个 case (F1 path、F2 subset name、F3 license lint、F4 schema)。

## Session 1 progress

- F1 已统一到 live `nvidia/Nemotron-RL-Super-Training-Blends` slug，覆盖 code comments、stage2 RL docs、RL user docs 和 raw blend path。
- F2 经 HF live repo 验证，dot subset stem 是当前正确形态；已补 comment 和网络可用时的 sibling regression。
- F3 已为 DAPO/Skywork placeholder target config 增加 `license` posture，并在 `HFPlaceholderResolver.create()` 前做 license lint。
- F4 已在 M0 registry、unified registry schema、M0 metadata/manifest 和测试中接入 `contamination_against`。
- Target tests：`PYTHONPATH=src pytest -q tests/recipes/super3/test_m0_data_env.py tests/recipes/super3/test_unified_data_registry.py` → `48 passed`。

## 依赖

无 — task058 独立于 task056/057，可以平行 / 先合入。

## 参考文件

- `src/nemotron/recipes/super3/stage2_rl/data_prep.py` (F1)
- `src/nemotron/recipes/super3/stage2_rl/_data_prep_base.py` (F1)
- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json` (F2)
- `src/nemotron/data_prep/utils/hf_placeholder.py` (F3, F1 间接)
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml` (F4)
- `docs/m0-dataset-expansion-plan.md` §4
