"""Tests for the M0 → M1 SWE1 data bridge (task016 Session 1).

Covers:

- Registry loader returns ≥ 2 envs (m0_missing slot + verifier_mismatch
  for the existing M0 SWE-bench Lite source)
- Registry rejects rows whose ``mix`` is not ``swe1``
- ``derive_env_map`` returns empty when no rows are active
- ``coverage_report`` counts statuses correctly
- ``prepare()`` raises a coverage-aware error on today's main (no active
  rows)
- ``tag_record`` preserves M0 payload + adds nemo_gym_env tag
- End-to-end happy path with a synthetic test-only registry that flips a
  row to ``active`` — manifest + lineage block tagged ``SWE1_ARTIFACT``
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from nemotron.recipes.super3.milestones.lineage import (
    SWE1_ARTIFACT,
    LineageRecord,
)
from nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl import (
    KNOWN_STATUSES,
    MIX_NAME,
    REGISTRY_PATH,
    SWE1_ENV_MAP,
    SWE1_PROFILE,
    build_mix_profile,
    coverage_report,
    derive_env_map,
    load_swe1_env_registry,
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
            "source_dataset": "stub",
            "license": "mit",
            "data_stage": "M0",
        },
    }


def _build_m0_dir(
    tmp_path: Path,
    *,
    env_rows: Mapping[str, Mapping[str, list[dict[str, Any]]]],
) -> Path:
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


def _args(m0_root: Path, out_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(
        m0_input_dir=m0_root,
        output_dir=out_dir,
        max_records_per_env=None,
        max_val_records_per_env=None,
    )


# ---------- Registry-level tests ----------


def test_registry_loads_with_expected_shape() -> None:
    registry = load_swe1_env_registry()
    assert len(registry) >= 2, "expected at least 2 rows (m0_missing slot + verifier_mismatch)"
    for row in registry:
        assert {"nemo_gym_env", "mix", "status"} <= row.keys()
        assert row["status"] in KNOWN_STATUSES
        assert row["mix"] == "swe1"


def test_registry_path_resolves_to_yaml_in_module() -> None:
    assert REGISTRY_PATH.is_file()
    assert REGISTRY_PATH.suffix == ".yaml"
    assert REGISTRY_PATH.parent.name == "m1_swe1"


def test_registry_rejects_non_swe1_mix(tmp_path: Path) -> None:
    """SWE1 registry must reject rlvr1/2/3 rows; that's what the m1_rlvr
    module is for. Catches accidental copy-paste between registries."""
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: rlvr1
    m0_env_id: m0_stub
    m0_verifier: exact_match
    nemo_gym_verifier: exact_match
    license: apache-2.0
    status: active
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="SWE1 registry should only carry swe1 rows"):
        load_swe1_env_registry(bad)


def test_registry_rejects_unknown_status(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: swe1
    status: definitely-not-a-status
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="status"):
        load_swe1_env_registry(bad)


def test_derive_env_map_filters_to_active() -> None:
    fake_registry = [
        {"nemo_gym_env": "swe_pivot_x", "mix": "swe1", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "swe_pivot_x", "mix": "swe1", "m0_env_id": None, "status": "m0_missing"},
        {"nemo_gym_env": "swe_pivot_x", "mix": "swe1", "m0_env_id": "m0_c", "status": "verifier_mismatch"},
    ]
    assert derive_env_map(fake_registry) == {"m0_a": "swe_pivot_x"}


def test_derive_env_map_rejects_conflicting_active_rows() -> None:
    fake_registry = [
        {"nemo_gym_env": "swe_x", "mix": "swe1", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "swe_y", "mix": "swe1", "m0_env_id": "m0_a", "status": "active"},
    ]
    with pytest.raises(ValueError, match="two active mappings"):
        derive_env_map(fake_registry)


def test_coverage_report_counts_statuses() -> None:
    fake_registry = [
        {"nemo_gym_env": "a", "mix": "swe1", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "a", "mix": "swe1", "m0_env_id": None, "status": "m0_missing"},
        {"nemo_gym_env": "a", "mix": "swe1", "m0_env_id": "m0_c", "status": "verifier_mismatch"},
    ]
    coverage = coverage_report(fake_registry)
    assert coverage["mix"] == "swe1"
    assert coverage["total_target_envs"] == 3
    assert coverage["counts"]["active"] == 1
    assert coverage["counts"]["m0_missing"] == 1
    assert coverage["counts"]["verifier_mismatch"] == 1


# ---------- Mix shape (post-audit) ----------


def test_swe1_profile_uses_correct_artifact() -> None:
    assert SWE1_PROFILE["artifact_type"] == SWE1_ARTIFACT
    assert SWE1_PROFILE["stage"] == "M1 SWE1"
    assert MIX_NAME == "swe1"


def test_swe1_env_map_lights_up_post_task016_session_2() -> None:
    """task016 Session 2 (M0 SWE-Gym-Lite → swe_pivot_tool_call) lit up
    the swe1 active row. The bridge now maps the M0 env to the NeMo-Gym
    single-step tool-comparison env. Previously asserted-empty
    (test_swe1_env_map_empty_today) — flipped to lock the active state
    so a future regression that removes the active row gets caught."""
    assert SWE1_ENV_MAP == {
        "swe_pivot_tool_call": "swe_pivot_single_step_tool_use_with_argument_comparison",
    }


# ---------- tag_record ----------


def test_tag_record_preserves_m0_payload_and_adds_swe1_tags() -> None:
    record = _m0_record("swe_pivot_patch_supervision", "fix the bug", "patch")
    tagged = tag_record(
        record,
        nemo_gym_env="swe_pivot_single_step_tool_use_with_argument_comparison",
        row_index=3,
        split="train",
    )
    assert tagged["nemo_gym_env"] == "swe_pivot_single_step_tool_use_with_argument_comparison"
    assert tagged["nemo_gym_mix"] == "swe1"
    assert tagged["environment"] == "swe_pivot_patch_supervision"
    assert tagged["responses_create_params"] == record["responses_create_params"]
    assert tagged["reward_config"] == record["reward_config"]
    assert tagged["metadata"]["source_dataset"] == "stub"
    assert tagged["metadata"]["m0_environment"] == "swe_pivot_patch_supervision"
    assert tagged["metadata"]["nemo_gym_env"] == "swe_pivot_single_step_tool_use_with_argument_comparison"
    assert tagged["metadata"]["swe1_row_index"] == 3
    assert tagged["metadata"]["swe1_split"] == "train"


# ---------- prepare() error and happy paths ----------


def test_prepare_raises_coverage_aware_error_when_no_active_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pre-task016-Session-2 main had no active swe1 rows and prepare()
    surfaced the gap. Post-Session-2 there *is* an active row, so this
    test pins the error path itself by monkey-patching to an all-inactive
    registry — the coverage-aware error must keep working for future
    regressions where someone removes the last active row."""
    from nemotron.recipes.super3.milestones.m1_swe1 import prepare_m1_swe1_jsonl

    monkeypatch.setattr(
        prepare_m1_swe1_jsonl,
        "_REGISTRY",
        [
            {
                "nemo_gym_env": "swe_pivot_single_step_tool_use_with_argument_comparison",
                "mix": "swe1",
                "m0_env_id": None,
                "status": "m0_missing",
                "license": "unknown",
            }
        ],
    )
    monkeypatch.setattr(prepare_m1_swe1_jsonl, "SWE1_ENV_MAP", {})
    monkeypatch.setattr(
        prepare_m1_swe1_jsonl,
        "SWE1_PROFILE",
        {**prepare_m1_swe1_jsonl.SWE1_PROFILE, "env_map": {}},
    )

    env_rows = {"swe_pivot_patch_supervision": {"train": [], "val": []}}
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "swe1_out"

    with pytest.raises(ValueError, match="no active M0"):
        prepare(_args(m0_root, out_dir))


