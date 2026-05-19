# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task021_m1_infra_minimum -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task021_m1_infra_minimum |
| PR | pending push |
| Session | 45 |

正在做：task021 Session 6 — rollout policy guard rail。原 plan 的 "literal
default flip from None to docker" 在 in-repo 没有 coherent target (M0
oracle 不需要容器；M1 RLVR rollout 在外部 NeMo-Gym repo)。改用 "guard
rail" 语义：

- `ROLLOUT_POLICY_ORACLE` / `ROLLOUT_POLICY_ADVERSARIAL` 常量 +
  `recommended_container_runtime(policy)` helper
- `run_python_unit_tests` 加 `rollout_policy: str = "oracle"` kwarg —
  adversarial + container_runtime=None → `RuntimeError` 立即报警，防
  untrusted code silently 跑 host。oracle 默认保持 Session 5 字节级 in-
  process 行为不变
- 顺 `score_record` → `score_rows` → `evaluate_policy` → `summarize_baselines`
  → CLI `--rollout-policy {oracle,adversarial}` 一路串
- typo → ValueError；adversarial + docker → 跑成功 + diagnostics 加
  `rollout_policy` 痕迹

11 个新 pytest case；sandbox 测试基线 215 → 226 passed + 6 skipped。
修了 Session 5 的一个 stub (fake_runner 加 `**kwargs`)。

task021 整 task 仍 InProgress：Session 4 (cluster verify) 待 NemTron。
