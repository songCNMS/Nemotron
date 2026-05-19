# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

- 由 task011 implementation roadmap 派生。task021 是 critical-path 前置；§1.8 列 4 个 infra 子条目，整块 PR 装不下。Session 切片落在本 task README。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 per-env telemetry emitter for M0 oracle health-baseline.

具体改动:

- `run_m0_health_baseline.py`:
  - 每个 verifier (score_text / score_numeric / score_json_value /
    score_command / score_patch / score_negative_recognition /
    score_tool_call) 包一层 timing + 收集语义化字段，写进 diagnostics
    dict。`score_record` 返回 shape 不变 (兼容现有 callers)。
  - `aggregate_scored_rows` 新增 `telemetry: {<name>: {…}}` 块，按字段
    类型聚合 (数值 mean/max/p99 / count；bool true_count / false_count；
    string/int 计 distinct value count)。
  - `summarize_health` 增加 cross-check declared-vs-emitted 列表，
    缺口写进 `env_summary["telemetry_gap"]`。
  - `build_report` + markdown writer 把 telemetry 表加进 .md。
- 测试: `tests/recipes/super3/test_m0_health_baseline.py` 加 4 个 case
  (latency_ms always present; tool_schema verifier emits
  invalid_tool_call/argument_match; aggregation produces summary;
  cross-check flags missing names).
- Doc: `docs/implementation-roadmap.md` §1.8 / §5 critical path 把
  Session 1 标 ✓ + 备注下一步 Session。

Sandbox 测试: M0 suite (test_m0_data_env + test_m0_health_baseline +
test_chat_template_super3) 全过；具体计数等 pytest 跑完更新。

Session 2-4 仍未启动；本 task 维持 InProgress。

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #30 已 squash-merge 为 `09c9089` 进 main。intern status 回 Idle (Session 18)。task021 整 task 仍 InProgress：Session 2 (W&B artifact lineage)、Session 3 (sandbox container build)、Session 4 (cluster verify) 都没启动。下一个 critical-path 候选 (roadmap §5)：task021 Session 2 (lineage schema 是 sandbox-friendly) 或 task014 (M1 RLVR data bridge)。

## Session 3 - 2026-05-18 - intern_nemontron_review_cc

实现 task021 Session 2 — cross-stage lineage schema + M0/M1 manifest emission.

设计选择：用 lightweight dataclasses (`src/nemotron/recipes/super3/milestones/lineage.py`) 而不是复用 `src/nemotron/kit/artifacts/base.py::Artifact`。理由：

- 后者 pydantic + W&B tracker + registry publish 三重耦合，pulling in pydantic 让 sandbox 测试需要 importorskip (chat_template_super3 测试踩过这个 pit)。
- Lineage block 直接住进 manifest.json，没有"额外的 metadata.json"概念；CI 工具可以 grep 一下 manifest 就能 walk 整条链路。
- 未来 Session 3 接 W&B publish 时，把 `Artifact.get_input_uris()` 这一类的 method 改成读 manifest 里的 lineage block 就可以，不需要 reshape schema。

实现：

- `lineage.py` (281 lines)：
  - `LineageInput` / `LineageOutput` / `LineageRecord` dataclasses，frozen-friendly。
  - `make_record(...)` 构造器自动盖时间戳 + schema version。
  - `walk_chain(starting_manifest)` 沿 `manifest`-kind inputs 递归到 root，oldest-first 返回。
  - `validate_chain(starting_manifest)` 报破链：缺 manifest input / 引用文件不存在 / artifact_type 不在 plan §10 vocabulary。
  - 11 个 plan §10 artifact-type 名字（`RAW_DATA_ARTIFACT` … `EVAL_REPORT_ARTIFACT`）作为模块常量导出。
- `prepare_m0_assets.py`: 每个 HF 数据集 → 一条 `hf_dataset` input；每个 split file → 一条 `m0_jsonl_split` output；emit `RawDataArtifact`。
- `prepare_m1_agentic_sft.py`: M0 manifest.json → `manifest` input；health-baseline report (如有) → `m0_health_baseline_report` input；train.jsonl / val_shadow.jsonl / blend.json → outputs；emit `SFTDataArtifact`。
- 测试 `tests/recipes/super3/test_lineage.py` (8 cases): JSON 双向转换、constants 完整、walker oldest-first、validate 报破链、happy-path 静默、end-to-end M1 emission 走 prepare() 真出 manifest 看 lineage。

测试基线推到 60 passed + 1 skipped (52 + 8 新)。Session 3 (sandbox containers) / Session 4 (cluster verify) 仍 InProgress。

## Session 4 - 2026-05-18 - intern_nemontron_review_cc