def test_prepare_happy_path_with_synthetic_active_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: monkey-patch the module to use a registry with one
    active row (`m0_env_id=swe_pivot_demo`), then prove prepare() emits
    JSONL, manifest, and a lineage block tagged SWE1_ARTIFACT.

    This is how Session 2 will look once the M0 SWE pivot env lands: a
    registry flip from m0_missing to active is enough to produce real
    rows — no Python edits required.
    """
    fake_registry = [
        {
            "nemo_gym_env": "swe_pivot_single_step_tool_use_with_argument_comparison",
            "mix": "swe1",
            "m0_env_id": "swe_pivot_demo",
            "status": "active",
            "m0_verifier": "argument_match",
            "nemo_gym_verifier": "argument_match",
            "license": "apache-2.0",
            "notes": "synthetic test row",
        },
    ]
    fake_profile = build_mix_profile(fake_registry)
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl._REGISTRY",
        fake_registry,
    )
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl.SWE1_PROFILE",
        fake_profile,
    )

    env_rows = {
        "swe_pivot_demo": {
            "train": [_m0_record("swe_pivot_demo", f"issue {i}", "patch") for i in range(3)],
            "val": [_m0_record("swe_pivot_demo", "val issue", "patch")],
        }
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "swe1_out"

    manifest = prepare(_args(m0_root, out_dir))

    assert manifest["mix"] == "swe1"
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
    assert len(train_rows) == 3
    assert len(val_rows) == 1
    assert manifest["combined_path"] == str(out_dir / "combined.jsonl")
    assert combined_rows == [*train_rows, *val_rows]
    assert combined_rows[-len(val_rows) :] == val_rows
    for row in train_rows:
        assert row["nemo_gym_env"] == "swe_pivot_single_step_tool_use_with_argument_comparison"
        assert row["nemo_gym_mix"] == "swe1"

    lineage = LineageRecord.from_jsonable(manifest["lineage"])
    assert lineage.artifact_type == SWE1_ARTIFACT
    assert lineage.produced_by == "prepare_m1_swe1_jsonl.py"
    manifest_inputs = [inp for inp in lineage.inputs if inp.kind == "manifest"]
    assert len(manifest_inputs) == 1
    assert Path(manifest_inputs[0].ref).resolve() == (m0_root / "manifest.json").resolve()
    output_kinds = {out.kind for out in lineage.outputs}
    assert {
        "m1_swe1_train_jsonl",
        "m1_swe1_val_jsonl",
        "m1_swe1_combined_jsonl",
    }.issubset(output_kinds)
    combined_output = next(
        out for out in lineage.outputs if out.kind == "m1_swe1_combined_jsonl"
    )
    assert combined_output.rows == len(train_rows) + len(val_rows)

    coverage = manifest["coverage"]
    assert coverage["counts"]["active"] == 1
    assert coverage["active"] == [
        "swe_pivot_single_step_tool_use_with_argument_comparison",
    ]
    assert manifest["data_quality"]["source_metadata"]["train"]["rows"] == 3
    assert manifest["data_quality"]["source_metadata"]["val"]["rows"] == 1
    assert set(manifest["output_fingerprints"]) == {
        "train_path",
        "val_path",
        "combined_path",
    }
    assert len(manifest["output_fingerprints"]["train_path"]) == 64
    assert len(manifest["output_fingerprints"]["combined_path"]) == 64
    report_md = (out_dir / "report.md").read_text(encoding="utf-8")
    assert "## Data quality audit" in report_md
    assert "## Output fingerprints" in report_md
    assert "combined_path" in report_md


def test_prepare_filters_out_envs_outside_swe1_mix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M0 rows whose env isn't mapped active must not leak through."""
    fake_registry = [
        {
            "nemo_gym_env": "swe_pivot_single_step_tool_use_with_argument_comparison",
            "mix": "swe1",
            "m0_env_id": "swe_pivot_demo",
            "status": "active",
        },
    ]
    fake_profile = build_mix_profile(fake_registry)
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl._REGISTRY",
        fake_registry,
    )
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl.SWE1_PROFILE",
        fake_profile,
    )

    env_rows = {
        "swe_pivot_demo": {
            "train": [_m0_record("swe_pivot_demo", "q", "a")],
            "val": [_m0_record("swe_pivot_demo", "q", "a")],
        },
        "math_reasoning_numeric": {  # not in swe1
            "train": [_m0_record("math_reasoning_numeric", "1+1?", "2")],
            "val": [_m0_record("math_reasoning_numeric", "1+1?", "2")],
        },
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "swe1_out"

    manifest = prepare(_args(m0_root, out_dir))

    seen_envs = {
        row["environment"]
        for row in (
            json.loads(line)
            for line in (out_dir / "train.jsonl").read_text().splitlines()
            if line
        )
    }
    assert seen_envs == {"swe_pivot_demo"}
    assert "math_reasoning_numeric" not in manifest["counts"]["train"]
