# task003_m1_agentic_sft_v0_review

<!-- METADATA:STATUS=Done,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

M0 review (task001 / task002) 完成后，主干合并了 M1 Agentic SFT v0 三个 PR (#3 / #6 / #7) 由 `intern_nemontron_code_reading` 提交：

- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`（M0 JSONL → OpenAI chat 转换）
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py`（生成训练 manifest + run script）
- `src/nemotron/recipes/super3/stage1_sft/config/{m1_agentic_smoke,m1_agentic_train,data_prep/agentic_v0}.yaml`
- `src/nemotron/recipes/super3/smoke_runtime.py` + `tiny_model.py`/`test_train.py` 改造
- 顺带的 M0 修复 (`Fix M0 subset overwrite and M1 tool SFT conversion`, commit 126222e)

review 对照 `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` 的 §3 / §4 / §5.1 / §6 / §8 (M1 / Agentic SFT v0 章节)。

## 目标

把发现整理成一份 review 报告 markdown，落地到代码侧（与被 review 的代码同目录），通过 PR 提交。本任务**仅交付 findings 文档**，不直接修复——修复留给 `intern_nemontron_code_reading` 或后续 task。

## 交付物

- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md`：24 条 findings，按 P0/P1/P2/P3 分级
- 一个 PR，base=main，从 `intern_nemontron_review_cc/task003_m1_agentic_sft_v0_review` 推上去

## 验收

- [ ] REVIEW_v0.md 至少覆盖：cross-intern repo dir 泄漏 / GBS×DP 不匹配 / GSM8K `####` 泄漏 / SWE·terminal·structured output 缺失 / negative 例缺失 / chat template TODO / m1_use 名实不符 / tool role loss mask 待验
- [ ] PR 描述里列出 P0 两条
- [ ] 不修改任何代码 / 不动测试

## 参考

- 改动起点 commit: `47cb0ee`（task001 合并）
- 主要 review 对象 commits: `859fde9`, `126222e`, `58c1783`, `b4a0d46`
- plan 文档: `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md`
