"""Tests for the M0 → M1 SWE2 data bridge + SIF resolver (task017 Session 1).

Two surfaces under test:

1. SIF image mapping registry + ``resolve_sif_path`` / ``validate_sif_exists``
   (roadmap §1.5 first deliverable).
2. SWE2 env registry + ``prepare()`` bridge (third copy of the
   registry-driven bridge pattern after RLVR + SWE1).
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from nemotron.recipes.super3.milestones.lineage import (
    LineageRecord,
    SWE2_ARTIFACT,
)
from nemotron.recipes.super3.milestones.m1_swe2.prepare_m1_swe2_jsonl import (
    ENV_REGISTRY_PATH,
    KNOWN_SIF_SOURCES,
    KNOWN_STATUSES,
    MIX_NAME,
    SIF_REGISTRY_PATH,
    SWE2_ENV_MAP,
    SWE2_PROFILE,
    build_mix_profile,
    coverage_report,
    derive_env_map,
    load_swe2_env_registry,
    load_swe2_sif_registry,
    prepare,
    resolve_sif_path,
    tag_record,
    validate_sif_exists,
)


def _m0_record(env: str, instance_id: str = "octocat__hello-world-42") -> dict[str, Any]:
    return {
        "environment": env,
        "milestone": "M0",
        "use_stage": ["M0 data_env_foundation"],
        "question": f"fix issue {instance_id}",
        "expected_answer": "patch",
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "fix it"},
            ],
            "tools": [],
        },
        "reward_config": {"verifier": "openhands_loop", "max_score": 1.0},
        "extra_env_info": {"instance_id": instance_id},
        "metadata": {"source_dataset": "stub", "license": "mit"},
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


# ---------- SIF registry + resolver ----------


def test_sif_registry_loads_three_known_sources() -> None:
    rows = load_swe2_sif_registry()
    sources = {row["source"] for row in rows}
    assert sources == {"swebench", "swegym", "r2egym"}
    assert sources <= KNOWN_SIF_SOURCES
    for row in rows:
        assert "{instance_id}" in row["filename_template"]


def test_sif_registry_path_resolves_to_yaml_in_module() -> None:
    assert SIF_REGISTRY_PATH.is_file()
    assert SIF_REGISTRY_PATH.suffix == ".yaml"
    assert SIF_REGISTRY_PATH.parent.name == "m1_swe2"


def test_sif_registry_rejects_unknown_source(tmp_path: Path) -> None:
    bad = tmp_path / "sif.yaml"
    bad.write_text(
        """schema_version: 1
sif_sources:
  - source: definitely-not-a-source
    filename_template: "stub_{instance_id}.sif"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not in"):
        load_swe2_sif_registry(bad)


