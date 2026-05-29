"""Tests for the W&B artifact lineage publisher (task069 Session 1).

Covers:

- ``WandbArtifactPublisher.publish`` happy path against a FakeWandbRun:
  log_artifact called, use_artifact called for resolvable inputs,
  output files attached
- Dry-run mode (no wandb_run) returns a PublishResult but does not
  call W&B
- ``default_upstream_resolver`` for ``manifest`` / ``checkpoint`` /
  ``hf_dataset`` / unknown kinds
- Output file resolution: ``file_root`` joining, absolute paths, missing
  files surfaced in ``outputs_missing``
- Custom resolver injection
- Test doubles: ``FakeWandbRun`` captures both methods in order;
  ``FakeArtifact`` captures add_file + metadata
- CLI: scripts/publish_lineage.py dry-run roundtrip from a manifest.json
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from nemotron.recipes.super3.milestones.lineage import (
    LineageInput,
    LineageOutput,
    LineageRecord,
    make_record,
    now_utc_iso,
)
from nemotron.recipes.super3.milestones.lineage_publisher import (
    FakeArtifact,
    FakeWandbRun,
    PublishResult,
    WandbArtifactPublisher,
    default_upstream_resolver,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
PUBLISH_SCRIPT = REPO_ROOT / "scripts" / "publish_lineage.py"


def _toy_record(
    *,
    artifact_name: str = "toy-output",
    artifact_type: str = "SFTDataArtifact",
    inputs: list[LineageInput] | None = None,
    outputs: list[LineageOutput] | None = None,
) -> LineageRecord:
    return make_record(
        stage="M0 toy",
        produced_by="test_lineage_publisher.py",
        artifact_type=artifact_type,
        artifact_name=artifact_name,
        inputs=inputs or [],
        outputs=outputs or [],
    )


def _toy_artifact_factory(name: str, type: str) -> FakeArtifact:
    return FakeArtifact(name=name, type=type)


# ---------- Dry-run mode ----------


def test_dry_run_returns_publish_result_without_calling_wandb() -> None:
    """publish in dry-run mode (no wandb_run) must NOT raise and must
    return a PublishResult describing what would happen — useful for CI
    and planning passes that don't have W&B credentials."""
    publisher = WandbArtifactPublisher(wandb_run=None)
    record = _toy_record(
        outputs=[LineageOutput(kind="m0_data_jsonl", ref="train.jsonl")]
    )
    result = publisher.publish(record, file_root=None)
    assert isinstance(result, PublishResult)
    assert result.dry_run is True
    assert result.artifact_name == "toy-output"
    assert result.artifact_type == "SFTDataArtifact"


def test_dry_run_still_resolves_upstream_and_outputs(tmp_path: Path) -> None:
    """Dry-run reports what *would* be published; that includes upstream
    resolution and output-file presence so the operator can verify the
    plan before flipping to live mode."""
    output = tmp_path / "data.jsonl"
    output.write_text("row\n", encoding="utf-8")
    record = _toy_record(
        inputs=[LineageInput(kind="hf_dataset", ref="openai/gsm8k")],
        outputs=[LineageOutput(kind="m0_data_jsonl", ref=output.name)],
    )
    publisher = WandbArtifactPublisher(wandb_run=None)
    result = publisher.publish(record, file_root=tmp_path)
    assert result.outputs_attached == [str(output)]
    # hf_dataset input is unresolvable via default resolver — surfaces
    # in upstream_unresolved
    assert any("hf_dataset" in r for r in result.upstream_unresolved)


# ---------- Live mode against FakeWandbRun ----------


def test_publish_logs_artifact_against_fake_wandb_run(tmp_path: Path) -> None:
    output = tmp_path / "split.jsonl"
    output.write_text("row\n", encoding="utf-8")
    record = _toy_record(
        outputs=[LineageOutput(kind="m0_data_jsonl", ref=output.name)]
    )
    run = FakeWandbRun()
    publisher = WandbArtifactPublisher(
        wandb_run=run, artifact_factory=_toy_artifact_factory
    )
    result = publisher.publish(record, file_root=tmp_path)
    assert result.dry_run is False
    assert len(run.log_artifact_calls) == 1
    artifact = run.log_artifact_calls[0]
    assert artifact.name == "toy-output"
    assert artifact.type == "SFTDataArtifact"
    assert str(output) in artifact.files


