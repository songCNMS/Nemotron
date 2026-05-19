# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task056_m0_tier1_expansion -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task056_m0_tier1_expansion |
| PR | pending push |
| Session | 37 |

正在做：task056 Session 2 — `math_formal_lean` 的 code path（不含
data_registry 行）。Source-agnostic transformer (`transform_lean_proof_stub`)
从 `spec['fields']` 拿列名，将来不管选哪个 source (Nemotron-Math-Proofs /
mathlib4 extraction / LeanDojo-Bench / Lean-Workbook) Python 都不动。
新 verifier `lean_proof_stub` (M0 只校验非空；real Lean check task017/049
territory)。`environment_registry.yaml` 加 row + telemetry contract。
M1 SFT 加 `assistant_for_lean_proof` + `M1_USE_BY_ENV` entry。
`docs/m0-dataset-expansion-plan.md` §6 share-alike question 加 5 候选
source 对比表。13 个新 pytest case，sandbox 测试基线 148 → 161 passed +
2 skipped。data_registry 行待 product/legal 拍板再开 — 决议后是一次性
≤ 50 行 yaml PR。
