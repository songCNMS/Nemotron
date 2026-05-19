# task056_m0_tier1_expansion

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 2 LANDED: PR #50 / 2951cac on 2026-05-18 — code path only; data_registry row待 §6 share-alike 决议 -->

## 背景

`docs/m0-dataset-expansion-plan.md` 列出 8 个 Tier-1 M0 环境。`task005_m1_sft_v0_scope_expansion` 已合入 4 个 (terminal_basic_shell、swe_pivot_patch_supervision、tool_call_repair_negative、structured_outputs_json)；本 task Session 1 又合入 3 个 (math_competition_numeric、search_multihop_qa、multi_turn_tool_use)。剩 **1 个** Tier-1 环境等本 task Session 2 解锁：

- ~~`math_competition_numeric` ← `AI-MO/NuminaMath-CoT` (Apache-2.0, 859 608 行)~~ — Session 1 完成
- ~~`search_multihop_qa` ← `dgslibisey/MuSiQue` (CC-BY-4.0, 24 814 行)~~ — Session 1 完成
- ~~`multi_turn_tool_use` ← `NousResearch/hermes-function-calling-v1` `func_calling` config (Apache-2.0)~~ — Session 1 完成
- `math_formal_lean` — Session 2 lands the **code path** (transform / verifier / env_registry / M1 SFT builder); `data_registry.yaml` row 暂留 — 待 §6 share-alike 决议从下面几个候选选一个 source (Nemotron-Math-Proofs-v1 / mathlib4 extraction / LeanDojo-Bench / Lean-Workbook)

## 目标

每个环境走完六点 wiring checklist:

1. `data_registry.yaml` 注册 (hf_dataset、hf_config、hf_revision、license、contamination、use_stage)
2. `environment_registry.yaml` 注册 (verifier、resources、health_check)
3. `prepare_m0_assets.py` converter + 注册到 `CONVERTERS`
4. `SYSTEM_PROMPTS` 条目 (如需)
5. `run_m0_health_baseline.py` verifier 注册 (math_formal_lean 需要新 `lean_proof_stub`；前 3 个复用现有 verifier)
6. `prepare_m1_agentic_sft.py` supervision builder + `M1_USE_BY_ENV` 条目

## 子任务

### A. math_competition_numeric

- HF: `AI-MO/NuminaMath-CoT` (Apache-2.0, 859 K)。CoT 解题，最后答案在 `\boxed{...}` 里。
- Converter 关键点: 抽 `solution` 最后一个 `\boxed{}` 的内容当 `expected_answer`；cn_k12 等没有 boxed 的行 fallback 到 solution 尾部 token。
- Verifier: `normalized_exact_or_contains` (math-judge 真正的版本在 plan §5.3 的 `math_with_judge`，M0 阶段够用)。
- M1 supervision: 复用 `assistant_for_reasoning` (它已经优先 `expected_answer`，刚好兼容)。
- 注意污染: NuminaMath 包含 MATH / AIME / AMC / HMMT 源题，eval 时必须扣掉。

### B. search_multihop_qa

- HF: `dgslibisey/MuSiQue` (CC-BY-4.0, 25 K)。MuSiQue-Ans 配置 (2-4 hops)。
- Converter 关键点: 每个 paragraph 是 `{idx, title, paragraph_text, is_supporting}` (与 HotpotQA 的 `{title, sentences: [...]}` 结构不同); 把 `is_supporting=True` 的 title 抽进 `supporting_titles` flat list。
- Verifier: 复用 hotpot 的 `normalized_exact_or_contains`。注意保留 `answer_aliases` 字段给后续更宽容的 verifier。
- M1 supervision: 复用 `assistant_for_search`，并扩展 `_supporting_fact_titles` 同时认 MuSiQue 的 flat list 与 HotpotQA 的 mapping 形态。
- 注意 MuSiQue 经常用作 eval，决定 train role 时跟 HotpotQA 一起做 split (一个用 train，一个用 eval)。

### C. multi_turn_tool_use

- HF: `NousResearch/hermes-function-calling-v1` `func_calling` config (Apache-2.0)。同源不同 config — singleturn 已在 `general_tool_calling`。
- Converter: 复用 `transform_hermes_function_calling` (task002 之后已支持多轮 trajectory)。**不需要新 converter**，只新加 registry / env spec / max_turns=10。
- M1 supervision: 复用 `trajectory_for_tool_calling`；需要把 `_TOOL_CALLING_ENVIRONMENTS` 改成 frozenset 包含 `multi_turn_tool_use`。
- 注意 NeMo-Gym 那侧 `multi_turn_tool_use` env 的 `max_turns=10` 配置需要单独修。

### D. math_formal_lean

- HF: `nvidia/Nemotron-Math-Proofs-v1` Lean split (**CC-BY-SA-4.0 ⚠** — share-alike，需要 product/legal 拍板再合入主干 train 数据流)。
- 数据形态: theorem statement + Lean proof。
- Verifier: 新加 `lean_proof_stub` — M0 阶段只校验非空 + 包含 `theorem`/`lemma`/`:=`；真 Lean 检查留给 task017 (sandbox)。
- 警告: share-alike posture pending。可以先把环境注册起来 + converter 上 PR；默认 `use_stage` 不包含 M1 SFT v0 直到合规确认。
- M1 supervision: 新加 `assistant_for_lean_proof(record)` 返回 `{"role":"assistant","content": <gold_proof>}`。

## 验收

- [ ] 4 个 env 全部完成 6 点 wiring。
- [ ] 新加 1 个 verifier stub (`lean_proof_stub`)，前 3 个复用现有 verifier。
- [ ] `tests/recipes/super3/test_m0_data_env.py` + `test_m0_health_baseline.py` 新增 ≥ 8 个 case (每 env converter + verifier)。
- [ ] `tests/recipes/super3/test_m1_agentic_sft.py` 新增 ≥ 4 个 case 覆盖 M1 supervision routing。
- [ ] `docs/m0-dataset-expansion-plan.md` §3 Tier-1 表里把这 4 行 "Wired in this PR" 改 ✓。
- [ ] `share-alike posture` open question (math_formal_lean) 有定论：要么 product/legal 拍板可用，要么把 use_stage 限制为 `["M0 data_env_foundation"]`，不进 M1 SFT v0。

## 依赖

无 — 4 个环境互相独立，可以平行分多个子 PR 或一次性合入。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py` — 加 converter
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml` — 加 spec
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml` — 加 env
- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py` — 加 verifier
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` — 加 supervision builder + `M1_USE_BY_ENV`
- `docs/m0-dataset-expansion-plan.md` §3 Tier-1 + §5 wiring rules + §6 open questions
- task005 PR 系列 (commit `e2d0bcd` + `3e37616`) — 4 个 task005 env 是直接的 pattern 参考
