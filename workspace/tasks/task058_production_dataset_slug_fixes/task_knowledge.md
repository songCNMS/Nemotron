# task_knowledge

<!-- METADATA:SESSION=0 -->

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

### Slug 404 检测策略

修完 F1 后，加一个 lint test 用 `requests.head(f"https://huggingface.co/datasets/{slug}")` 校验所有 registry entry 的 `hf_dataset` 都返回 200。CI 只在 daily run 跑 (避免 PR 卡 HF down)。

如果未来发生类似 slug rename，lint 会在 daily run 报出来 — 比等部署失败再回查快多了。
