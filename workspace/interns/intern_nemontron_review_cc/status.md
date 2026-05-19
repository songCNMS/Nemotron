# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task021_m1_infra_minimum -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task021_m1_infra_minimum |
| PR | pending push |
| Session | 41 |

正在做：task021 Session 5 — ContainerSandbox runtime shim 接 M0 verifier。
新模块 `sandbox_containers/runtime_shim.py` 含 `ContainerSandbox`
dataclass (docker / podman 同 dialect / singularity exec dialect) +
`build_argv` 纯函数 (--rm --network=none --mount bind --workdir
--read-only --tmpfs --cpus --memory) + `sandbox_for_env(env_id)`。
`run_python_unit_tests` 加 `container_runtime` kwarg 顺着
`score_record` → `score_rows` → `evaluate_policy` → `summarize_baselines`
→ CLI `--container-runtime {docker,podman,singularity}` 一路串。**默认
`None` 保留 in-process subprocess 字节级同 behavior** (regression gate)；
显式 `--container-runtime docker` 才走容器路径。Envs 没注册 image →
in-process fallback + diagnostics 标 `container_fallback=True`。15 个新
pytest case (subprocess monkey-patched)，sandbox 测试基线 189 → 204
passed + 6 skipped。
