# task058_production_dataset_slug_fixes

<!-- METADATA:STATUS=Todo,ASSIGNEE= -->

## 背景

`docs/m0-dataset-expansion-plan.md` §4 列出 4 个跟 M0 扩展独立的生产线 bug，都跟数据集 slug / 字段命名 / 污染审计有关。每条单独都是分钟级修，但和 task056/057 的 wiring 在 review 上容易混在一起，所以拆出来。

## 修复项

### F1 — HF slug 404

`src/nemotron/recipes/super3/stage2_rl/data_prep.py` 与 `src/nemotron/recipes/super3/stage2_rl/_data_prep_base.py` 引用 `nvidia/Nemotron-3-Super-RL-Training-Blends`，live HF 是 `nvidia/Nemotron-RL-Super-Training-Blends` (去掉 `-3-`)。当前 path 404。

修复：

- 全部 occurrences 改名。
- 加一个 regression test 验证 `huggingface_hub.dataset_info(...)` 走得通 (gate by `huggingface_hub` import 可用)。

### F2 — subset 命名 dot vs underscore

`src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json` 用 `competitive_coding_cpp.part_00` (dot)，HF repo 是 `_part00` (underscore，无 dot)。Loader 当前失败。

修复：JSON 6 行 subset 名替换。同时把 `_missing_categories` 的 weight 校验 (12 个 entry 合计应该接近 100 - 已落地的 weight 合计) 留 comment。

### F3 — Skywork-OR1-RL-Data 缺许可证声明

`Skywork/Skywork-OR1-RL-Data` HF card 没明示 license。`src/nemotron/data_prep/utils/hf_placeholder.py` `SUPER3_TARGET_DATASETS` / `NANO3_TARGET_DATASETS` 把它当做合法源用了。

修复：

- 上游 HF issue 询问 license (链接到 task task_knowledge.md)。
- 临时方案：注册表里加 `license: unknown_pending_legal_review` 字段；CI 加一个 lint 验所有 registry entry 必须有非空 `license`，把这个 special-case 排除直到答案。

### F4 — DAPO-Math-17k 污染审计缺位

`BytedTsinghua-SIA/DAPO-Math-17k` 没有 documented benchmark scrub。task058 的范围内只做 schema 工作 (不做实际去重)，但要：

- 在 `data_registry.yaml` 引入新字段 `contamination_against: list[str]` (M0 阶段 doc-only，标注 "未审计前不许进 M1 eval-relevant 数据流")。
- 给现有 4 个 M0 env 都补上 `contamination_against` (空 list 默认值)。
- 文档化字段：含义、由谁填、什么时候更新。

实际 decontamination pipeline 是另起一个 task (M1 RL 之前必须建)。

## 验收

- [ ] F1：slug 全替换 + regression test (`gh api repos/songCNMS/Nemotron/contents/...` 验 path)。
- [ ] F2：subset 命名修 + 加 comment 说 dot vs underscore 是 HF 那边历史遗留。
- [ ] F3：`license` 字段加 lint，Skywork registry entry 标记为 `unknown_pending_legal_review` 直到上游确认。
- [ ] F4：`contamination_against` 字段 schema 落地 + 4 个 M0 env 补 default。
- [ ] `tests/recipes/super3/test_m0_data_env.py` 加 ≥ 4 个 case (F1 path、F2 subset name、F3 license lint、F4 schema)。

## 依赖

无 — task058 独立于 task056/057，可以平行 / 先合入。

## 参考文件

- `src/nemotron/recipes/super3/stage2_rl/data_prep.py` (F1)
- `src/nemotron/recipes/super3/stage2_rl/_data_prep_base.py` (F1)
- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json` (F2)
- `src/nemotron/data_prep/utils/hf_placeholder.py` (F3, F1 间接)
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml` (F4)
- `docs/m0-dataset-expansion-plan.md` §4