def test_publish_calls_use_artifact_for_resolvable_manifest_input(
    tmp_path: Path,
) -> None:
    """A LineageInput of kind=manifest pointing at a real manifest with
    a lineage block resolves to ``<artifact_name>:latest``."""
    # Set up upstream manifest with its own lineage block
    upstream_manifest = tmp_path / "upstream_manifest.json"
    upstream_manifest.write_text(
        json.dumps(
            {
                "lineage": {
                    "schema_version": 1,
                    "stage": "M0",
                    "produced_by": "test",
                    "produced_at_utc": now_utc_iso(),
                    "artifact_type": "RawDataArtifact",
                    "artifact_name": "m0_raw_v1",
                    "inputs": [],
                    "outputs": [],
                }
            }
        ),
        encoding="utf-8",
    )

    record = _toy_record(
        inputs=[LineageInput(kind="manifest", ref=str(upstream_manifest))]
    )
    run = FakeWandbRun()
    publisher = WandbArtifactPublisher(
        wandb_run=run, artifact_factory=_toy_artifact_factory
    )
    result = publisher.publish(record)
    assert "m0_raw_v1:latest" in run.use_artifact_calls
    assert "m0_raw_v1:latest" in result.upstream_resolved


def test_publish_skips_use_artifact_for_unresolvable_inputs(tmp_path: Path) -> None:
    """hf_dataset and bogus manifest inputs DON'T trigger use_artifact;
    they show up in upstream_unresolved instead."""
    record = _toy_record(
        inputs=[
            LineageInput(kind="hf_dataset", ref="openai/gsm8k"),
            LineageInput(kind="manifest", ref="/nonexistent/manifest.json"),
            LineageInput(kind="something_weird", ref="x"),
        ]
    )
    run = FakeWandbRun()
    publisher = WandbArtifactPublisher(
        wandb_run=run, artifact_factory=_toy_artifact_factory
    )
    result = publisher.publish(record)
    assert run.use_artifact_calls == []
    assert len(result.upstream_unresolved) == 3


def test_publish_attaches_each_output_file_to_artifact(tmp_path: Path) -> None:
    """A record with 3 outputs results in 3 add_file calls on the
    artifact."""
    files = []
    for i in range(3):
        path = tmp_path / f"shard_{i}.jsonl"
        path.write_text(f"row{i}\n", encoding="utf-8")
        files.append(path.name)
    record = _toy_record(
        outputs=[LineageOutput(kind="shard", ref=f) for f in files]
    )
    run = FakeWandbRun()
    publisher = WandbArtifactPublisher(
        wandb_run=run, artifact_factory=_toy_artifact_factory
    )
    publisher.publish(record, file_root=tmp_path)
    artifact = run.log_artifact_calls[0]
    assert len(artifact.files) == 3


def test_publish_surfaces_outputs_missing_on_disk(tmp_path: Path) -> None:
    """Output file declared in lineage but missing on disk: lands in
    `outputs_missing`. Useful for catching a manifest that drifted from
    its on-disk artifacts."""
    record = _toy_record(
        outputs=[
            LineageOutput(kind="missing", ref="not_there.jsonl"),
            LineageOutput(kind="present", ref="here.jsonl"),
        ]
    )
    (tmp_path / "here.jsonl").write_text("row\n", encoding="utf-8")
    publisher = WandbArtifactPublisher(wandb_run=None)
    result = publisher.publish(record, file_root=tmp_path)
    assert any("not_there.jsonl" in p for p in result.outputs_missing)
    assert any("here.jsonl" in p for p in result.outputs_attached)


def test_absolute_output_paths_used_as_is(tmp_path: Path) -> None:
    """If LineageOutput.ref is absolute, file_root is ignored — the
    publisher uses the path directly. Some bridges emit absolute paths
    (e.g., when writing to a shared lustre path)."""
    abs_output = tmp_path / "absolute.jsonl"
    abs_output.write_text("row\n", encoding="utf-8")
    record = _toy_record(
        outputs=[LineageOutput(kind="abs", ref=str(abs_output))]
    )
    publisher = WandbArtifactPublisher(wandb_run=None)
    # file_root deliberately different — should not affect resolution
    result = publisher.publish(record, file_root=tmp_path / "different")
    assert result.outputs_attached == [str(abs_output)]


# ---------- default_upstream_resolver ----------


def test_default_resolver_handles_manifest_input(tmp_path: Path) -> None:
    manifest = tmp_path / "m.json"
    manifest.write_text(
        json.dumps(
            {
                "lineage": {
                    "schema_version": 1,
                    "stage": "M0",
                    "produced_by": "test",
                    "produced_at_utc": now_utc_iso(),
                    "artifact_type": "RawDataArtifact",
                    "artifact_name": "upstream_v2",
                    "inputs": [],
                    "outputs": [],
                }
            }
        ),
        encoding="utf-8",
    )
    inp = LineageInput(kind="manifest", ref=str(manifest))
    assert default_upstream_resolver(inp) == "upstream_v2:latest"


