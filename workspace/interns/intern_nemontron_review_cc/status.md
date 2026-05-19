# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 58 |

刚做完：task020 Session 1 — M1 eval basket full extension (PR #72 /
deec7b7, merged 2026-05-19)。把 v0 8 benchmark 扩到 plan §5.7 全 19
个。新 file `m1_eval_basket/m1_eval_full_basket_registry.yaml` 11 rows
(HMMT / HLE / SciCode / TerminalBench / SWE-Bench Verified / AA-LCR /
MMLU-ProX / WMT24++ / BFCL / MCP-Mark / Tool Decathlon) **复用 task019
加的 `eval_basket_registry` schema kind — KNOWN_KINDS 保持 7**。
`unified_index.yaml` 加 `m1_eval_full_basket` entry，
`stage3_eval/config/m1_full_basket.yaml` 选 19 个 task (v0 + full)。
14 个新 pytest case；sandbox 测试基线 357 → 371 passed + 7 skipped。

task020 整 task 仍 InProgress：Sessions 2-4 (promotion gate weighted-parity
logic + cluster verify + gap analysis) 待开；Session 2 sandbox-runnable
(weighted-mean Super3 parity + per-category regression > 1-2% +
rollback rule on safety / SWE / tool / IF per plan §5.7)，Session 3
需 cluster + 真 SFT checkpoint。

**M1 eval basket 全 19 benchmark 数据层全落地**:
- task019 ✓ Session 1 (8 v0 + schema kind + regression_report.py)
- task020 ✓ Session 1 (11 full extension + combined config)
- 接下来 promotion gate logic (task020 Session 2) 是 sandbox-runnable
  的下一步候选

下一候选 (sandbox-runnable):
- **task020 Session 2** — promotion gate logic，最 productive 因为
  task019/020 数据层刚铺好
- task014 / 016 / 017 / 018 各自 Session 2 (converter 单测，sandbox 部分)
- 之前 task 的 Session 2+ — 大都需 cluster
