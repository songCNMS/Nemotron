# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 40 |

最近：task021 Session 3 (PR #53 `d6e5b25`) 已 squash-merge 进 main —
sandbox container 构建基建。新模块 `sandbox_containers/` 含 3 个
Dockerfile (code_exec / lean / terminal，都 UID 1000 非 root) +
`sandbox_image_registry.yaml` + `image_resolver.py` (`resolve_image_for_env(env_id)`)
+ `build_sandbox_containers.sh` (docker / podman / singularity 任一)。
接入 task030 Session 1 unified index：加 `sandbox_image_registry` 第 6
个 kind + `m1_sandbox_images` entry。25 个新 pytest case，sandbox 测试
基线 164 → 189 passed + 6 skipped。

task021 整 task 仍 InProgress：Session 4 (NeMo-RL / Ray / vLLM cluster
verify — block on NemTron access) + Session 5 候选 (ContainerSandbox
runtime shim 把 M0 verifier 直 subprocess 改成走容器 — 改生产行为) 待开。

下一个候选 (sandbox-runnable):
- **task021 Session 5** — ContainerSandbox runtime shim 接入 `run_m0_health_baseline.run_python_unit_tests` (单元测试用 `Mock(subprocess)` + 真 image_resolver 路径)
- **task030 Session 2** — schema enforcement at write time (pre-commit hook) + 把 8+ module-local loader 接进 schema 层 merge 两层校验
- **task019 / task020** — M1 eval basket (本身 sandbox-runnable，acceptance 要真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都需 cluster / Docker / HF
