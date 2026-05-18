# task056_m0_tier1_expansion

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

`docs/m0-dataset-expansion-plan.md` 列出 7 个 Tier-1 M0 环境：math_competition_numeric、search_multihop_qa、multi_turn_tool_use、structured_outputs_json、math_formal_lean、swe_pivot_patch_supervision、tool_call_repair_negative。

第一版 PR (本 task 的 Session 1) 已经 wired 前 3 个 (NuminaMath / MuSiQue / Hermes multi-turn)，剩 4 个等本 task 继续。

## 目标

落地余下 4 个 Tier-1 环境，每个走完六点 wiring checklist:

1. `data_registry.yaml` 注册 (hf_dataset、hf_config、hf_revision、license、contamination、use_stage)
2. `environment_registry.yaml` 注册 (verifier、resources、health_check)
3. `prepare_m0_assets.py` converter + 注册到 `CONVERTERS`
4. `SYSTEM_PROMPTS` 条目 (如需)
5. `run_m0_health_baseline.py` verifier 注册 (新加 `json_structured_output_match`、`lean_proof_stub`、`patch_diff_stub`、`negative_recognition` 四个 verifier stub，oracle baseline 至少返回 1.0)
6. `prepare_m1_agentic_sft.py` supervision builder + `M1_USE_BY_ENV` 条目

## 子任务

### A. structured_outputs_json

- HF: `nvidia/Nemotron-Instruction-Following-Chat-v1` subset `structured_outputs` (CC-BY-4.0, 4 969 行)。
- 数据形态需读 HF card 确认；预期是 prompt + 期望 JSON 输出。
- Verifier: `json_structured_output_match` — 至少校验 candidate 解析为合法 JSON；Phase-2 再加 schema match。
- M1 supervision: `assistant_for_structured_output(record)` 返回 `{"role":"assistant","content": <expected JSON string>}`。

### B. math_formal_lean

- HF: `nvidia/Nemotron-Math-Proofs-v1` Lean split (CC-BY-SA-4.0 ⚠ 需要在 derived artifact 中标注 share-alike)。
- 数据形态：theorem statement + Lean proof。
- Verifier: `lean_proof_stub` — M0 阶段只校验非空 + 包含 `theorem`/`lemma`/`:=`；真 Lean 检查留给 task017 (sandbox)。
- 警告: share-alike posture pending — 需要 product/legal 拍板再合入主干 train 数据。可以先把环境注册起来，把数据下载/converter 上 PR，但默认 `use_stage` 不包含 M1 SFT v0 直到合规确认。

### C. swe_pivot_patch_supervision

- HF: `nvidia/Nemotron-SWE-v1` (CC-BY-4.0, 51 029 行, subset `r2e_gym`)。
- 数据形态：repo + base_commit + problem_statement + gold_patch。
- Verifier: `patch_diff_stub` — M0 阶段只校验 candidate 包含 `diff --git` + 非空；真 patch apply 留给 task017 SWE2。
- 注意 SWE-Bench Verified 污染风险 — 在 `data_registry.yaml` 加 `contamination_against: ["SWE-Bench_Verified"]` 字段 (新 schema 项)。
- M1 supervision: `assistant_for_swe_pivot(record)` 返回 `{"role":"assistant","content": <gold_patch>}`。

### D. tool_call_repair_negative

- 源: 从 `func_calling_singleturn` 已有数据合成。两种 negative_kind:
  - `malformed_tool_call`: 截断 JSON、缺逗号、错 key、值类型错位。
  - `hallucinated_tool_output`: tool 角色 turn 替换为 schema-相邻但语义错误的 JSON。
- 每条 negative 行带 `metadata.negative_kind` 和 `metadata.repair_target` (正确的 tool call / 正确的 final answer)。
- Verifier: `negative_recognition` — 模型输出应识别错误并复述正确 tool call。M0 阶段 oracle = `metadata.repair_target`，模型输出至少包含 repair_target 关键字段。
- M1 supervision: `assistant_for_tool_repair(record)` 返回 supervision = "I notice the previous tool call has X error; the correct call is: …" + 正确 tool_calls。

## 验收

- [ ] 上面 A/B/C/D 四个 env 都完成 6 点 wiring。
- [ ] 新加 4 个 verifier stub，oracle baseline 全部通过 (`run_m0_health_baseline.py --skip-code-execution`)。
- [ ] `tests/recipes/super3/test_m0_data_env.py` + `test_m0_health_baseline.py` 新增 ≥ 8 个 case (每 env converter + verifier)。
- [ ] `tests/recipes/super3/test_m1_agentic_sft.py` 新增 ≥ 4 个 case 覆盖 M1 supervision routing。
- [ ] `docs/m0-dataset-expansion-plan.md` §3 Tier-1 表里把这 4 行 "Wired in this PR" 改 ✓。
- [ ] `share-alike posture` open question (math_formal_lean) 有定论：要么 product/legal 拍板可用，要么把 use_stage 限制为 `["M0 data_env_foundation"]`，不进 M1 SFT v0。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py` — 加 converter
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml` — 加 spec
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml` — 加 env
- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py` — 加 verifier
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` — 加 supervision builder + `M1_USE_BY_ENV`
- `docs/m0-dataset-expansion-plan.md` §5 wiring rules
- 上一轮 PR (`task056_m0_tier1_expansion_partial`)：NuminaMath + MuSiQue + Hermes multi-turn 的 wiring 已合入主干，可作 pattern 参考。