Session 3 PR #32 已 squash-merge 为 `62b7774` 进 main — cross-stage lineage schema (`lineage.py`) + M0/M1 manifest emission + 8 个新 pytest case 都进了 main。intern status 回 Idle (Session 20)。task021 整 task 仍 InProgress：Session 3 (sandbox container build：code-exec / Lean / terminal Dockerfile) 和 Session 4 (NeMo-RL / Ray / vLLM 真集群验证) 都没启动；Session 4 仍 block 在 NemTron cluster access 上。下一个 critical-path 候选 (roadmap §5)：task014 (M1 RLVR data bridge) 或 task015 (RLVR 21-env mix)。


## Session 5 - 2026-05-18 - intern_nemontron_review_cc

Session 3 实现 — sandbox container 构建基建 (roadmap §1.8 task021 第 3
个子条目)。落地 5 个 sandbox-runnable 产物：

- 3 个 Dockerfiles 在新模块 `src/nemotron/recipes/super3/milestones/sandbox_containers/`:
  - `code_exec.Dockerfile` (python:3.12-slim + pytest，UID 1000，pip
    purged 后)
  - `lean.Dockerfile` (debian:bookworm-slim + elan v3.1.1 + Lean 4
    stable，apt curl purge after install，UID 1000)
  - `terminal.Dockerfile` (alpine:3.20 + bash + coreutils + findutils +
    grep + sed + gawk，UID 1000)
- `sandbox_image_registry.yaml` 注册表：`image_id` → `dockerfile_path` /
  `target_envs[]` / `version_tag` / `base_image` / `runtime_recommendations` /
  `notes`。3 行: code_exec → `[code_execution_python]`, lean →
  `[math_formal_lean]`, terminal → `[terminal_basic_shell]` (terminal_pivot
  等 task057 落 M0 之后加进去)。
- `image_resolver.py`：`load_sandbox_image_registry` / `resolve_image_for_env`
  / `image_tag` / `resolve_dockerfile_path` / `validate_dockerfile_exists` /
  `envs_covered_by_registry` 一套 helper，sandbox-runnable。
- `build_sandbox_containers.sh`：包装 docker / podman / singularity build，
  读 YAML 注册表（inline python yaml）逐 image 构建。支持 `--runtime` /
  `--only <id>` / `--dry-run` / `--help` 四个 flag。
- 接入 task030 Session 1 unified registry：
  - `data_registries/schema.py` 加 `sandbox_image_registry` kind +
    KNOWN_KINDS 从 5 → 6
  - `unified_index.yaml` 加一行 `m1_sandbox_images` entry
  - `unified_index_loader._ROWS_KEY_BY_KIND` + `_row_identity` 加分支

测试 `tests/recipes/super3/test_sandbox_containers.py` 25 cases:

- Registry shape 5：load + path + dup id 拒 + 缺字段拒 + target_envs 空 拒
- Dockerfile on-disk 2：每行 path 真存在 + image_tag 格式
- Per-env 3：known envs 返正确 tag / unsandboxed envs 返 None / envs_covered_by_registry
- Dockerfile content lint × 3 file = 9：FROM 在头 + USER 非 root + 无
  `:latest` / 无未 pin branch URL
- Build script 3：可执行 + 正确 shebang + 引用 registry yaml
- Cross-registry (unified index 接入) 3：unified_index 含 m1_sandbox_images
  / live validation clean / KNOWN_KINDS 含 sandbox_image_registry

测试基线 164 → 189 passed + 6 skipped (25 new). 修了 task030 的
test_unified_data_registry.py `test_known_kinds_covers_today_registry_families`
里硬编码的 5-kind set，加上 `sandbox_image_registry` 第 6 个。

Roadmap §1.8 task021 Session 3 ☐ → ✓。task021 整 task 仍 InProgress：
Session 4 (NeMo-RL / Ray / vLLM / NeMo-Gym launch path on real cluster)
没启动 — 需 NemTron cluster access。

Session 4 不在本 PR。本 PR 也不动 ContainerSandbox runtime shim (那条把
M0 verifier 的直 subprocess 改成走容器) — 那是 task021 Session 5 或单
独 PR。

## Session 6 - 2026-05-18 - intern_nemontron_review_cc

Session 3 PR #53 已 squash-merge 为 `d6e5b25` 进 main — sandbox container
构建基建 + 3 个 Dockerfile + image_resolver + build script + 25 个 pytest
case + task030 unified index 接入都进了 main。intern status 回 Idle
(Session 40)。task021 整 task 仍 InProgress：Session 4 (NeMo-RL / Ray /
vLLM cluster verify — block on NemTron) + Session 5 候选 (ContainerSandbox
runtime shim 把 M0 verifier 直 subprocess 改成走容器) 没启动。

下一个候选 (sandbox-runnable): task021 Session 5 (ContainerSandbox shim
单测可用 Mock(subprocess) + 真 image_resolver 路径) / task030 Session 2
(schema enforcement at write time + module-local loader merge schema 层) /
task019-020 (M1 eval basket — block on task014 Session 2 真 RLVR checkpoint).
