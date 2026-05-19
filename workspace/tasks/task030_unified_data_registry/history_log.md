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
