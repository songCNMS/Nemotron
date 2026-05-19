# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 plan §6 W1 派生：跨 SFT + RL + Eval 的 unified data registry。今天 8
个 registry YAML 散在 5 个目录，每个有自己的 loader。Session 1 决定不
合并文件 — 上面叠一层 schema + 索引 + cross-registry walk。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 schema 层 + unified index + 三个 inventory walk。设计:

- 新模块 `src/nemotron/recipes/super3/milestones/data_registries/`，
  跟 `_bridge_base.py` 同层 (跨 milestone 的共享代码)。
- 三个文件:
  - `schema.py` — 5 个 kind 的 row 校验 (per-kind required fields +
    extra_row_validator hook)
  - `unified_index.yaml` — 8 个 registry 一行 entry + kind / path /
    summary / produced_by / consumed_by / expected_mixes (仅
    bridge_env_registry)
  - `unified_index_loader.py` — load + validate + 三个 read-only
    inventory walk (licenses / hf_dataset / m0_to_downstream)
- 关键设计点 1: **schema 层不替代** module-local loader。`m1_rlvr/`
  / `m1_swe1/` 等的 prepare script 继续用 `_bridge_base.load_env_registry`
  做自己的校验。schema 层是 audit 工具，在 pytest 上层 cross-cut。
  Session 2 之后可以让两层 merge — 但现在先把 audit 工具落到位。
- 关键设计点 2: `KNOWN_BRIDGE_STATUSES` 在 schema.py 重复声明而不 import
  `_bridge_base`，保持 data_registries → bridge runtime 单向独立。然
  后用 pytest 验证两层是否对齐 — drift 由 test 发现，不靠 import 强
  绑定。
- 关键设计点 3: `bridge_env_registry` 的 `expected_mixes` 字段在
  unified_index.yaml 上声明，而不是在每个 registry 自己的 yaml 上。
  这样 schema 层就能 catch "RLVR 行错放到 SWE1 registry" 这种 copy-
  paste bug — 之前只在 bridge runtime 校验时才能发现。
- Live registries 全过 (`test_live_unified_index_validation_is_clean`
  return `[]`)。
- 19 个 pytest case 跨：schema 校验 6 + index shape 4 + live
  validation 2 + cross-registry inventory 4 + read-only 检查 1 + 双
  向对齐 1 + dispatcher 1。

测试基线 129 + 2 skipped → 148 + 2 skipped (19 new)。
`test_m1_agentic_sft.py` pyarrow collect-error pre-existing。

Roadmap §3 W1 row 状态从 "✗ — RL and eval data have no registry" → ⚠
(Session 1 ✓；eval registry 等 task019)。§5 critical-path #11 task030
加 Session 1 进展。

Session 2+ 不在本 PR:
- task019 / task020 落地后加 eval_basket_registry kind + index row
- Pre-commit / pre-PR hook 自动跑 `validate_unified_index()`
- 把 8 个 module-local loader 接进 schema 层 (merge 两层校验逻辑)

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #48 已 squash-merge 为 `ec1b271` 进 main — data_registries
模块 + schema 层 + 索引 + 3 个 inventory walk + 19 个 pytest case 都进
了 main。intern status 回 Idle (Session 36)。task030 整 task 仍
InProgress：Session 2 (eval basket registry + schema enforcement +
module-local loader merge) 未启动。

下一个候选：之前 task 的 Session 2+ 大都需 cluster/Docker。Sandbox-
runnable 候选：task019/020 (eval basket — 但 block on task014 Session 2
真 RLVR checkpoint)。


## Session 3 - 2026-05-18 - intern_nemontron_review_cc

实现 schema enforcement at write time。Session 1 落了 validator + 索引 +
inventory；Session 2 把 validator 包成 CLI + pre-commit hook，operators
不显式调用 `validate_unified_index()` 也能在 commit 时拦下 shape drift。

新增产物：

