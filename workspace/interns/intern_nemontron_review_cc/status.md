# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 42 |

最近：task021 Session 5 (PR #55 `43b3612`) 已 squash-merge 进 main —
ContainerSandbox runtime shim 接 M0 verifier。新模块
`sandbox_containers/runtime_shim.py` 含 ContainerSandbox dataclass +
build_argv (docker/podman 同 dialect / singularity exec dialect) +
sandbox_for_env。`run_python_unit_tests` 加 `container_runtime` kwarg
顺 score_record → score_rows → evaluate_policy → summarize_baselines →
CLI `--container-runtime` 一路串。**默认 None 保留 sys.executable -I
字节级 byte-for-byte 不变**；显式 `--container-runtime docker` 走容器
路径。Envs 没注册 image → in-process fallback + container_fallback=True
标 diagnostics。15 个新 pytest case，sandbox 测试基线 189 → 204 passed
+ 6 skipped。

task021 整 task 仍 InProgress：Session 4 (NeMo-RL / Ray / vLLM cluster
verify) 待 NemTron access。

下一个候选 (sandbox-runnable + leverage):
- **task030 Session 2** — schema enforcement at write time (pre-commit
  hook tooling) + 把 module-local loader 接进 schema 层 merge 两层校验
- **task021 Session 6 候选** — 把 RLVR rollout default `container_runtime`
  从 `None` 翻成 `"docker"` (production behavior flip；独立 PR)
- **task019 / task020** — M1 eval basket (本身 sandbox-runnable，acceptance
  要真 RLVR checkpoint)
- **task058 follow-ups** — 之前 task058 加了 hf_placeholder license-lint，
  pydantic 依赖只在 NemTron 跑；可加更多 license/contamination 检查
- 之前 task 的 Session 2+ — 大都需 cluster / Docker / nvcr container
