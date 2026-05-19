# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### `contamination_against` 字段的隐含约定

引入新字段 `contamination_against: list[str]` 时要约定：

- **空 list `[]`** = 已审计，已知无污染。
- **null / 字段缺失** = 未审计，禁止进 M1 eval-relevant 数据流。
- **非空 list** = 已知与哪些 eval 重叠；进数据流前必须先做去重 pass。

后续 contamination pipeline (M1 task020 infra minimum 范围) 会消费这个字段决定是否需要 dedup。

Session 1 已把当前 11 个 M0 dataset row 全部补上 `contamination_against`，并让 M0 metadata / manifest 透传该字段。后续新增 M0 row 时字段缺失会被 `validate_registries()` 拒绝。

### Slug 404 检测策略

修完 F1 后，加一个 lint test 用 `requests.head(f"https://huggingface.co/datasets/{slug}")` 校验所有 registry entry 的 `hf_dataset` 都返回 200。CI 只在 daily run 跑 (避免 PR 卡 HF down)。

如果未来发生类似 slug rename，lint 会在 daily run 报出来 — 比等部署失败再回查快多了。

### Competitive Programming subset live stem

2026-05-19 用 Hugging Face live repo 验证：`nvidia/Nemotron-Competitive-Programming-v1@d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` 的公开文件名是 `data/competitive_coding_cpp.part_00.jsonl`、`data/competitive_coding_python.part_00.jsonl`、`data/infinibyte.part_00.jsonl` 这类 dot stem。不要把 `data_blend_raw.json` 的 subset 改成 `_part00`，否则 discovery 找不到文件。

### Skywork placeholder license posture

2026-05-19 查 `Skywork/Skywork-OR1-RL-Data@1cdedc52e0e2db85fdf252f9be682e63a5a38c33`，HF card metadata 没有 license 字段。当前代码只能标 `unknown_pending_legal_review`，并用 license lint 防止 future target config 漏填；创建上游 discussion 需要带权限 HF 账号，本环境没有 `HF_TOKEN`。