def test_default_resolver_returns_none_for_missing_manifest() -> None:
    inp = LineageInput(kind="manifest", ref="/nonexistent")
    assert default_upstream_resolver(inp) is None


def test_default_resolver_returns_none_for_hf_dataset() -> None:
    """External HF doesn't have a W&B artifact equivalent — None is
    correct. The lineage record still records the reference."""
    inp = LineageInput(kind="hf_dataset", ref="openai/gsm8k")
    assert default_upstream_resolver(inp) is None


def test_default_resolver_handles_checkpoint_input() -> None:
    """checkpoint input → `<basename>:latest` heuristic."""
    inp = LineageInput(kind="checkpoint", ref="/path/to/super3-sft-stage-a-model")
    assert default_upstream_resolver(inp) == "super3-sft-stage-a-model:latest"


# ---------- Custom resolver ----------


def test_custom_resolver_overrides_default(tmp_path: Path) -> None:
    """Operators with stricter naming conventions can inject a custom
    resolver that wins over the default."""
    record = _toy_record(
        inputs=[LineageInput(kind="hf_dataset", ref="openai/gsm8k")]
    )
    run = FakeWandbRun()
    publisher = WandbArtifactPublisher(
        wandb_run=run, artifact_factory=_toy_artifact_factory
    )

    def custom(inp: LineageInput) -> str | None:
        return f"custom-{inp.kind}-{inp.ref.replace('/', '_')}:v1"

    result = publisher.publish(record, upstream_artifact_resolver=custom)
    assert "custom-hf_dataset-openai_gsm8k:v1" in run.use_artifact_calls
    assert "custom-hf_dataset-openai_gsm8k:v1" in result.upstream_resolved


# ---------- Test double surface ----------


def test_fake_artifact_captures_add_file_calls() -> None:
    artifact = FakeArtifact(name="x", type="t")
    artifact.add_file("/a/b/c.txt")
    artifact.add_file("/d/e/f.txt")
    assert artifact.files == ["/a/b/c.txt", "/d/e/f.txt"]


def test_fake_wandb_run_captures_calls_in_order(tmp_path: Path) -> None:
    """The order of use_artifact / log_artifact in the captures matches
    the order they were called — required for assertions about
    use-before-log semantics."""
    run = FakeWandbRun()
    run.use_artifact("a:v1")
    run.use_artifact("b:v2")
    art = FakeArtifact(name="out", type="OutputType")
    run.log_artifact(art)
    assert run.use_artifact_calls == ["a:v1", "b:v2"]
    assert len(run.log_artifact_calls) == 1


# ---------- CLI roundtrip ----------


def test_cli_dry_run_roundtrip_from_manifest_json(tmp_path: Path) -> None:
    """`scripts/publish_lineage.py manifest.json --dry-run` reads the
    manifest, extracts the lineage block, and prints the publish plan.
    Exit 0 even without W&B credentials."""
    manifest_path = tmp_path / "manifest.json"
    output = tmp_path / "split.jsonl"
    output.write_text("row\n", encoding="utf-8")
    manifest_path.write_text(
        json.dumps(
            {
                "lineage": {
                    "schema_version": 1,
                    "stage": "M0",
                    "produced_by": "test_cli",
                    "produced_at_utc": now_utc_iso(),
                    "artifact_type": "RawDataArtifact",
                    "artifact_name": "cli-test-v1",
                    "inputs": [
                        {"kind": "hf_dataset", "ref": "openai/gsm8k"}
                    ],
                    "outputs": [
                        {"kind": "m0_data_jsonl", "ref": output.name}
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(PUBLISH_SCRIPT), str(manifest_path), "--dry-run"],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr}\nstdout: {proc.stdout}"
    assert "(dry-run)" in proc.stdout
    assert "cli-test-v1" in proc.stdout
    assert "RawDataArtifact" in proc.stdout
    assert "split.jsonl" in proc.stdout


def test_cli_exits_1_on_missing_manifest(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(PUBLISH_SCRIPT),
            str(tmp_path / "nonexistent.json"),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 1
    assert "manifest not found" in proc.stderr


def test_cli_exits_2_on_missing_lineage_block(tmp_path: Path) -> None:
    """Manifest exists but lacks a `lineage` block — e.g., pre-task021
    Session 2 artifacts. Exit 2 with a clear error."""
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(PUBLISH_SCRIPT), str(manifest), "--dry-run"],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 2
    assert "lineage block" in proc.stderr
