# history_log

<!-- METADATA:SESSION=2 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，PR #11 + PR #12 合并后按 REVIEW_v0.md 推荐顺序继续。
- 范围：把 P1 剩余三条 (#4 empty-content guard / #11 search supervision template / #14 tool role loss_mask end-to-end test) 一并收掉。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

完成 P1 三条 + 5 个回归测试。

分支 `intern_nemontron_review_cc/task007_m1_p1_remaining_fixes`，PR <https://github.com/songCNMS/Nemotron/pull/13>，CLEAN/MERGEABLE。

修复要点：
1. **#4** `_ensure_assistant_supervision_non_empty` 在 `convert_m0_record` 入口处对所有 env raise ValueError；移除 tool_calling 专属的 soft warning，统一走 raise 路径。
2. **#11** `assistant_for_search` 改成 grounded template "Based on the retrieved passages ([N] Title), the answer is …"；空 expected_answer 时返回 content="" 让 #4 守卫拦截。
3. **#14** 两个测试合拢：结构性 `test_tool_role_supervision_survives_to_chat_template_input` + cosmos_xenna-gated end-to-end `test_tokenize_chunks_with_mask_pins_tool_role_to_zero`，端到端跑 `_tokenize_chunks_with_mask` 断言 tool 段 loss_mask=0。

测试：`PYTHONPATH=src pytest tests/recipes/super3/ -q` → 56 passed + 1 skipped（task006 基线 52 + 新 5 - 1 cosmos_xenna 跳过）。

REVIEW_v0.md v5：#4 / #11 / #14 全部标 ✓ Fixed。整体进度 7 fixed / 1 partial / 11 open / 2 tracked。

## Session 2 - 2026-05-17 - intern_nemontron_review_cc

PR #13 已 squash-merge 为 `745d634`，远程 task007 分支删除。task007 结题。

剩余 P2 由 task008 承接：#7 difficulty curriculum + #10 m1_use 名实不符。（#5/#6 在 task005 由 intern_nemontron_code_reading 推进。）
