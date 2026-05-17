# history_log

<!-- METADATA:SESSION=2 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，把 M1 Agentic SFT v0 review 的 24 条 findings 落成 markdown 报告并通过 PR 提交。
- 仅交付 findings 文档，不改代码。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

写入 `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md`（235 行，24 条 findings, P0/P1/P2/P3 分级）。

分支 `intern_nemontron_review_cc/task003_m1_agentic_sft_v0_review`，PR <https://github.com/songCNMS/Nemotron/pull/9>，CLEAN/MERGEABLE。

文档落点选 `milestones/m1_agentic_sft/REVIEW_v0.md` 而不是 `docs/reviews/...` 是想让被 review 的代码作者打开模块目录时就能看到。

## Session 2 - 2026-05-17 - intern_nemontron_review_cc

`intern_nemontron_code_reading` 在 PR #10 (`589368b`) 和 PR #8 (`14bbbac`) 之后合了 M1 correctness 修复 + Qwen local SFT entry。

把 PR #9 分支 rebase 到 main，逐条复核 24 条 finding：
- **1 fixed** (#1)
- **4 partial** (#4, #14, #16, #23)
- **17 still open** (含 P0 #2, P1 #3, #11)
- **2 tracked** (#5, #6 → task005)

并发现 3 条新问题：
- N1：PR #8 `qwen_local_train.py:25` 把 lei.song 路径带回来（v1 #16 已清的退步）
- N2：PR #10 把 `m1_agentic_smoke.yaml` 的 `pretrained_checkpoint` 改成强制 env var，但 smoke `finetune=false` 路径下 `train.py:367` 无条件 log 触发 MissingMandatoryValue，README 文档的 offline smoke 流被打断
- N3：`trust_remote_code: true` 进 hotpotqa 注册表却没在 M0 README/SECURITY 标注

REVIEW_v0.md 从 v1 单层结构 (Priority summary + 24 findings) 重排为：v2 status summary 表格 + 新发现 N1–N3 + T1（信息项）+ 修订建议 + v1 原文（保留作 traceability）。

`PYTHONPATH=src pytest tests/recipes/super3/ -q` → 45 passed (v1 基线 32 → PR #10 加 13)。

分支 force-with-lease 推送（task branch，非 main）。PR #9 body 走 REST 更新。

PR #9 由主管同意 squash-merge 为 `45a470d`，远程 task003 分支删除；worktree 切回 main 同步完成。状态切 Idle。

task003 结题：REVIEW_v0.md（v1 + v2）已落 main，task005 已由 intern_nemontron_code_reading 承接覆盖面扩展（#5/#6）。剩余 17 条 open + 3 条 v2 新发现都已在 PR #9 body 与 REVIEW_v0.md 写明 follow-up 建议。
