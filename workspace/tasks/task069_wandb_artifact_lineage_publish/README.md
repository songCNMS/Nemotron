# task069_wandb_artifact_lineage_publish

<!-- METADATA:STATUS=Todo,ASSIGNEE=unassigned -->

## 背景

Plan §10 M1 infra explicitly lists:

> - W&B/artifact lineage for raw data, prepared data, model checkpoints,
>   and eval reports.

task021_m1_infra_minimum covers the **schema side** of lineage (Session 2
landed `LineageRecord` / `LineageInput` / `LineageOutput` dataclasses
with the plan §10 artifact-type vocabulary baked in as module
constants), but the **runtime publish side** — actually emitting these
records to W&B as `wandb.Artifact` rows with the proper `produced_by`
relationships — was deferred. Today every M0 / M1 bridge writes a
`manifest.json` with a `lineage` block, but those blocks are local-only;
nothing pushes them up where the operator's W&B board can render the
chain.

This task is the formal owner of the publish side, so the deferral has
a tracked home instead of being a footnote in task021's README.

## 范围

Wire the existing `lineage.py` `LineageRecord` output into W&B as a
structured artifact lineage:

```
RawDataArtifact (M0 HF source)
   → SFTDataArtifact (M0 prep output)
   → ModelArtifact-sft (after SFT training)
   → RLVR{1,2,3}DataArtifact / SWE{1,2}DataArtifact / RLHFDataArtifact (bridges)
   → ModelArtifact-rlvr{1,2,3} / -swe{1,2} / -rlhf (after each RL stage)
   → EvalReport (after promotion gate run)
```

Each link is a `wandb.Artifact` with `use_artifact()` / `log_artifact()`
calls keyed on the artifact-type vocabulary already declared in
`lineage.py`.

## 整 task 拆 Sessions

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | `lineage_publisher.py` module — pure Python interface that takes a `LineageRecord` and emits the `wandb.Artifact` calls; injectable W&B client so unit tests use a fake | yes | Todo |
| 2 | Wire `lineage_publisher.publish()` into every `prepare_*.py` (M0 / SFT / RLVR / SWE1 / SWE2 / RLHF / eval) so each bridge auto-publishes after writing manifest.json | partial (interface yes, real W&B yes-but-mocked) | Todo |
| 3 | Cluster verify: real W&B run logs the full chain M0 → SFT → RL → Eval against an actual checkpoint | no — needs NemTron cluster + W&B credentials + real run | Todo |

## Session 1 目标

Standalone publisher module that the existing bridges can call without
deep integration:

1. **`m1_infra/lineage_publisher.py`** new module:
   - `WandbArtifactPublisher` class with `__init__(wandb_run=None)` —
     accepts an injected W&B run object (or `None` for dry-run mode)
   - `publish(record: LineageRecord) -> None` — translates the record
     into `wandb.Artifact(name, type=record.artifact_type)` +
     `add_file()` for each output + `use_artifact()` for each input
   - `FakeWandbRun` test double that captures `log_artifact` /
     `use_artifact` calls in a list for assertions
   - Dry-run mode (no `wandb_run` provided) is a no-op — sandbox can
     import + call publish without raising
2. **CLI entrypoint** `scripts/publish_lineage.py` — reads a
   manifest.json, extracts lineage block, calls publisher; useful for
   backfilling lineage for runs that pre-dated this task
3. **Tests** (≥ 12): publish creates expected Artifact calls, use vs log
   distinction, dry-run is no-op, FakeWandbRun captures, CLI roundtrip
   from manifest.json

## Session 1 验收

- [ ] `lineage_publisher.py` 新模块 + `WandbArtifactPublisher` class +
  `FakeWandbRun` test double + dry-run mode
- [ ] `scripts/publish_lineage.py` reads manifest.json + publishes
- [ ] ≥ 12 个 pytest case (no real W&B import needed in sandbox; use
  `pytest.importorskip("wandb")` for any test that needs the real
  module; otherwise mock)
- [ ] Roadmap §1.8 task021 entry references task069 as Session 7

## 依赖

- task021 Session 2 (lineage schema ✓) — already landed
- task021 Session 5+ (other Sessions) — already landed
- Sessions 2-3 依赖每个 bridge module 还在原位 (task014/015/016/017/018
  各自 prepare_*.py)
- Session 3 依赖 NemTron cluster + W&B credentials

## 参考文件

- `src/nemotron/recipes/super3/milestones/lineage.py` — schema + artifact-type vocabulary
- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py` — first publish target
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` — second publish target
- `src/nemotron/recipes/super3/milestones/m1_*/prepare_m1_*_jsonl.py` — four RL-stage publish targets
- plan §10 + roadmap §1.8 task021

## 不在本 task

- Real W&B run management (one-run-per-stage vs grouped-runs) — operator
  decides at launch time
- Artifact garbage collection / retention policy — W&B-side ops
- Cross-org W&B sharing — out of scope; per-team W&B project setup
