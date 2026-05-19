# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task021_m1_infra_minimum -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task021_m1_infra_minimum |
| PR | pending push |
| Session | 39 |

正在做：task021 Session 3 — sandbox container 构建基建。新模块
`src/nemotron/recipes/super3/milestones/sandbox_containers/` 含 3 个
Dockerfile (code_exec / lean / terminal) + `sandbox_image_registry.yaml`
+ `image_resolver.py` + `build_sandbox_containers.sh` (支持 docker /
podman / singularity)。所有 Dockerfile 都 USER 非 root；image_resolver
按 env_id 返 `<image>:<version>` tag（envs 不需 sandbox 时返 None 让
caller fallback in-process）。接入 task030 Session 1 unified registry：
schema 加 `sandbox_image_registry` 第 6 个 kind，unified_index 多一行
`m1_sandbox_images`。25 个新 pytest case (registry shape / Dockerfile
lint / build script / unified index 接入)，sandbox 测试基线 164 → 189
passed + 6 skipped。Session 4 (cluster verify) 不在本 PR。
