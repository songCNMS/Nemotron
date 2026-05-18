# history_log

<!-- METADATA:SESSION=0 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 task011 implementation roadmap 派生：完整 M0 dataset 扩展工作量过大，task011 doc 把它分成 task056 (Tier-1) / task057 (Tier-2) / task058 (slug 修复) 三个独立 task。本 task 负责 Tier-1。
- 同 session 起手做过一次 implementation attempt (NuminaMath + MuSiQue + 多轮 Hermes 三个环境)，但 push 时碰到 `task005_m1_sft_v0_scope_expansion` 在 main 上同时合入 4 个环境 (terminal / SWE pivot / tool-call repair negative / structured outputs)，conflict 与 force-push 限制让 review surface 不干净，因此 abandon code 改回 doc-only PR。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

完成 doc-only PR：`docs/m0-dataset-expansion-plan.md` + 3 个 task scaffold (task056 / task057 / task058) + README 更新映射现状。本 PR 不动任何代码。

更新点对齐 main `3e37616`：4 / 8 个 Tier-1 环境已经在 main，剩 4 个 (NuminaMath / MuSiQue / 多轮 Hermes / Lean) 由本 task assign 后做 implementation。

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

接 task011 roadmap，把剩余 Tier-1 envs 中 3 个有清洁公共数据的全部落地：

- `math_competition_numeric` ← `AI-MO/NuminaMath-CoT` (Apache-2.0)。新加 converter `transform_numinamath_competition` + helper `extract_boxed_answer`；reuse `assistant_for_reasoning` builder。
- `search_multihop_qa` ← `dgslibisey/MuSiQue` (CC-BY-4.0)。新加 converter `transform_musique_search`；扩展 `_supporting_fact_titles` 让它兼容 MuSiQue 的 flat list 和 HotpotQA 的 mapping 两种 shape；reuse `assistant_for_search` 的 grounded template。
- `multi_turn_tool_use` ← Hermes `func_calling` config (Apache-2.0)。不需要新 converter — `transform_hermes_function_calling` 已经从 task002 起支持多轮 trajectory；新加 registry / env_registry / `_TOOL_CALLING_ENVIRONMENTS` frozenset 把它跟 `general_tool_calling` 一起 route。

每个 env 走完 7 点 wiring checklist (含 `docs/m0-dataset-expansion-plan.md` §5.7 加的 round-trip smoke 步骤 — 在 sandbox 因为 pyarrow 缺，run-time gate 留给 NemTron。)

剩 `math_formal_lean` (CC-BY-SA-4.0) 等 §6 share-alike posture 拍板再做 Session 3。

测试：sandbox 没装 pyarrow / jinja2，M1 test 文件 collection 失败 (pre-existing — `run_m1_sft_roundtrip_smoke` 模块顶层 import pyarrow)。M0 test 套件 43 passed (38 前 + 5 新)。M1 routing 用 stub pyarrow 手工验证全部通过 (NuminaMath -> reasoning builder、MuSiQue -> grounded template、multi-turn Hermes -> trajectory builder)。完整 pytest 等 NemTron 跑。

## Session 3 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #25 (`4e95552`) + 配套 doc refresh PR #26 (`910eb57`) 都已 squash-merge 进 main。intern status 回 Idle (Session 14)，task056 整体保留 InProgress —— Session 4 (`math_formal_lean`) 等 §6 share-alike posture 拍板再启动；那时再把这一行勾掉、task056 整体 Done。

## Session 4 - 2026-05-18 - intern_nemontron_review_cc

实现 `math_formal_lean` 的 **code path**（不含 data_registry 行 — 那条留
给 share-alike 决议后的一次性 wiring PR）。设计要点：

- **Source-agnostic transformer**：`transform_lean_proof_stub(row, spec)`
  从 `spec['fields']` 拿列名 (`statement` / `proof` / `theorem_name` /
  `language` 可独立 remap)，所以将来不管选 Nemotron-Math-Proofs-v1 /
  mathlib4 extraction / LeanDojo-Bench / Lean-Workbook 哪个 source，
  Python 代码都不动 — 只改 data_registry 行的 `fields` map。
- **M0-side verifier**：`lean_proof_stub` 只校验非空 strip 之后还在。
  Real Lean compiler verification (跑 mathlib4 + `#print axioms`) 留
  task017 / task049 territory — 需要 sandbox container 带 Lean toolchain。
- **Telemetry**: `nonempty_proof` (bool)、`proof_length` (numeric)、
  `language` (str) — 走 task021 Session 1 那套 per-verifier 自动 aggregator
  (bool → true_count/false_count；numeric → min/max/mean；str → distinct_count)。
- **SYSTEM_PROMPTS**：新增 `math_formal_lean` 条目，明确要求"只返回
  proof code，不要 prose"；User prompt 里也带语言 (`Prove in lean4...`)
  让模型知道 dialect。
- **M1 SFT supervision**：`assistant_for_lean_proof(record)` 优先
  `expected_answer`，fallback 到 `extra_env_info.reference_proof`。
  注册进 `ASSISTANT_BUILDERS["math_formal_lean"]`。`M1_USE_BY_ENV` 加
  `["formal-proof syntax", "Lean tactic-style proof"]`。
- **environment_registry.yaml** 加 `math_formal_lean` row 含
  `verifier: lean_proof_stub`、telemetry list、`min_rows_per_split: 25`、
  required_fields 含 `extra_env_info.{statement_only,reference_proof}`。
  Comment 显式说明 data_registry source 待 §6 决议。

文档：
- `docs/m0-dataset-expansion-plan.md` §3 Tier-1 表 `math_formal_lean` 那
  行从 "✗ Session 2, blocked" 改成 "✓ code path landed; data_registry
  row 待决议"。
- §6 Q1 share-alike posture 加 5 个候选 source 比较表 (mathlib4 / LeanDojo /
  MiniF2F / Nemotron-Math-Proofs / Lean-Workbook) + license 风险排名。
- §7 delivered/remaining 表 `math_formal_lean` 改 ✓ (code path)，data
  row 注明待 §6 决议。

测试 (`tests/recipes/super3/test_math_formal_lean.py`, 13 cases)：
- transformer: default columns / 字段 remap / 拒空 statement / language
  默认 lean4 / 注册进 CONVERTERS (5)
- M0 verifier: 非空 → 1.0 / 空 / None / whitespace → 0.0 / language
  字段保留 (3)
- environment_registry: 含 math_formal_lean row + telemetry contract (1)
- M1 SFT supervision: ASSISTANT_BUILDERS 注册 / expected_answer 优先 /
  extra_env_info.reference_proof fallback / M1_USE_BY_ENV 有 Lean tag (3)
- 跨 registry: task030 Session 1 unified index validation 加新 env_registry
  row 后仍 clean (1)

测试基线 148 → 161 passed + 2 skipped。`test_m1_agentic_sft.py` 在 sandbox
仍 pyarrow collect-error pre-existing，跟本 PR 无关 (M1 routing 通过新
test_math_formal_lean.py 直接验证不走那条 module-level pyarrow import 路径)。

task056 整 task 仍 InProgress：唯一剩的是 data_registry 行 — 等 product/
legal review。决议后的 wiring 是一次性 PR (任一候选 source 都 ≤ 50 行 yaml)。