- **`scripts/validate_data_registries.py`** — CLI 包 `validate_unified_index()`，
  退出码:
  - 0 = 全部 registry clean
  - 1 = shape drift (issues 走 stderr，registry id 走 stdout via --paths)
  - 2 = validator 本身坏 (missing index / import 失败)
  - Flags: `--quiet` (pre-commit 静默 clean) / `--paths` (stdout 只列
    offending registry id，方便 pipe) / `--index-path` (测试用，可改默认
    路径)

- **`.pre-commit-config.yaml` local hook**：
  - `id: validate-data-registries`
  - `entry: bash -c 'PYTHONPATH=src python3 scripts/validate_data_registries.py --quiet'`
  - `files: ^(src/.../milestones/.*\.(yaml|yml)|scripts/validate_data_registries\.py|src/.../data_registries/.*\.py)$`
    — trigger on registry YAML / loader / schema / script 变动
  - `pass_filenames: false`（script 总 validate 整个索引；per-file 没意义）

设计决策：**不**合并 bridge runtime loaders 跟 schema 校验层。`_bridge_base.load_env_registry`
fail-fast 在第一个 issue raise，prepare step 立刻 abort；schema 层
`validate_rows` 收集 *所有* issues 给 PR review。两个 consumer 不一样 —
merge 会破坏 fail-fast，runtime 跑废 partial data。在 script docstring +
README 明确写出。

测试 `tests/recipes/super3/test_validate_data_registries_cli.py` 11 cases:

- Script file shape 2: 存在 + 可执行 + python shebang
- Clean-main 2: 整 index clean 时 exit 0 / `--quiet` 不出 stdout
- Broken-index 3 (subprocess 跑真 CLI):
  - 缺 status 字段 → exit 1 + stderr 含 issue 数 + missing required field
  - `--paths` → stdout 一行一 registry id；stderr 无 verbose dump
  - 不存在 index 文件 → exit 2 (区分 CI infra 坏 vs schema drift)
- In-process main() 2: 同 subprocess 但作为 import 测，快反馈给 Python caller
- Pre-commit config 2: yaml 解析 + local hooks 含 validate-data-registries
  id + entry 引 PYTHONPATH=src + scripts 路径 + --quiet

测试基线 204 → 215 passed + 6 skipped (11 new). `test_m1_agentic_sft.py`
pyarrow collect-error pre-existing。

Session 2 不在本 PR 的两个 carry-over:
- M1 eval basket registry (Session 3 候选；block task019/020)
- Bridge / M0 loader 接 schema 层 (Session 4 候选；注意 fail-fast 语义)

## Session 4 - 2026-05-18 - intern_nemontron_review_cc

Session 2 PR #57 已 squash-merge 为 `324e062` 进 main —
`scripts/validate_data_registries.py` CLI + `.pre-commit-config.yaml`
local hook + 11 个 pytest case + 设计决策 (不合并 bridge fail-fast 跟
schema collect-all) 都进了 main。intern status 回 Idle (Session 44)。
task030 整 task 仍 InProgress: Session 3 (M1 eval basket — block on
task019/020) + Session 4 (loader merge into schema layer — careful
refactor) 没启动。

下一个候选: task058 follow-ups (license/contamination 额外校验加进
schema 层) / task021 Session 6 候选 (RLVR rollout default container_runtime
翻 docker) / task030 Session 4 (loader merge) / task019-020 (M1 eval basket，
block on task014 Session 2 真 RLVR checkpoint) / 之前 task 的 Session 2+。

## Session 5 - 2026-05-18 - intern_nemontron_review_cc

实现 Session 4 — bridge / M0 module-local loader 接进 schema 层。Session 1
+ Session 2 closeout 时反复强调"两层 fail-fast vs collect-all 不要合并"，
Session 4 在重新审视这条决策时找到了正确的合并粒度：

**合并 row-shape *definitions*，不合并 aggregation *behavior***。

具体：

- `data_registries/schema.py::validate_rows` 加 `fail_fast=False` 参数：
  - `True` → 第一个 issue 就 raise `ValueError` (runtime semantics)
  - `False` (default) → 收集所有 issues 返 list (audit semantics)
  - 两个 mode 跑同一套 `required_row_fields` 检查 — 这就是单 source of truth
