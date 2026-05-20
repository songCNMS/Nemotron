# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task069_wandb_artifact_lineage_publish -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task069_wandb_artifact_lineage_publish |
| PR | pending push |
| Session | 81 |

正在做：task069 Session 2 — wire `lineage_publisher.publish()` into every
`prepare_*.py` so each bridge auto-publishes after writing manifest.json.
Session 1 (PR #104) shipped the publisher; this PR threads it into every
M0 / M1 prep main().

## What's in this PR

### `lineage_publisher.py` 加 `maybe_publish_lineage_from_manifest` helper

- `_AUTO` sentinel — lazy-resolves `wandb.run` if installed + active;
  None when wandb absent / no run (sandbox-friendly)
- `_resolve_wandb_run(wandb_run)` translates explicit value / `_AUTO`
  to a concrete run or None
- `maybe_publish_lineage_from_manifest(manifest_path, *, file_root,
  wandb_run=_AUTO, upstream_artifact_resolver, artifact_factory)`:
  - Reads manifest.json, extracts lineage block, calls
    `WandbArtifactPublisher.publish`
  - **Failure-tolerant**: any exception (missing manifest, missing
    lineage block, malformed JSON, publisher crash) → returns None
    rather than propagating. Publishing must NEVER fail the underlying
    prep.
  - `artifact_factory` pass-through so tests can inject FakeArtifact
    without requiring wandb on the import path
  - Returns `PublishResult | None`

### Wire into 6 bridges' main()

After each `prepare(args)` succeeds + writes manifest.json, every bridge
now calls:

```python
try:
    from nemotron.recipes.super3.milestones.lineage_publisher import (
        maybe_publish_lineage_from_manifest,
    )
    maybe_publish_lineage_from_manifest(args.output_dir / "manifest.json")
except Exception:
    pass  # Publishing failures must NOT crash prep
```

Wired:
- `m0_data_env/prepare_m0_assets.py` (uses `Path(manifest["output_dir"])`)
- `m1_agentic_sft/prepare_m1_agentic_sft.py`
- `m1_rlvr/prepare_m1_rlvr_jsonl.py`
- `m1_swe1/prepare_m1_swe1_jsonl.py`
- `m1_swe2/prepare_m1_swe2_jsonl.py`
- `m1_rlhf/prepare_m1_rlhf_jsonl.py`

Behavior:
- Sandbox / no wandb installed → no-op (helper returns None)
- Cluster with active wandb.run → real publish (auto-detected via _AUTO)
- Helper itself raises → outer try/except in main() swallows
- Publishing succeeds but log to stdout / stderr left to W&B side

### Tests (`test_lineage_publisher_wiring.py`, 15 cases)

- `maybe_publish_lineage_from_manifest` 6: publishes with run /
  dry-runs without / None on missing manifest / None on missing lineage
  block / None on malformed JSON / swallows publisher exception
- `_AUTO` sentinel 3: wandb not importable → None / picks up active run /
  wandb installed but run is None → None
- Bridge wiring 5: m0 / m1_rlvr / m1_swe1 / m1_swe2 / m1_rlhf each call
  the helper after prep
- Critical safety 1: publisher helper crash does not crash bridge main()
  (exit_code still 0)

(m1_agentic_sft wiring is identical pattern; tested implicitly by the
test_m1_agentic_sft module — though that's collect-errored in sandbox
due to pre-existing pyarrow issue; the wiring lives in the source file.)

Sandbox 测试基线 577 → **592 passed + 7 skipped** (15 new)。

## task069 状态

- Session 1 ✓ (PR #104 / 860e175) — publisher + CLI + test doubles + dry-run
- Session 2 ✓ (this PR) — helper + wired into 6 bridges
- Session 3 ☐ — Cluster verify with real W&B credentials + an actual
  multi-stage pipeline run rendering the chain in W&B

Roadmap §5b 更新：Session 2 done。
