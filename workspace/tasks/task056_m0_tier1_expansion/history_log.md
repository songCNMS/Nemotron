# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 task011 implementation roadmap 派生：完整 M0 dataset 扩展工作量过大，task011 doc 把它分成 task056 (Tier-1) / task057 (Tier-2) / task058 (slug 修复) 三个独立 task。本 task 负责 Tier-1。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

第一波合入主干 (PR 待开)，wired 3 / 7 个 Tier-1 环境：

- `math_competition_numeric` ← `AI-MO/NuminaMath-CoT` (Apache-2.0, 859 K)
- `search_multihop_qa` ← `dgslibisey/MuSiQue` (CC-BY-4.0, 25 K)
- `multi_turn_tool_use` ← `NousResearch/hermes-function-calling-v1` `func_calling` config (Apache-2.0, reuses existing pin)

Wiring checklist 全部走完：data_registry + environment_registry + converter + system prompt + M1 supervision builder + M1_USE_BY_ENV。MuSiQue 复用 `normalized_exact_or_contains` (与 hotpot 同 verifier)；NuminaMath 提取 `\boxed{…}` 答案，复用同 verifier；multi-turn Hermes 复用 `transform_hermes_function_calling` 已有 trajectory 逻辑。

剩余 4 个 Tier-1 环境 (structured_outputs_json、math_formal_lean、swe_pivot_patch_supervision、tool_call_repair_negative) 都需要新 verifier 注册 + （Lean 的）合规确认 + （tool repair 的）合成 pipeline。留到 Session 2+。
