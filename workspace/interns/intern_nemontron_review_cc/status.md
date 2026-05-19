# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task020_m1_eval_full_basket -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task020_m1_eval_full_basket |
| PR | pending push |
| Session | 57 |

正在做：task020 Session 1 — M1 eval basket full extension。把 v0 8
benchmark 扩到 plan §5.7 全 19 个。新 file
`m1_eval_basket/m1_eval_full_basket_registry.yaml` 11 rows (HMMT /
HLE / SciCode / TerminalBench / SWE-Bench Verified / AA-LCR /
MMLU-ProX / WMT24++ / BFCL / MCP-Mark / Tool Decathlon) **复用 task019
加的 `eval_basket_registry` schema kind — 不动 KNOWN_KINDS**。
`unified_index.yaml` 加 `m1_eval_full_basket` entry，
`stage3_eval/config/m1_full_basket.yaml` 选 19 个 task (v0 + full)。
14 个新 pytest case；sandbox 测试基线 357 → 371 passed + 7 skipped。

task020 整 task 仍 InProgress：Sessions 2-4 (promotion gate weighted-parity
logic + cluster verify + gap analysis) 待开；Session 2 sandbox-runnable，
Session 3 需 cluster。
