"""Tests for `maybe_publish_lineage_from_manifest` + bridge wiring
(task069 Session 2).

Covers:

- `maybe_publish_lineage_from_manifest` happy path against
  a manifest.json with a lineage block + an injected wandb_run
- Failure-tolerance: missing manifest / missing lineage block /
  malformed JSON / wandb exception → returns None, never raises
- `_AUTO` sentinel: detects active wandb.run when present; falls back
  to None (dry-run) when wandb isn't importable or no run is active
- Every bridge's main() calls the helper after writing its manifest —
  verified by monkeypatching the helper and exercising each bridge
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


from nemotron.recipes.super3.milestones.lineage import (
    LineageInput,
    LineageOutput,
    make_record,
    now_utc_iso,
)
from nemotron.recipes.super3.milestones.lineage_publisher import (
    FakeWandbRun,
    PublishResult,
    _AUTO,
    _resolve_wandb_run,
    maybe_publish_lineage_from_manifest,
)


def _write_manifest_with_lineage(
    tmp_path: Path, *, artifact_name: str = "test-art-v1"
) -> Path:
    """Synthesize a manifest.json with a valid lineage block."""
    manifest_path = tmp_path / "manifest.json"
    record = make_record(
        stage="M0 test",
        produced_by="test_wiring",
        artifact_type="RawDataArtifact",
        artifact_name=artifact_name,
        inputs=[LineageInput(kind="hf_dataset", ref="openai/gsm8k")],
        outputs=[LineageOutput(kind="m0_jsonl", ref="split.jsonl")],
    )
    (tmp_path / "split.jsonl").write_text("row\n", encoding="utf-8")
    manifest_path.write_text(
        json.dumps({"lineage": record.to_jsonable()}), encoding="utf-8"
    )
    return manifest_path


# ---------- maybe_publish_lineage_from_manifest ----------


def test_helper_publishes_when_run_provided(tmp_path: Path) -> None:
    manifest = _write_manifest_with_lineage(tmp_path)
    run = FakeWandbRun()
    # Pass a fake artifact_factory so the helper doesn't try to
    # `import wandb` for `wandb.Artifact` (sandbox doesn't have wandb).
    from nemotron.recipes.super3.milestones.lineage_publisher import FakeArtifact
    result = maybe_publish_lineage_from_manifest(
        manifest,
        wandb_run=run,
        artifact_factory=lambda name, type: FakeArtifact(name=name, type=type),
    )
    assert isinstance(result, PublishResult)
    assert result.dry_run is False
    assert len(run.log_artifact_calls) == 1


def test_helper_dry_runs_when_run_is_none(tmp_path: Path) -> None:
    manifest = _write_manifest_with_lineage(tmp_path)
    result = maybe_publish_lineage_from_manifest(manifest, wandb_run=None)
    assert isinstance(result, PublishResult)
    assert result.dry_run is True


def test_helper_returns_none_when_manifest_missing(tmp_path: Path) -> None:
    """Failure-tolerance: missing manifest must not raise — prep already
    succeeded, publishing should not crash it."""
    result = maybe_publish_lineage_from_manifest(
        tmp_path / "nonexistent.json", wandb_run=None
    )
    assert result is None


def test_helper_returns_none_when_lineage_block_missing(tmp_path: Path) -> None:
    """Manifest exists but has no lineage block (pre-task021 Session 2
    artifact). Helper must no-op cleanly."""
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    result = maybe_publish_lineage_from_manifest(manifest, wandb_run=None)
    assert result is None


def test_helper_returns_none_on_malformed_json(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("not json {", encoding="utf-8")
    result = maybe_publish_lineage_from_manifest(manifest, wandb_run=None)
    assert result is None


def test_helper_swallows_publisher_exception(tmp_path: Path) -> None:
    """If the publisher raises mid-flight (e.g., wandb network failure),
    the helper returns None instead of propagating — the prep already
    succeeded."""
    manifest = _write_manifest_with_lineage(tmp_path)

    class BrokenRun:
        def use_artifact(self, name: str) -> Any:
            raise RuntimeError("network down")

        def log_artifact(self, art: Any) -> None:
            raise RuntimeError("network down")

    # No upstream → use_artifact not called; but log_artifact will raise
    result = maybe_publish_lineage_from_manifest(
        manifest, wandb_run=BrokenRun()
    )
    assert result is None


# ---------- _AUTO sentinel ----------


def test_auto_resolves_to_none_when_wandb_not_importable(monkeypatch) -> None:
    """If wandb isn't installed, _resolve_wandb_run returns None →
    publish dry-runs. Use monkeypatching to simulate."""
    monkeypatch.setitem(sys.modules, "wandb", None)
    result = _resolve_wandb_run(_AUTO)
    assert result is None


def test_auto_picks_up_active_wandb_run(monkeypatch) -> None:
    """Inject a fake wandb module with a `run` attribute; _AUTO must
    return that run."""
    fake_run = FakeWandbRun()
    fake_wandb = SimpleNamespace(run=fake_run)
    monkeypatch.setitem(sys.modules, "wandb", fake_wandb)
    result = _resolve_wandb_run(_AUTO)
    assert result is fake_run


def test_auto_resolves_to_none_when_wandb_run_is_none(monkeypatch) -> None:
    """wandb is installed but no run is active (wandb.run is None)."""
    fake_wandb = SimpleNamespace(run=None)
    monkeypatch.setitem(sys.modules, "wandb", fake_wandb)
    result = _resolve_wandb_run(_AUTO)
    assert result is None


# ---------- Bridge wiring ----------


def test_m0_main_calls_publisher_helper_after_prep(tmp_path: Path, monkeypatch) -> None:
    """task069 Session 2 wiring: prepare_m0_assets.py main() must call
    maybe_publish_lineage_from_manifest after prep succeeds. Verify by
    monkeypatching the helper symbol the bridge imports."""
    calls: list[Path] = []

    def fake_helper(manifest_path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(Path(manifest_path))

    from nemotron.recipes.super3.milestones import lineage_publisher

    monkeypatch.setattr(
        lineage_publisher, "maybe_publish_lineage_from_manifest", fake_helper
    )

    # Build a fake `manifest` return so the m0 main doesn't actually try
    # to download HF.
    fake_manifest = {"output_dir": str(tmp_path), "datasets": ["x"], "errors": []}
    from nemotron.recipes.super3.milestones.m0_data_env import prepare_m0_assets

    monkeypatch.setattr(prepare_m0_assets, "prepare_assets", lambda args: fake_manifest)
    # Stub argparse to swallow command-line args.
    monkeypatch.setattr(
        prepare_m0_assets,
        "build_parser",
        lambda: _DummyParser(SimpleNamespace(output_dir=tmp_path)),
    )

    exit_code = prepare_m0_assets.main([])
    assert exit_code == 0
    assert any(p.name == "manifest.json" for p in calls)


def test_m1_rlvr_main_calls_publisher_helper_after_prep(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    calls: list[Path] = []

    def fake_helper(manifest_path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(Path(manifest_path))

    from nemotron.recipes.super3.milestones import lineage_publisher

    monkeypatch.setattr(
        lineage_publisher, "maybe_publish_lineage_from_manifest", fake_helper
    )

    fake_manifest = {
        "mix": "rlvr1",
        "counts": {"train": {"env_a": 10}, "val": {"env_a": 2}},
        "train_path": str(tmp_path / "train.jsonl"),
        "val_path": str(tmp_path / "val.jsonl"),
        "errors": [],
    }
    from nemotron.recipes.super3.milestones.m1_rlvr import prepare_m1_rlvr_jsonl

    monkeypatch.setattr(prepare_m1_rlvr_jsonl, "prepare", lambda args: fake_manifest)
    monkeypatch.setattr(
        prepare_m1_rlvr_jsonl,
        "build_parser",
        lambda: _DummyParser(SimpleNamespace(output_dir=tmp_path)),
    )

    exit_code = prepare_m1_rlvr_jsonl.main([])
    assert exit_code == 0
    assert any(p.name == "manifest.json" for p in calls)


def test_m1_swe1_main_calls_publisher_helper_after_prep(tmp_path: Path, monkeypatch) -> None:
    calls: list[Path] = []

    def fake_helper(manifest_path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(Path(manifest_path))

    from nemotron.recipes.super3.milestones import lineage_publisher

    monkeypatch.setattr(
        lineage_publisher, "maybe_publish_lineage_from_manifest", fake_helper
    )

    fake_manifest = {
        "mix": "swe1",
        "counts": {"train": {"env_a": 5}, "val": {"env_a": 1}},
        "train_path": str(tmp_path / "train.jsonl"),
        "val_path": str(tmp_path / "val.jsonl"),
        "errors": [],
    }
    from nemotron.recipes.super3.milestones.m1_swe1 import prepare_m1_swe1_jsonl

    monkeypatch.setattr(prepare_m1_swe1_jsonl, "prepare", lambda args: fake_manifest)
    monkeypatch.setattr(
        prepare_m1_swe1_jsonl,
        "build_parser",
        lambda: _DummyParser(SimpleNamespace(output_dir=tmp_path)),
    )

    exit_code = prepare_m1_swe1_jsonl.main([])
    assert exit_code == 0
    assert any(p.name == "manifest.json" for p in calls)


def test_m1_swe2_main_calls_publisher_helper_after_prep(tmp_path: Path, monkeypatch) -> None:
    calls: list[Path] = []

    def fake_helper(manifest_path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(Path(manifest_path))

    from nemotron.recipes.super3.milestones import lineage_publisher

    monkeypatch.setattr(
        lineage_publisher, "maybe_publish_lineage_from_manifest", fake_helper
    )

    fake_manifest = {
        "mix": "swe2",
        "counts": {"train": {"env_a": 5}, "val": {"env_a": 1}},
        "train_path": str(tmp_path / "train.jsonl"),
        "val_path": str(tmp_path / "val.jsonl"),
        "errors": [],
    }
    from nemotron.recipes.super3.milestones.m1_swe2 import prepare_m1_swe2_jsonl

    monkeypatch.setattr(prepare_m1_swe2_jsonl, "prepare", lambda args: fake_manifest)
    monkeypatch.setattr(
        prepare_m1_swe2_jsonl,
        "build_parser",
        lambda: _DummyParser(SimpleNamespace(output_dir=tmp_path)),
    )

    exit_code = prepare_m1_swe2_jsonl.main([])
    assert exit_code == 0
    assert any(p.name == "manifest.json" for p in calls)


def test_m1_rlhf_main_calls_publisher_helper_after_prep(tmp_path: Path, monkeypatch) -> None:
    calls: list[Path] = []

    def fake_helper(manifest_path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(Path(manifest_path))

    from nemotron.recipes.super3.milestones import lineage_publisher

    monkeypatch.setattr(
        lineage_publisher, "maybe_publish_lineage_from_manifest", fake_helper
    )

    fake_manifest = {
        "mix": "rlhf",
        "counts": {"train": {"env_a": 5}, "val": {"env_a": 1}},
        "train_path": str(tmp_path / "train.jsonl"),
        "val_path": str(tmp_path / "val.jsonl"),
        "errors": [],
    }
    from nemotron.recipes.super3.milestones.m1_rlhf import prepare_m1_rlhf_jsonl

    monkeypatch.setattr(prepare_m1_rlhf_jsonl, "prepare", lambda args: fake_manifest)
    monkeypatch.setattr(
        prepare_m1_rlhf_jsonl,
        "build_parser",
        lambda: _DummyParser(SimpleNamespace(output_dir=tmp_path)),
    )

    exit_code = prepare_m1_rlhf_jsonl.main([])
    assert exit_code == 0
    assert any(p.name == "manifest.json" for p in calls)


def test_publisher_helper_failure_does_not_crash_bridge_main(
    tmp_path: Path, monkeypatch
) -> None:
    """Critical safety property: even if the publisher helper raises
    UNEXPECTEDLY (e.g., import error from a future bug), the bridge's
    main() must still return 0 — prep succeeded; publishing is best-
    effort."""
    def broken_helper(manifest_path, **kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("simulated publisher implosion")

    from nemotron.recipes.super3.milestones import lineage_publisher

    monkeypatch.setattr(
        lineage_publisher, "maybe_publish_lineage_from_manifest", broken_helper
    )

    fake_manifest = {
        "mix": "rlvr1",
        "counts": {"train": {"x": 1}, "val": {"x": 0}},
        "train_path": str(tmp_path / "train.jsonl"),
        "val_path": str(tmp_path / "val.jsonl"),
        "errors": [],
    }
    from nemotron.recipes.super3.milestones.m1_rlvr import prepare_m1_rlvr_jsonl

    monkeypatch.setattr(prepare_m1_rlvr_jsonl, "prepare", lambda args: fake_manifest)
    monkeypatch.setattr(
        prepare_m1_rlvr_jsonl,
        "build_parser",
        lambda: _DummyParser(SimpleNamespace(output_dir=tmp_path)),
    )

    exit_code = prepare_m1_rlvr_jsonl.main([])
    assert exit_code == 0  # bridge still succeeds despite publisher crash


# ---------- Test helpers ----------


class _DummyParser:
    """Minimal argparse stand-in that returns a preset namespace."""

    def __init__(self, namespace: SimpleNamespace) -> None:
        self._ns = namespace

    def parse_args(self, _argv: Any = None) -> SimpleNamespace:  # noqa: ANN401
        return self._ns
