# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task040_w1_curriculum_sampler -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task040_w1_curriculum_sampler |
| PR | pending push |
| Session | 75 |

正在做：task040 Session 1 — W1 difficulty curriculum sampler。Plan §6
W1 deliverable，roadmap §4 long-pending row。

## What's in this PR

### `m0_data_env/difficulty_sampler.py` 新模块

- `BUCKET_ORDER = ("trivial", "unknown", "hard")` — 跟 task008
  `prepare_m1_agentic_sft._difficulty_for` / DIFFICULTY_* 常量对齐
- `KNOWN_BUCKETS` frozenset；`VALID_POLICIES` frozenset
  (easy_first / hard_first / shuffle / as_is)
- `DEFAULT_SOLVED_THRESHOLD = 0.9`
- `bucket_rows(rows, *, policy, rng=None)`：
  - easy_first：ascending bucket ordinal (trivial → hard)；stable
    within bucket
  - hard_first：descending；same stability
  - shuffle：deterministic given rng；operator 必须传 rng 给 reproducibility
  - as_is：passthrough (control)
  - Unknown / missing bucket → middle ordinal (不丢)
- `filter_solved(rows, *, pass_rates=None, threshold=0.9)`：
  - 缺 pass_rates → keep everything (no signal → no decision)
  - Row id 解析顺序：metadata.m0_source_id > metadata.source_id >
    top-level id > instance_id
  - Strict > threshold (exact-threshold row kept)
- `weighted_sample(rows, *, weights, n, rng=None, replace=False)`：
  - replace=False (default)：caps at len(rows)
  - replace=True：emits exactly n
  - Negative weights → ValueError
  - All-zero weights → []
  - 没在 weights map 里的 bucket → weight 0 (excluded)

### 设计 vs scaffold spec

Scaffold README 原说 `BUCKET_ORDERINGS` per-domain ordinal map，但
task008 实际只用了一个简单 3-bucket categorical (`trivial` / `unknown` /
`hard`) 跨所有 env。所以本 PR 用一个共享 `BUCKET_ORDER` 元组而不是
per-domain dict — 跟实际数据 schema 对齐。

## Tests (`test_difficulty_sampler.py`, 23 cases)

- Constants 3：BUCKET_ORDER / VALID_POLICIES / DEFAULT_SOLVED_THRESHOLD
- bucket_rows 7：easy_first 3-bucket sort / hard_first reverses /
  stable within bucket / unknown → middle / as_is passthrough /
  shuffle deterministic / unknown policy raises
- filter_solved 5：drops > threshold / keeps == threshold /
  no pass_rates keeps all / row_id resolution preference /
  no-id rows pass through
- weighted_sample 8：respects weights / deterministic rng /
  no-replace caps at pool size / with-replace = exactly n /
  all-zero weights = [] / negative weights raise /
  missing-bucket = excluded / n=0 = []

Sandbox 测试基线 520 → **543 passed + 7 skipped** (23 new)。

## task040 状态

- Session 1 ✓ (this PR) — core sampler
- Session 2 ☐ — wire into prepare_m0_assets.py / prepare_m1_agentic_sft.py
  via `--curriculum-policy` CLI flag (sandbox-runnable next)
- Session 3 ☐ — numeric pass-rate filter (depends task032 rollout store, M2)
- Session 4 ☐ — per-env curriculum policy YAML

Roadmap §4 cross-cutting + §5b sandbox queue 状态更新。
