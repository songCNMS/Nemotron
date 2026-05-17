# task006_m1_p1_fixes

<!-- METADATA:STATUS=Open,ASSIGNEE= -->

## 背景

PR #11 (task004) 合并主干后，P0 两条已 ✓ Fixed。`src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md` 仍剩 4 条 P1 / 部分 P1：

- **#3 GSM8K `####` marker leaks into reasoning SFT target** — `prepare_m1_agentic_sft.assistant_for_reasoning` 优先取 `extra_env_info.reference_solution`，那是 M0 直接 passthrough 的 GSM8K 原 `answer` 字段（带 `#### N` 验证器标记）。SFT 目标因此把 `####` 当 verbatim 文本训进模型；同一 marker 会泄漏到非 GSM8K 题。
- **N1 `qwen_local_train.py:25 DEFAULT_QWEN_MODEL`** — PR #8 引入的 `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507` 硬编码路径。其他 intern 跑这个 entry 不设 env var 会在 HF auto-bridge 内部抛 "directory not found"。同时 `import_qwen3_4b_local_to_megatron.py` 是显式 CLI flag 入口，不受影响。

P1 还有 #4 (empty-content guard 仅 tool_calling) / #11 (search bare answer) / #14 (tool role loss_mask 端到端验证) — 这三条修复面更大、各自牵涉 SFT supervision 设计，留给后续任务。

## 目标

按 REVIEW_v0.md 推荐顺序收 P1 中"一行修就能解"的两条（#3 + N1），并加回归测试。其余 P1 三条留 follow-up。

## 验收

- [ ] `prepare_m1_agentic_sft.assistant_for_reasoning` 改成：优先用 `expected_answer`；若 `reference_solution` 非空就先 `re.sub(r"####\s*", "", reference_solution)` 再用，确保 `####` 永远不进 SFT target。
- [ ] `qwen_local_train.py` 的 `DEFAULT_QWEN_MODEL` 改为 `None`；解析时若 env var 与 flag 都未设则显式 `raise ValueError`，错误信息提示 `--qwen-model` 或 `SUPER3_M1_QWEN_HF_MODEL`。
- [ ] 新增 2 个 pytest case：
  - reasoning supervision 输入带 `#### 24` 的 reference_solution，断言 SFT assistant content 不含 `####`
  - qwen_local_train 在 env var 未设时 raise（而非 silent 走 lei.song 路径）
- [ ] REVIEW_v0.md 加 v4 行，把 #3 / N1 标 ✓ Fixed by task006 PR。
- [ ] `PYTHONPATH=src pytest tests/recipes/super3/` 全绿。
