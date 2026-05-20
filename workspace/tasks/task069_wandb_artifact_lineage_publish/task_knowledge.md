# task069 - task_knowledge

## Why a separate publisher module rather than inline calls

If every `prepare_*.py` does its own `wandb.log_artifact()` directly,
five copies of the same idea drift over time. Centralising into
`lineage_publisher.WandbArtifactPublisher`:

1. Single place to thread the W&B run object
2. Single place to map `LineageRecord` → `wandb.Artifact` shape
3. Single place to handle dry-run / sandbox mode (no W&B import needed)
4. Single place to add cross-cutting concerns later (retry, retention,
   PII scrubbing)

The pattern mirrors `_bridge_base.py` (task017 Session 4): each bridge
imports a shared helper instead of duplicating logic.

## Injectable W&B run

```python
class WandbArtifactPublisher:
    def __init__(self, wandb_run=None):
        self.wandb_run = wandb_run  # None → dry-run

    def publish(self, record: LineageRecord) -> None:
        if self.wandb_run is None:
            return
        artifact = wandb.Artifact(
            name=record.artifact_name,
            type=record.artifact_type,
        )
        for output in record.outputs:
            artifact.add_file(output.ref)
        for input_ in record.inputs:
            upstream = self.wandb_run.use_artifact(input_.ref)
            artifact.metadata["upstream_" + input_.kind] = upstream.name
        self.wandb_run.log_artifact(artifact)
```

For tests, inject `FakeWandbRun` capturing the calls in a list for
assertions — no real W&B import, no credentials.

## Artifact-type vocabulary already defined

From `lineage.py`:
- `RawDataArtifact` — M0 HF source manifest
- `SFTDataArtifact` — M0 prep output / Agentic SFT data
- `ModelArtifact-sft` — SFT checkpoint
- `RLVR1_ARTIFACT` / `RLVR2_ARTIFACT` / `RLVR3_ARTIFACT` — per-mix RLVR data
- `SWE1_ARTIFACT` / `SWE2_ARTIFACT` — per-stage SWE data
- `RLHF_ARTIFACT` — RLHF data
- `EvalReport` — eval basket output

These are MODULE CONSTANTS in `lineage.py`; the publisher reads them as
literal type strings.

## Backfill path

Session 1 ships `scripts/publish_lineage.py` that takes a path to a
manifest.json and publishes its lineage block. Operators can backfill
prior runs without re-running training:

```bash
python scripts/publish_lineage.py output/super3/m0/manifest.json
python scripts/publish_lineage.py output/super3/m1_rlvr/rlvr1/manifest.json
```

The CLI tool exits 0 in dry-run mode (no W&B credentials) — useful for
CI.

## Decision: tasks not in this scope

- **Run grouping** — whether one W&B run spans the entire M0 → SFT → RL
  → Eval pipeline, or each stage gets its own run, is an operator
  decision at launch time. The publisher accepts whatever run object
  is passed.
- **Retention policy** — W&B-side org config; not Nemotron code.
- **PII scrubbing** — assume training data is already scrubbed
  upstream; the lineage records reference paths not contents.

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` pyarrow ImportError —
pre-existing; run sandbox tests with `--ignore` flag.
