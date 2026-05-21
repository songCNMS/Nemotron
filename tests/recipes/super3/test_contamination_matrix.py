"""Tests for the task035 contamination/eval-overlap matrix scaffold."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.data_registries.contamination_matrix import (  # noqa: E402
    build_eval_overlap_matrix,
    format_eval_overlap_matrix,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_data_registries.py"


def _write_matrix_fixture(tmp_path: Path) -> Path:
    data_reg = tmp_path / "data_registry.yaml"
    data_reg.write_text(
        """schema_version: 1
milestone: M0
datasets:
  - id: stub_clean
    environment: stub_env
    domain: stub
    hf_dataset: stub/clean
    hf_split: train
    hf_revision: deadbeef
    license: apache-2.0
    contamination_against: ["StubEval dev", "held-out prompt basket"]
    converter: stub
    use_stage: ["M0 data_env_foundation"]
  - id: stub_placeholder
    environment: stub_env
    domain: stub
    hf_dataset: stub/placeholder
    hf_split: train
    hf_revision: deadbeef
    license: apache-2.0
    contamination_against: ["TBD"]
    converter: stub
    use_stage: ["M0 data_env_foundation"]
  - id: stub_blocker
    environment: other_env
    domain: stub
    hf_dataset: stub/blocker
    hf_split: train
    hf_revision: deadbeef
    license: apache-2.0
    contamination_against: []
    converter: stub
    use_stage: ["M0 data_env_foundation"]
""",
        encoding="utf-8",
    )
    env_reg = tmp_path / "environment_registry.yaml"
    env_reg.write_text(
        """schema_version: 1
milestone: M0
environments:
  - id: stub_env
    family: stub_family
    stage: M0 data_env_foundation
    input_schema: nemo_gym_jsonl
    reward: {verifier: stub_reward, range: [0, 1]}
    telemetry: [reward]
    health_check: {min_rows_per_split: 1}
  - id: other_env
    family: other_family
    stage: M0 data_env_foundation
    input_schema: nemo_gym_jsonl
    reward: {verifier: other_reward, range: [0, 1]}
    telemetry: [reward]
    health_check: {min_rows_per_split: 1}
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: stub_m0_data
    kind: m0_data_registry
    path: {data_reg.name}
    summary: stub
  - id: stub_m0_env
    kind: m0_environment_registry
    path: {env_reg.name}
    summary: stub
""",
        encoding="utf-8",
    )
    return index


def _run_script(*extra_args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_build_eval_overlap_matrix_groups_rows_by_environment(tmp_path: Path) -> None:
    index = _write_matrix_fixture(tmp_path)

    matrix = build_eval_overlap_matrix(index)

    assert matrix["row_count"] == 3
    assert matrix["counts"] == {"clean": 1, "informational": 1, "blocker": 1}
    envs = {env["environment"]: env for env in matrix["environments"]}
    assert envs["stub_env"]["family"] == "stub_family"
    assert envs["stub_env"]["posture"] == "informational"
    assert envs["other_env"]["posture"] == "blocker"

    clean_row = next(
        row for row in envs["stub_env"]["datasets"] if row["row_id"] == "stub_clean"
    )
    assert clean_row["eval_overlap_targets"] == [
        "StubEval dev",
        "held-out prompt basket",
    ]
    assert clean_row["posture"] == "clean"


def test_format_eval_overlap_matrix_shows_targets_and_posture(tmp_path: Path) -> None:
    matrix = build_eval_overlap_matrix(_write_matrix_fixture(tmp_path))

    text = format_eval_overlap_matrix(matrix)

    assert "eval-overlap matrix" in text
    assert "stub_clean [clean]" in text
    assert "StubEval dev; held-out prompt basket" in text
    assert "stub_placeholder [informational]" in text
    assert "stub_blocker [blocker]" in text
    assert "contamination_against is empty" in text


def test_live_eval_overlap_matrix_has_no_blockers() -> None:
    matrix = build_eval_overlap_matrix()
    assert matrix["row_count"] > 0
    assert matrix["counts"]["blocker"] == 0
    assert {env["posture"] for env in matrix["environments"]} <= {
        "clean",
        "informational",
    }


def test_eval_overlap_matrix_cli_clean_main_exits_zero() -> None:
    result = _run_script("--eval-overlap-matrix")
    assert result.returncode == 0, result.stderr
    assert "eval-overlap matrix" in result.stdout
    assert "0 blocker" in result.stdout
    assert result.stderr == ""


def test_eval_overlap_matrix_cli_with_broken_index_exits_one(tmp_path: Path) -> None:
    index = _write_matrix_fixture(tmp_path)

    result = _run_script("--eval-overlap-matrix", "--index-path", str(index))

    assert result.returncode == 1
    assert "stub_blocker [blocker]" in result.stdout
    assert "1 broken contamination_against field" in result.stderr
