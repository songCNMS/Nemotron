"""Path guard tests for benchmark alignment source manifests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m1_eval_basket import (  # noqa: E402
    benchmark_alignment,
)
from nemotron.recipes.super3.milestones.m1_eval_basket.benchmark_alignment import (  # noqa: E402
    BENCHMARK_ALIGNMENT_LEDGER_PATH,
    validate_benchmark_alignment_ledger,
)


def _alignment_ledger_data() -> dict:
    return yaml.safe_load(BENCHMARK_ALIGNMENT_LEDGER_PATH.read_text(encoding="utf-8"))


def test_production_ledger_source_manifests_validate() -> None:
    assert validate_benchmark_alignment_ledger(_alignment_ledger_data()) == []


def test_repo_relative_source_manifest_file_is_accepted() -> None:
    issues = benchmark_alignment._validate_repo_relative_existing_paths(
        [
            "src/nemotron/recipes/super3/milestones/m1_eval_basket/"
            "qwen_benchmark_alignment_ledger.yaml"
        ],
        context="source_manifests",
    )

    assert issues == []


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/../pyproject.toml", "must not contain traversal components"),
        ("./pyproject.toml", "must use normal repo-relative path components"),
        ("src//nemotron", "must use normal repo-relative path components"),
        (".", "must use normal repo-relative path components"),
        ("", "must use normal repo-relative path components"),
    ],
)
def test_repo_relative_source_manifest_rejects_bad_components(
    path: str,
    expected: str,
) -> None:
    issues = benchmark_alignment._validate_repo_relative_existing_paths(
        [path],
        context="source_manifests",
    )

    assert any(expected in issue for issue in issues), issues


def test_repo_relative_source_manifest_rejects_symlink_escape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "repo"
    outside = tmp_path / "outside"
    repo_root.mkdir()
    outside.mkdir()
    outside_file = outside / "manifest.yaml"
    outside_file.write_text("manifest: outside\n", encoding="utf-8")
    symlink = repo_root / "escape.yaml"
    try:
        symlink.symlink_to(outside_file)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    monkeypatch.setattr(benchmark_alignment, "REPO_ROOT", repo_root)

    issues = benchmark_alignment._validate_repo_relative_existing_paths(
        ["escape.yaml"],
        context="source_manifests",
    )

    assert any("must stay under repo root" in issue for issue in issues), issues


def test_repo_relative_source_manifest_rejects_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / "manifests").mkdir(parents=True)
    monkeypatch.setattr(benchmark_alignment, "REPO_ROOT", repo_root)

    issues = benchmark_alignment._validate_repo_relative_existing_paths(
        ["manifests"],
        context="source_manifests",
    )

    assert any("repo-relative path must be a file" in issue for issue in issues), issues


def test_benchmark_alignment_ledger_surfaces_bad_evidence_source_manifests() -> None:
    data = deepcopy(_alignment_ledger_data())
    data["evidence_records"][0]["source_manifests"] = ["../escape.yaml"]

    issues = validate_benchmark_alignment_ledger(data)

    assert any(
        "evidence_records[0].source_manifests" in issue
        and "must not contain traversal components" in issue
        for issue in issues
    ), issues


def test_benchmark_alignment_rejects_directory_local_raw_artifacts(
    tmp_path: Path,
) -> None:
    data = deepcopy(_alignment_ledger_data())
    artifact_dir = tmp_path / "raw_artifact_dir"
    artifact_dir.mkdir()
    record = data["evidence_records"][0]
    record["raw_artifact_paths"] = [str(artifact_dir)]
    record["raw_artifact_sha256"] = {str(artifact_dir): "a" * 64}

    issues = validate_benchmark_alignment_ledger(data)

    assert any(
        "raw_artifact_paths local path must be a regular file" in issue
        for issue in issues
    ), issues
