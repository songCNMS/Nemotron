# task019 - task_knowledge

## Plan §5.7 v0 acceptance list

Eight benchmarks for M1 promotion gate:

| benchmark_id | category | gate_metric | license | upstream |
|---|---|---|---|---|
| mmlu_pro | reasoning_mc | accuracy | mit | TIGER-Lab/MMLU-Pro |
| aime25 | reasoning_math_competition | pass_at_1 | cc-by-sa-4.0 ⚠ | AIME 2025 |
| gpqa | reasoning_graduate_science | accuracy | cc-by-4.0 | idavidrein/gpqa |
| livecodebench | code_competitive_programming | pass_at_1 | cc-by-4.0 | livecodebench |
| ifbench | instruction_following | strict_accuracy | apache-2.0 | (HF varies) |
| multichallenge | multi_turn_instruction | judge_accuracy | cc-by-4.0 | scale-ai/multichallenge |
| ruler_256k | long_context | needle_accuracy | apache-2.0 | ruler |
| taubench_airline | tool_use_agentic | success_rate | cc-by-4.0 | sierra-research/tau-bench |

## License decisions

AIME25 is cc-by-sa-4.0 — same family as HotpotQA. Eval-time use is
*not* training-time inheritance:

- Training-time use of CC-BY-SA dataset cascades share-alike to any
  derived checkpoint
- Eval-time use (running a benchmark *against* a checkpoint) does NOT
  cascade — the checkpoint isn't derived *from* the eval data
- task058 license_audit module will surface AIME25 anyway via the
  registry walk; readers should understand the audit is informational
  for eval baskets, blocking for training data

## regression_report status semantics

5 mutually exclusive states per benchmark:

| status | When | What it means |
|---|---|---|
| improved | both runs, delta > +tolerance | gate improved |
| regressed | both runs, delta < -tolerance | gate regressed (PROMOTION BLOCKER) |
| unchanged | both runs, |delta| ≤ tolerance | noise / no signal |
| new | only in current | new benchmark wired; no historical baseline |
| dropped | only in baseline | benchmark stopped reporting (harness crash?) |

Tolerance is `DEFAULT_REGRESSION_TOLERANCE = 1e-4`. Eval runs aren't
bit-exact; this absorbs sampling noise. Operator can pass a tighter
tolerance if they want stricter promotion gates.

## NeMo Evaluator task names

NeMo Evaluator uses `adlr_*` prefix for its built-in adapter set (see
`stage3_eval/config/default.yaml` for examples). `m1_basket.yaml`
uses the same convention:

- `adlr_mmlu_pro` → MMLU-Pro adapter
- `adlr_aime25` → AIME25 adapter
- etc.

The suffix matches `benchmark_id` in the registry so the cross-walk
between config selection and registry rows is unambiguous.

## task030 Session 3 dependency satisfied

task030 multiple closeout notes marked Session 3 as "block on task019/020
给 eval basket 真定义". Session 1 of task019 satisfies that block by:

1. Adding `eval_basket_registry` kind to `schema.py::_KIND_SCHEMAS`
2. Adding `m1_eval_basket` entry to `unified_index.yaml`
3. Wiring the kind into `unified_index_loader._ROWS_KEY_BY_KIND` and `_row_identity`

After this PR, task030 Session 3 is also complete.

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| Registry shape + schema integration | yes |
| regression_report math (load JSON / diff / format markdown) | yes |
| m1_basket.yaml file shape | yes |
| 真 `nemotron super3 eval -c m1_basket` 启动 | no — NeMo Evaluator + checkpoint + cluster |
| W&B publish | no — runtime credentials |
| Per-benchmark adapter setup | partial — config side yes, real benchmark run no |

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，pre-existing；非 sandbox 正常跑。