- `schema.validate_rows` 加 `source_path=None` 参数：runtime loader 传文
  件路径，error message 前缀就是 yaml path (matches pre-Session-4 格式)
- `schema.validate_top_level` 加 `strict=True` 参数：
  - `True` (audit, default) → 要 `schema_version` + `milestone` + rows_key
  - `False` (runtime) → 只要 rows_key (documentation 字段对 runtime 不影响)
- Error message 格式统一成 `f"<rows_key>[<index>] missing required field 'X'"`
  (跟 runtime loader 原来的格式一致)

四个 runtime loader 都 refactor 成"thin wrapper":

| Loader | 删的行数 | 留的 module-specific 逻辑 |
|---|---|---|
| `_bridge_base.load_env_registry` | ~30 行内联校验 | mix-set membership + display_label 包成 `extra_validators` closure |
| `m1_swe2.load_swe2_sif_registry` | ~30 行内联校验 | sif_source 词汇 + filename_template `{instance_id}` 格式 closure |
| `m1_rlhf.load_rlhf_pref_data_registry` | ~20 行内联校验 | (无 module-specific 检查；schema 的 required_row_fields 全覆盖) |
| `sandbox_containers.image_resolver.load_sandbox_image_registry` | ~30 行内联校验 | target_envs 非空 + image_id 唯一 cross-row check |

**关键不变量**: 测试基线 226 → 226 + 7 个新 schema API surface tests =
233 passed + 6 skipped. 没动任何模块测试文件 — 226 + 不动 + 7 新。
Refactor 契约 "external behavior identical" 守住。

新加 7 个测试 (test_unified_data_registry.py):
- `test_validate_rows_fail_fast_raises_on_first_issue` (catch regression
  where fail_fast 被绕过 collect-all)
- `test_validate_rows_fail_fast_with_source_path_includes_path_prefix`
- `test_validate_rows_collect_all_still_returns_full_issue_list` (audit
  mode 仍 collect 完整 list)
- `test_validate_top_level_strict_requires_schema_version_and_milestone`
- `test_validate_top_level_runtime_mode_skips_documentation_fields`
- `test_validate_top_level_runtime_mode_still_requires_rows_key`
- `test_known_bridge_statuses_still_double_aligned_after_session_4`
  (drift detection between schema.KNOWN_BRIDGE_STATUSES vs
  _bridge_base.KNOWN_STATUSES — 两层独立声明但 pytest 强对齐)

## task030 状态

