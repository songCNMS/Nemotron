"""Tests for the RLVR1 smoke wiring (task014 Session 2).

Covers:

- Bridge emits a ``combined.jsonl`` whose contents are concat(train,
  val) — val rows last so the consumer's ``val_holdout`` re-split lands
  on the same boundary
- ``combined.jsonl`` appears in the bridge manifest + lineage outputs
- RLVR1/RLVR2/RLVR3 data-prep defaults load, no longer reference
  NVIDIA-internal /lustre paths, and point at templated bridge outputs
- ``stage1_rlvr/config/smoke.yaml`` loads + structurally smaller
  resource footprint than ``small.yaml`` (the next-up production tier)
- ``smoke.yaml`` inherits ``default.yaml`` like its production siblings
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m1_rlvr.prepare_m1_rlvr_jsonl import (  # noqa: E402
    RLVR1_ENV_MAP,
    prepare,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PREP_CONFIG_DIR = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/data_prep"
)
DATA_PREP_CONFIG_PATHS = {
    mix: DATA_PREP_CONFIG_DIR / f"{mix}.yaml"
    for mix in ("rlvr1", "rlvr2", "rlvr3")
}
SMOKE_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/smoke.yaml"
)
SMALL_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/small.yaml"
)


def _m0_record(env: str, question: str, expected: str) -> dict:
    return {
        "environment": env,
        "milestone": "M0",
        "use_stage": ["M0 data_env_foundation"],
        "question": question,
        "expected_answer": expected,
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": question},
            ],
            "tools": [],
        },
        "reward_config": {"verifier": "stub", "max_score": 1.0},
        "extra_env_info": {},
        "metadata": {
            "source_dataset": "stub-dataset",
            "license": "mit",
            "data_stage": "M0",
        },
    }


def _build_m0_dir(tmp_path: Path) -> Path:
    """Lay out a minimal M0 dir with rows for every rlvr1 mix env."""
    root = tmp_path / "m0"
    root.mkdir()
    for env in RLVR1_ENV_MAP:
        env_dir = root / env
        env_dir.mkdir()
        train_rows = [_m0_record(env, f"train q{i}", f"a{i}") for i in range(3)]
        val_rows = [_m0_record(env, f"val q{i}", f"a{i}") for i in range(2)]
        (env_dir / "train-split.jsonl").write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in train_rows) + "\n",
            encoding="utf-8",
        )
        (env_dir / "val-split.jsonl").write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in val_rows) + "\n",
            encoding="utf-8",
        )
    (root / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "milestone": "M0"}), encoding="utf-8"
    )
    return root


def _args(m0_root: Path, out_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(
        m0_input_dir=m0_root,
        output_dir=out_dir,
        mix="rlvr1",
        max_records_per_env=None,
        max_val_records_per_env=None,
    )


def _load_data_prep_config(mix: str) -> dict:
    path = DATA_PREP_CONFIG_PATHS[mix]
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path}: top-level YAML must be a mapping"
    return data


# ---------- Bridge writes combined.jsonl ----------


def test_bridge_writes_combined_jsonl_alongside_train_and_val(tmp_path: Path) -> None:
    m0_root = _build_m0_dir(tmp_path)
    out_dir = tmp_path / "rlvr1_out"
    prepare(_args(m0_root, out_dir))
    combined_path = out_dir / "combined.jsonl"
    assert combined_path.is_file()


def test_combined_jsonl_equals_train_plus_val_with_val_at_end(tmp_path: Path) -> None:
    """The consumer (``stage2_rl/_data_prep_base.split_local_jsonl``)
    holds out the last ``val_holdout`` rows as val. For the re-split to
    be idempotent with the bridge's split, val rows must come last in
    ``combined.jsonl``."""
    m0_root = _build_m0_dir(tmp_path)
    out_dir = tmp_path / "rlvr1_out"
    prepare(_args(m0_root, out_dir))

    train_rows = [
        json.loads(line)
        for line in (out_dir / "train.jsonl").read_text().splitlines()
        if line
    ]
    val_rows = [
        json.loads(line)
        for line in (out_dir / "val.jsonl").read_text().splitlines()
        if line
    ]
    combined_rows = [
        json.loads(line)
        for line in (out_dir / "combined.jsonl").read_text().splitlines()
        if line
    ]
    assert combined_rows == [*train_rows, *val_rows]
    # Last N rows of combined must equal val.jsonl exactly, so a
    # downstream `val_holdout=len(val_rows)` re-split reproduces the
    # bridge's train/val boundary.
    n_val = len(val_rows)
    assert combined_rows[-n_val:] == val_rows


def test_bridge_manifest_records_combined_path(tmp_path: Path) -> None:
    m0_root = _build_m0_dir(tmp_path)
    out_dir = tmp_path / "rlvr1_out"
    manifest = prepare(_args(m0_root, out_dir))
    assert "combined_path" in manifest
    assert manifest["combined_path"].endswith("combined.jsonl")


def test_bridge_lineage_includes_combined_output(tmp_path: Path) -> None:
    """The combined output is the artifact the data_prep config consumes;
    it must show up in the lineage outputs so downstream lineage chains
    can trace back to it."""
    m0_root = _build_m0_dir(tmp_path)
    out_dir = tmp_path / "rlvr1_out"
    manifest = prepare(_args(m0_root, out_dir))
    output_kinds = {o["kind"] for o in manifest["lineage"]["outputs"]}
    assert "m1_rlvr_combined_jsonl" in output_kinds
    combined_out = next(
        o for o in manifest["lineage"]["outputs"] if o["kind"] == "m1_rlvr_combined_jsonl"
    )
    # row count = train + val
    train_total = sum(manifest["counts"]["train"].values())
    val_total = sum(manifest["counts"]["val"].values())
    assert combined_out["rows"] == train_total + val_total


# ---------- data_prep/rlvr{1,2,3}.yaml ----------


@pytest.mark.parametrize("mix", ("rlvr1", "rlvr2", "rlvr3"))
def test_data_prep_rlvr_defaults_reject_internal_lustre_paths(mix: str) -> None:
    """NVIDIA-internal cluster paths must not be runnable defaults."""
    text = DATA_PREP_CONFIG_PATHS[mix].read_text(encoding="utf-8")
    assert "/lustre/" not in text
    assert "yifuw" not in text


@pytest.mark.parametrize("mix", ("rlvr1", "rlvr2", "rlvr3"))
def test_data_prep_rlvr_defaults_point_at_bridge_combined_output(mix: str) -> None:
    """`input_path` must reference the bridge's combined.jsonl shape so
    the M0 → bridge → data_prep pipeline is wired end-to-end."""
    data = _load_data_prep_config(mix)
    assert data["input_path"] == (
        f"${{oc.env:NEMO_RUN_DIR,.}}/output/super3/m1_rlvr/{mix}/combined.jsonl"
    )
    # NEMO_RUN_DIR templating so the path works wherever the operator runs
    assert "${oc.env:NEMO_RUN_DIR" in data["input_path"]


@pytest.mark.parametrize("mix", ("rlvr1", "rlvr2", "rlvr3"))
def test_data_prep_rlvr_defaults_preserve_data_prep_base_fields(mix: str) -> None:
    """The data_prep config must keep the contract fields the existing
    `_data_prep_base.SubStageDataPrepConfig` consumes."""
    data = _load_data_prep_config(mix)
    for field in ("input_path", "output_dir", "val_holdout", "sample", "force"):
        assert field in data, f"data_prep {mix}.yaml missing field {field}"
    assert data["output_dir"] == f"${{oc.env:PWD}}/../output/super3/stage2_rl/{mix}"
    assert data["val_holdout"] == "auto"
    assert data["sample"] is None
    assert data["force"] is False


# ---------- smoke.yaml ----------


def test_smoke_yaml_loads_cleanly() -> None:
    data = yaml.safe_load(SMOKE_PATH.read_text(encoding="utf-8"))
    assert data["defaults"] == "default.yaml"
    assert "grpo" in data
    assert "policy" in data
    assert "cluster" in data


def test_smoke_yaml_has_smaller_footprint_than_small_yaml() -> None:
    """Smoke is meant for end-to-end pipeline verification, not parity
    runs. Footprint must be strictly less than small.yaml so the smoke
    run actually finishes in a few minutes."""
    smoke = yaml.safe_load(SMOKE_PATH.read_text(encoding="utf-8"))
    small = yaml.safe_load(SMALL_PATH.read_text(encoding="utf-8"))
    assert smoke["cluster"]["num_nodes"] <= small["cluster"]["num_nodes"]
    assert (
        smoke["grpo"]["num_prompts_per_step"]
        < small["grpo"]["num_prompts_per_step"]
    )
    assert (
        smoke["grpo"]["num_generations_per_prompt"]
        <= small["grpo"]["num_generations_per_prompt"]
    )
    assert (
        smoke["policy"]["train_global_batch_size"]
        < small["policy"]["train_global_batch_size"]
    )


def test_smoke_yaml_caps_step_count_for_fast_iteration() -> None:
    """Smoke must declare `max_num_steps` so the run is bounded — the
    point is end-to-end verification, not long convergence."""
    smoke = yaml.safe_load(SMOKE_PATH.read_text(encoding="utf-8"))
    assert "max_num_steps" in smoke["grpo"]
    assert smoke["grpo"]["max_num_steps"] <= 100, (
        "smoke step count should be small (≤ 100) for fast cluster verification; "
        f"got {smoke['grpo']['max_num_steps']}"
    )


def test_smoke_yaml_runs_validation_at_end_for_a_signal_check() -> None:
    """Smoke must produce *some* val signal so the operator can confirm
    the regression report path works end-to-end against real rollouts."""
    smoke = yaml.safe_load(SMOKE_PATH.read_text(encoding="utf-8"))
    assert smoke["grpo"]["val_at_end"] is True


def test_smoke_yaml_keeps_run_block_contract() -> None:
    """The training scaffold expects the `run.data` / `run.model` /
    `run.env.container` triple to be present (per `default.yaml` /
    `small.yaml` pattern)."""
    smoke = yaml.safe_load(SMOKE_PATH.read_text(encoding="utf-8"))
    run = smoke["run"]
    assert "data" in run and "model" in run
    assert "container" in run["env"]
