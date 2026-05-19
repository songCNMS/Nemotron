# task019_m1_eval_basket_v0

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR pending on 2026-05-19 (eval basket registry + regression report generator + NeMo Evaluator config) -->

## 背景

`docs/implementation-roadmap.md` §1.7 / §5 critical-path 第 9 条 (parallel
track after task008-018):

> task019 — M1 eval basket v0 — minimum-viable for Super3 parity:
> - NeMo Evaluator launcher wiring
> - Adapters for MMLU-Pro, AIME25, GPQA, LiveCodeBench, IFBench,
>   MultiChallenge, RULER 256K, TauBench airline
> - W&B regression report (gain/loss per task vs previous checkpoint)
> - Acceptance: `nemotron super3 eval -c m1_basket` runs against an SFT
>   checkpoint, produces `regression_report.md`

整 task 拆 Sessions:

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | 8-benchmark registry + schema kind + regression_report.py + m1_basket.yaml | yes | ✓ Done (this PR) |
| 2 | CLI wiring `nemotron super3 eval -c m1_basket` runs against real SFT checkpoint + W&B publish | partial (config-side yes, 真 launch 要 cluster) | Todo |
| 3 | Per-benchmark adapter shim (each adapter may need a config under stage3_eval/config/...; ops collaboration) | yes | Todo |
| 4 | Promotion gate logic — read regression_report deltas, decide promote/hold per plan §5.7 | yes | Todo |

## Session 1 目标

- `m1_eval_basket/m1_eval_basket_registry.yaml` 8 rows (MMLU-Pro /
  AIME25 / GPQA / LiveCodeBench / IFBench / MultiChallenge / RULER
  256K / TauBench airline)。每行: benchmark_id / adapter / category /
  license / gate_metric / notes
- 新 schema kind `eval_basket_registry` 注册进 `data_registries/schema.py::KNOWN_KINDS` + `_KIND_SCHEMAS`
- `unified_index.yaml` 加 `m1_eval_basket` entry
- `unified_index_loader._ROWS_KEY_BY_KIND` / `_row_identity` 加分支
- `m1_eval_basket/regression_report.py` — `load_eval_results` / `diff_eval_runs` /
  `format_regression_report` 三件套，sandbox-runnable
- `stage3_eval/config/m1_basket.yaml` — 8 个 task name (adlr_ 前缀) +
  `defaults: default.yaml`
- 22 个 pytest case (registry shape / 8 row coverage / schema integration /
  regression math improved/regressed/unchanged/new/dropped/sorted / format
  report / config yaml shape)

## Session 1 验收

- [x] 新模块 `m1_eval_basket/__init__.py` + `m1_eval_basket_registry.yaml` + `regression_report.py`
- [x] schema 加 `eval_basket_registry` kind (KNOWN_KINDS 6 → 7)
- [x] `unified_index.yaml` 加 `m1_eval_basket` entry；validate clean
- [x] `stage3_eval/config/m1_basket.yaml` 选 8 个 benchmark task
- [x] regression_report 处理 5 个 status (improved/regressed/unchanged/new/dropped)
- [x] tolerance edge case (within DEFAULT_REGRESSION_TOLERANCE → unchanged)
- [x] 22 个 pytest case；sandbox 测试基线 335 → 357 passed + 7 skipped
- [x] **task030 Session 3 unblock**: eval_basket_registry kind 加进 schema =
  task030 Session 3 acceptance achieved as part of this PR

## task030 Session 3 unblock

task030 多次 closeout 把 Session 3 标 "block on task019/020 给 eval
basket 真定义"。本 PR 给了 eval_basket 真定义 + 新 schema kind + unified
index 接入，task030 Session 3 自动达成。

## 依赖

- 不依赖 cluster / W&B / 真 SFT checkpoint (Session 1 只是 scaffold)
- Session 2 依赖 cluster + NeMo Evaluator + W&B credentials
- Session 4 promotion gate 依赖 Sessions 2-3 真数据

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_eval_basket/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/data_registries/{schema.py,unified_index.yaml,unified_index_loader.py}` — schema 接入
- `src/nemotron/recipes/super3/stage3_eval/config/{default,m1_basket}.yaml` — NeMo Evaluator config
- plan §5.7 + roadmap §1.7 / §5
