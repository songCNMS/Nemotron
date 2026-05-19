# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 38 |

最近：task056 Session 2 (PR #50 `2951cac`) 已 squash-merge 进 main —
`math_formal_lean` 的 source-agnostic code path 落地（transformer +
verifier + env_registry + M1 SFT builder + 5 候选 source 对比表）。
data_registry 行待 §6 share-alike 决议。13 个新 pytest case。

**合并后修复**: task058 (production_dataset_slug_fixes) 并发 merge 进
main 同步加了 `contamination_against` 必填字段 + 加了 hf_placeholder
license-lint 测试，导致两个 sandbox regression:
1. 我的 Lean 测试 `_spec()` 缺 `contamination_against` → 3 tests 失败
2. test_m0_data_env.py 顶层 import `hf_placeholder` 拽进 pydantic →
   整文件 collection 失败 (sandbox 没 pydantic)

修复 (本 closeout PR 一并合)：
- test_math_formal_lean `_spec()` helper 加 `contamination_against: ["minif2f", "mathlib4_test"]`
- test_m0_data_env hf_placeholder import 改为 lazy 进两个用到它的 test 函数内 + 加 `pytest.importorskip("pydantic")` 让 sandbox 跳但 NemTron 跑

测试基线 sandbox: **164 passed + 6 skipped** (4 sandbox-gated: 2 pydantic +
2 网络相关; 2 torch-gated 老的). task058 + task056 Session 2 一起算
~24 个新 case 进 main。

task056 整 task 仍 InProgress：data_registry.yaml 待 §6 决议。

下一个候选 (sandbox-runnable + leverage):
- task021 Session 3 — sandbox container 构建脚本 (code-exec / Lean / terminal Dockerfile)
- task030 Session 2 — eval basket registry kind (block on task019 / task020)
- task019 / task020 — M1 eval basket (本身设计 sandbox-runnable，但 acceptance 要真 RLVR checkpoint)
- task013 / 014 / 016 / 017 / 018 各自的 Session 2+ — 大都需要 cluster / nvcr container
