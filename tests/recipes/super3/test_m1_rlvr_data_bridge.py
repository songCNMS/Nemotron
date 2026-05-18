"""Tests for the M0 → M1 RLVR data bridge (task014 Session 1).

Covers:

- ``RLVR1_ENV_MAP`` matches roadmap §1.3 (four NeMo-Gym envs)
- Unknown mix names raise; rlvr2/rlvr3 slots are reserved but unbuildable
- ``prepare()`` writes ``train.jsonl`` / ``val.jsonl`` / ``manifest.json``
- Output rows carry ``nemo_gym_env`` + ``nemo_gym_mix`` tags
- M0 envs outside the mix are filtered out
- Missing splits surface in ``manifest.errors``
- Lineage block declares ``RLVR1`` artifact pointing at the M0 manifest
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.lineage import (
    RLVR1_ARTIFACT,
    LineageRecord,
)
from nemotron.recipes.super3.milestones.m1_rlvr.prepare_m1_rlvr_jsonl import (
    MIX_PROFILES,
    RLVR1_ENV_MAP,
    RLVR2_ENV_MAP,
    RLVR3_ENV_MAP,
    prepare,
    tag_record,
)


def _m0_record(env: str, question: str, expected: str) -> dict[str, Any]:
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


def _build_m0_dir(
    tmp_path: Path,
    *,
    env_rows: Mapping[str, Mapping[str, list[dict[str, Any]]]],
) -> Path:
    """Lay out a fake M0 output dir: ``<env>/<split>-split.jsonl`` + manifest."""
    root = tmp_path / "m0"
    root.mkdir(parents=True)
    for env, splits in env_rows.items():
        env_dir = root / env
        env_dir.mkdir()
        for split, rows in splits.items():
            (env_dir / f"{split}-split.jsonl").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""),
                encoding="utf-8",
            )
    (root / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "milestone": "M0"}), encoding="utf-8"
    )
    return root


def _args(m0_root: Path, out_dir: Path, *, mix: str = "rlvr1") -> argparse.Namespace:
    return argparse.Namespace(
        m0_input_dir=m0_root,
        output_dir=out_dir,
        mix=mix,
        max_records_per_env=None,
        max_val_records_per_env=None,
    )


def test_rlvr1_env_map_covers_roadmap_four_envs() -> None:
    """Roadmap §1.3 task014 declares exactly these 4 M0 → NeMo-Gym mappings."""
    assert RLVR1_ENV_MAP == {
        "math_reasoning_numeric": "math_with_judge",
        "code_execution_python": "code_gen",
        "search_grounded_qa": "search_grounded_qa",
        "general_tool_calling": "general_tool_calling",
    }
    # Profile picks up the same map and tags the right artifact type.
    assert MIX_PROFILES["rlvr1"]["env_map"] is RLVR1_ENV_MAP
    assert MIX_PROFILES["rlvr1"]["artifact_type"] == RLVR1_ARTIFACT


def test_rlvr2_and_rlvr3_slots_reserved_but_unbuildable() -> None:
    """Future RLVR2 / RLVR3 mixes (task015) declare the slot but no env map.

    Until the per-env reward verifier registration lands, calling prepare
    with those mix names must surface a clear "unbuildable" error rather
    than silently emit an empty mix.
    """
    assert RLVR2_ENV_MAP == {}
    assert RLVR3_ENV_MAP == {}


def test_tag_record_preserves_m0_payload_and_adds_nemo_gym_tags() -> None:
    record = _m0_record("math_reasoning_numeric", "1+1?", "2")
    tagged = tag_record(
        record,
        nemo_gym_env="math_with_judge",
        mix_name="rlvr1",
        row_index=7,
        split="train",
    )
    assert tagged["nemo_gym_env"] == "math_with_judge"
    assert tagged["nemo_gym_mix"] == "rlvr1"
    # M0 contract fields untouched.
    assert tagged["environment"] == "math_reasoning_numeric"
    assert tagged["responses_create_params"] == record["responses_create_params"]
    assert tagged["reward_config"] == record["reward_config"]
    # Metadata is enriched, not replaced.
    assert tagged["metadata"]["source_dataset"] == "stub-dataset"
    assert tagged["metadata"]["m0_environment"] == "math_reasoning_numeric"
    assert tagged["metadata"]["nemo_gym_env"] == "math_with_judge"
    assert tagged["metadata"]["rlvr_row_index"] == 7
    assert tagged["metadata"]["rlvr_split"] == "train"


def test_prepare_writes_jsonl_and_manifest(tmp_path: Path) -> None:
    """End-to-end happy path with 2 rows per env across the 4-env mix."""
    env_rows = {
        env: {
            "train": [_m0_record(env, f"train q{i}", f"a{i}") for i in range(2)],
            "val": [_m0_record(env, f"val q{i}", f"a{i}") for i in range(1)],
        }
        for env in RLVR1_ENV_MAP
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr1_out"

    manifest = prepare(_args(m0_root, out_dir))

    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "val.jsonl"
    assert train_path.is_file()
    assert val_path.is_file()
    train_rows = [json.loads(line) for line in train_path.read_text().splitlines() if line]
    val_rows = [json.loads(line) for line in val_path.read_text().splitlines() if line]
    assert len(train_rows) == 8  # 4 envs × 2 rows
    assert len(val_rows) == 4  # 4 envs × 1 row
    assert manifest["mix"] == "rlvr1"
    assert manifest["counts"]["train"] == {env: 2 for env in RLVR1_ENV_MAP}
    assert manifest["counts"]["val"] == {env: 1 for env in RLVR1_ENV_MAP}
    assert manifest["errors"] == []
    # Every emitted row is tagged with the NeMo-Gym env mapping.
    for row in [*train_rows, *val_rows]:
        m0_env = row["environment"]
        assert row["nemo_gym_env"] == RLVR1_ENV_MAP[m0_env]
        assert row["nemo_gym_mix"] == "rlvr1"
        assert row["metadata"]["nemo_gym_env"] == RLVR1_ENV_MAP[m0_env]


def test_prepare_filters_out_envs_outside_rlvr1_mix(tmp_path: Path) -> None:
    """M0 envs that don't appear in ``RLVR1_ENV_MAP`` must not leak through."""
    env_rows = {
        "math_reasoning_numeric": {
            "train": [_m0_record("math_reasoning_numeric", "q", "a")],
            "val": [_m0_record("math_reasoning_numeric", "q", "a")],
        },
        "swe_pivot_patch_supervision": {  # not in the rlvr1 mix
            "train": [_m0_record("swe_pivot_patch_supervision", "q", "a")],
            "val": [_m0_record("swe_pivot_patch_supervision", "q", "a")],
        },
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr1_out"

    manifest = prepare(_args(m0_root, out_dir))

    seen_envs = {row["environment"] for row in (
        json.loads(line) for line in (out_dir / "train.jsonl").read_text().splitlines() if line
    )}
    assert seen_envs == {"math_reasoning_numeric"}
    assert "swe_pivot_patch_supervision" not in manifest["counts"]["train"]


def test_prepare_records_missing_split_as_error(tmp_path: Path) -> None:
    """If an env has train but no val (or vice versa), surface it in errors."""
    env_rows = {
        "math_reasoning_numeric": {
            "train": [_m0_record("math_reasoning_numeric", "q", "a")],
            # No val split — bridge should still emit train rows + record the gap.
        },
        # Mix envs absent from M0 entirely surface a separate "not in M0 mix" error.
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr1_out"

    manifest = prepare(_args(m0_root, out_dir))

    error_strings = {
        f"{e.get('environment')}::{e.get('split')}::{e.get('error')}"
        for e in manifest["errors"]
    }
    # val split missing for the only present env
    assert any(
        s.startswith("math_reasoning_numeric::val::missing")
        for s in error_strings
    )
    # Three other rlvr1 envs absent from M0 → "not in M0 mix" on both splits
    for missing_env in ("code_execution_python", "search_grounded_qa", "general_tool_calling"):
        assert any(s.startswith(f"{missing_env}::train::") for s in error_strings)
        assert any(s.startswith(f"{missing_env}::val::") for s in error_strings)


def test_prepare_emits_lineage_pointing_at_m0_manifest(tmp_path: Path) -> None:
    """The emitted lineage block must declare the M0 manifest as input and
    tag the artifact as ``RLVR1``."""
    env_rows = {
        env: {
            "train": [_m0_record(env, "q", "a")],
            "val": [_m0_record(env, "q", "a")],
        }
        for env in RLVR1_ENV_MAP
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr1_out"

    manifest = prepare(_args(m0_root, out_dir))

    assert "lineage" in manifest
    lineage = LineageRecord.from_jsonable(manifest["lineage"])
    assert lineage.artifact_type == RLVR1_ARTIFACT
    assert lineage.produced_by == "prepare_m1_rlvr_jsonl.py"
    manifest_inputs = [inp for inp in lineage.inputs if inp.kind == "manifest"]
    assert len(manifest_inputs) == 1
    assert Path(manifest_inputs[0].ref).resolve() == (m0_root / "manifest.json").resolve()
    output_kinds = {out.kind for out in lineage.outputs}
    assert {"m1_rlvr_train_jsonl", "m1_rlvr_val_jsonl"}.issubset(output_kinds)


def test_prepare_rejects_unknown_mix(tmp_path: Path) -> None:
    env_rows = {
        env: {"train": [], "val": []} for env in RLVR1_ENV_MAP
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr1_out"

    import pytest

    # argparse `choices=` would catch this at CLI parse time; calling prepare
    # directly bypasses argparse and lands inside the MIX_PROFILES lookup.
    with pytest.raises(ValueError, match="unknown mix"):
        prepare(_args(m0_root, out_dir, mix="not_a_mix"))


def test_prepare_rejects_rlvr2_until_task015(tmp_path: Path) -> None:
    """rlvr2/rlvr3 profile slots exist but their env_map is empty."""
    # Add rlvr2 to the choices list at runtime so argparse-bypass works;
    # MIX_PROFILES only has rlvr1 today, so prepare's ValueError path is the
    # one that flags the missing env_map.
    profiles_before = MIX_PROFILES.copy()
    MIX_PROFILES["rlvr2"] = {
        "artifact_type": "RLVR2",
        "stage": "M1 RLVR2",
        "env_map": RLVR2_ENV_MAP,
        "used_in_tag": "super3_rlvr2_v0",
    }
    try:
        env_rows = {env: {"train": [], "val": []} for env in RLVR1_ENV_MAP}
        m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
        out_dir = tmp_path / "rlvr2_out"

        import pytest

        with pytest.raises(ValueError, match="task015"):
            prepare(_args(m0_root, out_dir, mix="rlvr2"))
    finally:
        MIX_PROFILES.clear()
        MIX_PROFILES.update(profiles_before)