- Session 1 ✓ (PR #48 `ec1b271`) — schema 层 + 索引 + inventory walks
- Session 2 ✓ (PR #57 `324e062`) — CLI validator + pre-commit hook
- Session 4 ✓ (this PR) — module-local loader merge into schema layer
- Session 3 ☐ — M1 eval basket registry (block on task019/020)

Roadmap §3 W1 row + §5 critical-path #11 task030 状态更新 Sessions 1+2+4 ✓。

## Session 6 - 2026-05-18 - intern_nemontron_review_cc

Session 4 PR #61 已 squash-merge 为 `159d81f` 进 main — schema.validate_rows
加 fail_fast + source_path / validate_top_level 加 strict / 4 个 runtime
loader refactor 成 thin wrapper + 7 个新 pytest case 都进了 main。intern
status 回 Idle (Session 48)。

task030 整 task 仍 InProgress：Session 3 (M1 eval basket — block on
task019/020) 待开。下一个候选: task058 follow-ups (license/contamination
额外校验加进 schema 层) / task019-020 (M1 eval basket，block on task014
Session 2 真 RLVR checkpoint) / 之前 task 的 Session 2+。

## Session 7 - 2026-05-18 - intern_nemontron_review_cc

实现 Session 5 — share-alike license cascade audit (task058 license/
contamination 主题 follow-up)。

设计要点：

- 新模块 `data_registries/license_audit.py`:
  - `SHARE_ALIKE_LICENSE_PREFIXES` — CC-BY-SA / GPL / AGPL / LGPL / ODBL 家族
  - `is_share_alike(license_str)` — case-insensitive prefix match;
    支持 None / 整数 / 空字符串 等 defensive 输入
  - `find_share_alike_sources(index)` — 走 `m0_data_registry` +
    `pref_data_registry`，返 share-alike row + 元数据
  - `license_cascade(index)` — 把 share-alike 源串接到 `m0_environment_registry`
    + `bridge_env_registry` 行，按 `m0_env_id` 索引下游 bridge 行；带
    `live_chains` 计数 (=`status==active` 的 bridge 行数)，让运维区分
    live vs latent cascade
  - `format_cascade_report(cascade)` — 文本渲染 (CLI 消费)
- `scripts/validate_data_registries.py` 加 `--license-cascade` flag:
  - 走 audit-only path，**短路** schema validation
  - 退出 0 即使有 finding (informational，share-alike 不是 wrong，是要
    可见性 review)
  - 报告写 stdout (内容)；stderr 留干净

Live audit 今天 finding：

> `m0_search_hotpotqa` (cc-by-sa-4.0, m0_data_registry) — latent: 0 active bridge mapping(s)
>     hf_dataset='hotpotqa/hotpot_qa'
>     m0_env_id='search_grounded_qa'
>     bridge_mappings: (none — no bridge references this M0 env yet)

HotpotQA 是 cc-by-sa-4.0 但 task015 Session 1 audit 删了 `search_grounded_qa`
的 NeMo-Gym 错名 mapping (rlvr1)，所以现在没 bridge 行 reference
`search_grounded_qa` 这个 m0_env_id。**Cascade 是 latent — share-alike
没向任何下游 derived artifact 传**。一旦未来谁把 HotpotQA wire 到 RLVR
mix，audit 会从 latent 翻 LIVE，提醒重审 §6 Q1 决策。

Tests (`tests/recipes/super3/test_license_audit.py`, 27 cases):

- `is_share_alike` predicate 17 cases (7 share-alike 接受 + 10 permissive /
  invalid 拒绝) — `cc-by-sa-4.0` / `CC-BY-SA-4.0` / 带空格 / `gpl-3.0` /
  `AGPL-3.0` / `lgpl-2.1` / `odbl-1.0` 接受；`cc-by-4.0` (非 share-alike)
  / `apache-2.0` / `mit` / `bsd-3-clause` / `license-pending-legal-review` /
  `source-repository-specific` / 空串 / None / int 拒绝
- `find_share_alike_sources` 2 cases — live: 找到 HotpotQA / 拒
  permissive rows (MBPP / GSM8K / NuminaMath / Hermes)
- `license_cascade` 2 cases — HotpotQA 是 latent (post-task015 audit
  搬走了 bridge 引用) / 合成 fixture (active bridge → live_chains=1)
- `format_cascade_report` 3 cases — empty 输出 clean ✓ marker / 含
  license + chain count + LIVE marker / latent marker
- CLI 2 cases — `--license-cascade` exit 0 + 报告写 stdout / 短路
  validation (不输出 default 的 "all registries clean")

测试基线 233 → 260 passed + 6 skipped (27 new). `test_m1_agentic_sft.py`
pyarrow collect-error pre-existing。

文档：`docs/m0-dataset-expansion-plan.md` §6 Q1 加段落指向新 CLI flag，
让 future maintainer 看着 §6 prose 时就知道有 audit 工具配套。

## task030 状态

- Session 1 ✓ (PR #48) — schema layer + index + inventories
- Session 2 ✓ (PR #57) — CLI validator + pre-commit hook
- Session 4 ✓ (PR #61) — module-local loader merge
- Session 5 ✓ (this PR) — share-alike license cascade audit
- Session 3 ☐ — M1 eval basket registry (block on task019/020)

Roadmap §3 W1 row + §5 critical-path #11 状态更新 Sessions 1+2+4+5 ✓。
