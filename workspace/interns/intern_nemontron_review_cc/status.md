# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task040_w1_curriculum_sampler -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task040_w1_curriculum_sampler |
| PR | pending push |
| Session | 91 |

正在做：task040 Session 2 — wire the W1 curriculum sampler into
`prepare_m1_agentic_sft.py` via opt-in CLI flags. Session 1 (PR #99)
shipped the sampler primitives; this PR threads them into the data
prep path.

## What's in this PR

### 4 new CLI flags on `prepare_m1_agentic_sft.py` (`build_parser`)

- `--curriculum-policy {as_is,easy_first,hard_first,shuffle}` — default
  `as_is` (passthrough; back-compat for existing callers)
- `--curriculum-seed <int>` — default 0; deterministic shuffle when
  `policy=shuffle`
- `--curriculum-pass-rates-json <path>` — optional JSON `{row_id: float}`
  for `filter_solved`; M1 sandbox operators supply a static JSON, M2
  task032 rollout store will feed dynamic values
- `--curriculum-solved-threshold <float>` — default 0.9

### `_apply_curriculum_to_train(train_rows, *, policy, seed, pass_rates_path, solved_threshold)`

Pure helper composing task040 Session 1's `filter_solved` +
`bucket_rows` against the M1 SFT train split:

- Drop happens BEFORE reorder (rows above threshold filtered, then
  remaining rows policy-ordered)
- Returns `(reordered_rows, audit_dict)`
- Audit dict shape locked: `policy / seed / pass_rates_provided /
  solved_threshold / rows_in / rows_out / rows_dropped_solved`
- **Val rows never reordered** — shadow eval needs stable ordering
  for reproducibility

### Manifest gets a `curriculum` block

The audit dict lands at `manifest["curriculum"]` so downstream
consumers (W&B publisher / dashboard) can see what curriculum config
was applied without re-running.

### Tests (`test_curriculum_sampler_wiring.py`, 13 cases)

- as_is is passthrough (back-compat) 1
- Policy reorderings 3: easy_first / hard_first / shuffle determinism
- Pass-rates wiring 3: drops > threshold / exactly-at threshold kept /
  compose with policy reorder (drop-then-easy-first)
- Error surfaces 2: missing pass-rates file / non-object JSON
- CLI surface 3: 4 flags exposed with correct defaults / rejects
  unknown policy / accepts each valid policy
- Audit dict shape lock 1: exactly 7 keys, contract for manifest

Sandbox 测试基线 662 → **675 passed + 7 skipped** (13 new).

## 不在本 PR

- `prepare_m0_assets.py` wiring — the bucket info is added by the M1
  agentic SFT converter (per task008), not by M0 prep. So M0 has no
  meaningful `difficulty_bucket` to sample on. The original scaffold
  listed M0 prep as a target but the schema doesn't support it.
- W2 cross-stage curriculum coordination (Session 4 territory)

## task040 状态

- Session 1 ✓ (PR #99) — sampler primitives
- Session 2 ✓ (this PR) — wired into M1 agentic SFT
- Session 3 ☐ — numeric pass-rate filter via task032 rollout store
  (M2 dependency)
- Session 4 ☐ — per-env curriculum policy YAML

Roadmap §5b 更新.