def test_sif_registry_rejects_template_without_instance_id(tmp_path: Path) -> None:
    """Catches authorship typos that would silently produce identical paths."""
    bad = tmp_path / "sif.yaml"
    bad.write_text(
        """schema_version: 1
sif_sources:
  - source: swebench
    filename_template: "swebench_static.sif"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"\{instance_id\}"):
        load_swe2_sif_registry(bad)


def test_resolve_sif_path_for_each_known_source() -> None:
    assert resolve_sif_path(
        instance_id="astropy__astropy-12907",
        source="swebench",
        sif_dir="/lustre/sif",
    ) == Path("/lustre/sif/swebench_sweb.eval.x86_64.astropy__astropy-12907.sif")
    assert resolve_sif_path(
        instance_id="docker__compose-99",
        source="swegym",
        sif_dir="/lustre/sif",
    ) == Path("/lustre/sif/swegym_sweb.eval.x86_64.docker__compose-99.sif")
    assert resolve_sif_path(
        instance_id="rust-lang__cargo-100",
        source="r2egym",
        sif_dir=Path("/lustre/sif"),
    ) == Path("/lustre/sif/r2egym_rust-lang__cargo-100.sif")


def test_resolve_sif_path_rejects_unknown_source() -> None:
    with pytest.raises(ValueError, match="unknown SIF source"):
        resolve_sif_path(instance_id="x__y-1", source="nonexistent", sif_dir="/tmp")


def test_resolve_sif_path_rejects_path_injection() -> None:
    """instance_ids interpolate into filesystem paths — anything with a
    separator is a path-injection attempt."""
    with pytest.raises(ValueError, match="instance_id"):
        resolve_sif_path(instance_id="..", source="swebench", sif_dir="/tmp")
    with pytest.raises(ValueError, match="instance_id"):
        resolve_sif_path(instance_id="a/b", source="swebench", sif_dir="/tmp")
    with pytest.raises(ValueError, match="instance_id"):
        resolve_sif_path(instance_id="", source="swebench", sif_dir="/tmp")


def test_validate_sif_exists_reads_filesystem(tmp_path: Path) -> None:
    sif = tmp_path / "swebench_sweb.eval.x86_64.demo__repo-1.sif"
    assert not validate_sif_exists(sif)
    sif.write_text("", encoding="utf-8")
    assert validate_sif_exists(sif)


# ---------- SWE2 env registry ----------


def test_env_registry_loads_with_expected_shape() -> None:
    registry = load_swe2_env_registry()
    assert len(registry) >= 3, "expected at least 3 rows (one per SIF source family)"
    for row in registry:
        assert {"nemo_gym_env", "mix", "status"} <= row.keys()
        assert row["status"] in KNOWN_STATUSES
        assert row["mix"] == "swe2"
        sif_source = row.get("sif_source")
        if sif_source is not None:
            assert sif_source in KNOWN_SIF_SOURCES


def test_env_registry_path_resolves_to_yaml_in_module() -> None:
    assert ENV_REGISTRY_PATH.is_file()
    assert ENV_REGISTRY_PATH.suffix == ".yaml"
    assert ENV_REGISTRY_PATH.parent.name == "m1_swe2"


def test_env_registry_rejects_non_swe2_mix(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: swe1
    status: active
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="SWE2 registry should only carry swe2 rows"):
        load_swe2_env_registry(bad)


def test_env_registry_rejects_unknown_sif_source(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: swe2
    status: active
    sif_source: not-a-source
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="sif_source"):
        load_swe2_env_registry(bad)


def test_derive_env_map_filters_to_active() -> None:
    fake = [
        {"nemo_gym_env": "swe_agents", "mix": "swe2", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "swe_agents", "mix": "swe2", "m0_env_id": None, "status": "m0_missing"},
    ]
    assert derive_env_map(fake) == {"m0_a": "swe_agents"}


def test_coverage_report_breaks_down_by_sif_source() -> None:
    """SWE2-specific extension over the RLVR/SWE1 coverage: a per-SIF-family
    histogram so coverage explains *which* container family still needs
    an M0 source."""
    fake = [
        {"nemo_gym_env": "swe_agents", "mix": "swe2", "sif_source": "swebench", "status": "m0_missing"},
        {"nemo_gym_env": "swe_agents", "mix": "swe2", "sif_source": "swegym", "status": "m0_missing"},
        {"nemo_gym_env": "swe_agents", "mix": "swe2", "sif_source": "r2egym", "status": "m0_missing"},
    ]
    coverage = coverage_report(fake)
    assert coverage["mix"] == "swe2"
    assert coverage["total_target_envs"] == 3
    assert coverage["counts"]["m0_missing"] == 3
    breakdown = coverage["sif_source_breakdown"]
    assert set(breakdown.keys()) == {"swebench", "swegym", "r2egym"}
    for family in ("swebench", "swegym", "r2egym"):
        assert breakdown[family] == {"m0_missing": 1}


# ---------- SWE2 mix shape (today) ----------


def test_swe2_profile_uses_correct_artifact() -> None:
    assert SWE2_PROFILE["artifact_type"] == SWE2_ARTIFACT
    assert SWE2_PROFILE["stage"] == "M1 SWE2"
    assert MIX_NAME == "swe2"


def test_swe2_env_map_lights_up_post_task017_session_2() -> None:
    """task017 Session 2 (M0 SWE-Gym → swe2_openhands_trace) lit up the
    swe2 active row for the `swegym` SIF family. The bridge now maps
    the M0 env to the NeMo-Gym ``swe_agents`` env. Previously asserted-
    empty (test_swe2_env_map_empty_today) — flipped to lock the active
    state so a future regression that removes the active row gets caught."""
    assert SWE2_ENV_MAP == {"swe2_openhands_trace": "swe_agents"}


# ---------- tag_record ----------


def test_tag_record_preserves_m0_payload_and_adds_swe2_tags() -> None:
    record = _m0_record("swe_pivot_patch_supervision", "demo__repo-1")
    tagged = tag_record(
        record,
        nemo_gym_env="swe_agents",
        sif_source="swebench",
        row_index=5,
        split="train",
    )
    assert tagged["nemo_gym_env"] == "swe_agents"
    assert tagged["nemo_gym_mix"] == "swe2"
    assert tagged["sif_source"] == "swebench"
    assert tagged["environment"] == "swe_pivot_patch_supervision"
    assert tagged["responses_create_params"] == record["responses_create_params"]
    assert tagged["metadata"]["m0_environment"] == "swe_pivot_patch_supervision"
    assert tagged["metadata"]["sif_source"] == "swebench"
    assert tagged["metadata"]["swe2_row_index"] == 5
    assert tagged["metadata"]["swe2_split"] == "train"


# ---------- prepare() ----------


def test_prepare_raises_coverage_aware_error_when_no_active_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Post-task017-Session-2 main has an active swe2 row, so pin the
    error path by monkey-patching to an all-inactive registry — the
    coverage-aware error must keep working as a regression guard."""
    from nemotron.recipes.super3.milestones.m1_swe2 import prepare_m1_swe2_jsonl

    monkeypatch.setattr(
        prepare_m1_swe2_jsonl,
        "_REGISTRY",
        [
            {
                "nemo_gym_env": "swe_agents",
                "mix": "swe2",
                "m0_env_id": None,
                "sif_source": "swebench",
                "status": "m0_missing",
                "license": "unknown",
            }
        ],
    )
    monkeypatch.setattr(prepare_m1_swe2_jsonl, "SWE2_ENV_MAP", {})
    monkeypatch.setattr(
        prepare_m1_swe2_jsonl,
        "SWE2_PROFILE",
        {**prepare_m1_swe2_jsonl.SWE2_PROFILE, "env_map": {}},
    )

    env_rows = {"swe_pivot_patch_supervision": {"train": [], "val": []}}
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "swe2_out"

    with pytest.raises(ValueError, match="no active M0"):
        prepare(_args(m0_root, out_dir))


def test_prepare_happy_path_with_synthetic_active_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end with one active row monkeypatched in. Proves the bridge
    will pick up Session 2's M0 SWE2 source the moment the registry flips."""
    fake_registry = [
        {
            "nemo_gym_env": "swe_agents",
            "mix": "swe2",
            "m0_env_id": "swe_openhands_demo",
            "status": "active",
            "sif_source": "swebench",
            "license": "apache-2.0",
        },
    ]
    fake_profile = build_mix_profile(fake_registry)
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_swe2.prepare_m1_swe2_jsonl._REGISTRY",
        fake_registry,
    )
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_swe2.prepare_m1_swe2_jsonl.SWE2_PROFILE",
        fake_profile,
    )

    env_rows = {
        "swe_openhands_demo": {
            "train": [_m0_record("swe_openhands_demo", f"demo__r-{i}") for i in range(2)],
            "val": [_m0_record("swe_openhands_demo", "demo__r-val")],
        }
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "swe2_out"

    manifest = prepare(_args(m0_root, out_dir))

    assert manifest["mix"] == "swe2"
    train_rows = [
        json.loads(line)
        for line in (out_dir / "train.jsonl").read_text().splitlines()
        if line
    ]
    assert len(train_rows) == 2
    for row in train_rows:
        assert row["nemo_gym_env"] == "swe_agents"
        assert row["nemo_gym_mix"] == "swe2"
        assert row["sif_source"] == "swebench"

    lineage = LineageRecord.from_jsonable(manifest["lineage"])
    assert lineage.artifact_type == SWE2_ARTIFACT
    assert lineage.produced_by == "prepare_m1_swe2_jsonl.py"
    manifest_inputs = [inp for inp in lineage.inputs if inp.kind == "manifest"]
    assert len(manifest_inputs) == 1
    assert Path(manifest_inputs[0].ref).resolve() == (m0_root / "manifest.json").resolve()
    output_kinds = {out.kind for out in lineage.outputs}
    assert {"m1_swe2_train_jsonl", "m1_swe2_val_jsonl"}.issubset(output_kinds)

    coverage = manifest["coverage"]
    assert coverage["counts"]["active"] == 1
    assert coverage["active"] == ["swe_agents"]
    assert manifest["data_quality"]["source_metadata"]["train"]["rows"] == 2
    assert manifest["data_quality"]["source_metadata"]["val"]["rows"] == 1
    assert set(manifest["output_fingerprints"]) == {"train_path", "val_path"}
    assert len(manifest["output_fingerprints"]["train_path"]) == 64
    report_md = (out_dir / "report.md").read_text(encoding="utf-8")
    assert "## Data quality audit" in report_md
    assert "## Output fingerprints" in report_md
