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

