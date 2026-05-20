# task040_w1_curriculum_sampler

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #99 / a090453 on 2026-05-19 (bucket_rows / filter_solved / weighted_sample + 23 tests) -->
<!-- SESSION 2 LANDED: PR pending on 2026-05-20 (wired into prepare_m1_agentic_sft.py via --curriculum-policy CLI flag; 13 tests) -->

## 背景

Plan §6 W1 deliverable: **difficulty curriculum sampler**.

> Create difficulty curricula by filtering samples the current SFT model
> already solves consistently, then sorting the remaining samples by
> pass rate, judge confidence, and rollout length.

Roadmap §4 cross-cutting work cites:

> W1 difficulty curriculum sampler — task008 added bucket metadata;
> sampler not wired

task008 已经把每行 M0 数据上了 `difficulty` 字段 (categorical bucket per
domain)，但下游 SFT/RL data prep 完全没用这个字段 — 数据按原顺序喂模型。
本 task 把 sampler 接进去：训练前把 row 按 bucket 排序、过滤、加权，让
模型先吃简单题再吃困难题 (或反过来：丢掉已经能解的简单题)。

## 整 task 拆 Sessions

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | `m0_data_env/difficulty_sampler.py` 实现 — `bucket_rows(rows, *, policy)` + `filter_solved(rows, pass_rate_threshold)` + `weighted_sample(rows, weights)` | yes | ✓ Done (this PR) |
| 2 | Wire into `prepare_m1_agentic_sft.py` via opt-in CLI flags (`--curriculum-policy` / `--curriculum-seed` / `--curriculum-pass-rates-json` / `--curriculum-solved-threshold`); train-only (val skipped for shadow-eval reproducibility) | yes | ✓ Done (this PR) |
| 3 | Integrate with task032 rollout store pass-rate (M2 dependency) for `filter_solved` real data; until then operator supplies a static pass-rate JSON | partial (depends task032) | Todo |
| 4 | Per-env curriculum config: `m0_data_env/curriculum_policies.yaml` declares per-env policy + threshold defaults | yes | Todo |

## Session 1 目标

新模块 `m0_data_env/difficulty_sampler.py`:

- `BUCKET_ORDERINGS` — declarative bucket → ordinal map per domain (e.g.,
  `math_reasoning_numeric` rows have buckets `easy / medium / hard`;
  `code_execution_python` has `trivial / standard / advanced`)
- `bucket_rows(rows, *, policy)` returns rows re-sorted per policy
  - `easy_first` — ascending bucket ordinal
  - `hard_first` — descending bucket ordinal
  - `random` — passthrough (control)
  - `drop_solved` — pair with `filter_solved`
- `filter_solved(rows, *, pass_rates, threshold)` — drop rows whose
  prior-checkpoint pass rate exceeds `threshold` (default 0.9)
  - `pass_rates` is a `dict[row_id, float]` keyed on
    `metadata.source_id` or `instance_id`
- `weighted_sample(rows, *, weights, n, rng)` — emit `n` rows with
  per-row sampling weight; `weights` is `dict[bucket, float]`. Caps the
  sample at `len(rows)` (no oversample by default; opt-in via `replace`)

## Session 1 验收

- [x] 新模块 `m0_data_env/difficulty_sampler.py` + tests
- [x] `BUCKET_ORDER` covers task008's 3-bucket vocabulary
  (`trivial` / `unknown` / `hard`) — schema simpler than initial scaffold
  spec; one shared ordering instead of per-domain BUCKET_ORDERINGS
- [x] `bucket_rows` 4 policy (easy_first / hard_first / shuffle /
  as_is) 各自 sanity-tested
- [x] `filter_solved` 处理 missing pass_rate (keep), exact-threshold
  (keep), > threshold (drop), row_id resolution preference (m0_source_id
  > source_id > id > instance_id)
- [x] `weighted_sample` deterministic given fixed seed, replace +
  no-replace modes, zero-weight handling, negative-weight rejection
- [x] **23 个 pytest case** (vs ≥12 acceptance)
- [x] Roadmap §4 cross-cutting row + §5b sandbox queue updated with
  Session 1 ✓

## 依赖

- 不依赖 cluster / W&B / HF / Docker
- 依赖 task008 (bucket metadata) — already landed
- Sessions 2-4 sandbox-runnable
- Session 3 真 `filter_solved` 需 task032 rollout store (M2 dependency)；
  before that, operator supplies a static pass-rate JSON

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml` — `difficulty` field per row
- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py` — wiring target for Session 2
- plan §6 W1 + roadmap §4 cross-cutting

## 不在本 task

- Pass-rate emission from RL rollouts (task032 rollout store, M2)
- Per-environment quotas / backpressure (task033 env scheduler, M2)
- Dynamic resampling during training (task038 M2 RL curriculum)
