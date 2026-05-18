"""Tests for the M0 → M1 RLHF data bridge (task018 Session 1).

Three surfaces:

1. RLHF env registry (two NeMo-Gym envs: ``genrm_compare`` +
   ``single_step_tool_use_with_argument_comparison``).
2. Preference-data candidate registry (HelpSteer-2 / UltraFeedback /
   distilabel orca pairs).
3. ``prepare()`` bridge — fourth registry-driven copy, today active=0.
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
    RLHF_ARTIFACT,
)
from nemotron.recipes.super3.milestones.m1_rlhf.prepare_m1_rlhf_jsonl import (
    ENV_REGISTRY_PATH,
    KNOWN_STATUSES,
    MIX_NAME,
    PREF_DATA_REGISTRY_PATH,
    RLHF_ENV_MAP,
    RLHF_PROFILE,
    build_mix_profile,
    coverage_report,
    derive_env_map,
    load_rlhf_env_registry,
    load_rlhf_pref_data_registry,
    pref_candidate_ids,
    prepare,
    tag_record,
)


def _m0_record(env: str) -> dict[str, Any]:
    return {
        "environment": env,
        "milestone": "M0",
        "question": "judge response A vs B",
        "expected_answer": "A",
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "judge"},
                {"role": "user", "content": "A or B?"},
            ],
            "tools": [],
        },
        "reward_config": {"verifier": "genrm_compare", "max_score": 1.0},
        "extra_env_info": {"completion_a": "x", "completion_b": "y"},
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


# ---------- Env registry ----------


def test_env_registry_loads_with_expected_shape() -> None:
    registry = load_rlhf_env_registry()
    assert len(registry) >= 2, "expected at least 2 rows (genrm_compare + tool-call validity)"
    nemo_gym_envs = {row["nemo_gym_env"] for row in registry}
    assert {"genrm_compare", "single_step_tool_use_with_argument_comparison"} <= nemo_gym_envs
    for row in registry:
        assert {"nemo_gym_env", "mix", "status"} <= row.keys()
        assert row["status"] in KNOWN_STATUSES
        assert row["mix"] == "rlhf"


def test_env_registry_path_resolves_to_yaml_in_module() -> None:
    assert ENV_REGISTRY_PATH.is_file()
    assert ENV_REGISTRY_PATH.suffix == ".yaml"
    assert ENV_REGISTRY_PATH.parent.name == "m1_rlhf"


def test_env_registry_rejects_non_rlhf_mix(tmp_path: Path) -> None:
    """RLHF registry must reject rlvr1/swe1/swe2 rows — catches copy-paste."""
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: rlvr1
    status: active
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="RLHF registry should only carry rlhf rows"):
        load_rlhf_env_registry(bad)


def test_env_registry_rejects_unknown_status(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: rlhf
    status: bogus
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="status"):
        load_rlhf_env_registry(bad)


# ---------- Preference-data candidate registry ----------


def test_pref_data_registry_loads_with_expected_candidates() -> None:
    pref = load_rlhf_pref_data_registry()
    ids = pref_candidate_ids(pref)
    # Roadmap names HelpSteer-2, UltraFeedback as primaries.
    assert "helpsteer2" in ids
    assert "ultrafeedback" in ids
    for row in pref:
        assert {"id", "hf_dataset", "license"} <= row.keys()


def test_pref_data_registry_path_resolves_to_yaml_in_module() -> None:
    assert PREF_DATA_REGISTRY_PATH.is_file()
    assert PREF_DATA_REGISTRY_PATH.suffix == ".yaml"
    assert PREF_DATA_REGISTRY_PATH.parent.name == "m1_rlhf"


def test_pref_data_registry_rejects_missing_fields(tmp_path: Path) -> None:
    bad = tmp_path / "pref.yaml"
    bad.write_text(
        """schema_version: 1
datasets:
  - id: incomplete
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required field"):
        load_rlhf_pref_data_registry(bad)


# ---------- Mix profile + derivation ----------


def test_rlhf_profile_uses_correct_artifact() -> None:
    assert RLHF_PROFILE["artifact_type"] == RLHF_ARTIFACT
    assert RLHF_PROFILE["stage"] == "M1 RLHF"
    assert MIX_NAME == "rlhf"


def test_rlhf_env_map_empty_today() -> None:
    """All registry rows are m0_missing or blocked_external — env_map empty."""
    assert RLHF_ENV_MAP == {}


def test_derive_env_map_filters_to_active() -> None:
    fake = [
        {"nemo_gym_env": "genrm_compare", "mix": "rlhf", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "genrm_compare", "mix": "rlhf", "m0_env_id": None, "status": "blocked_external"},
    ]
    assert derive_env_map(fake) == {"m0_a": "genrm_compare"}


def test_coverage_report_includes_pref_dataset_breakdown_and_candidates() -> None:
    """RLHF-specific extension: coverage block carries
    ``pref_dataset_breakdown`` (status histogram per pref candidate named
    in env registry) AND ``known_pref_candidates`` (id list from the pref
    data registry). Together they answer 'which pref source is wired to
    which env, and which pref sources have no wiring yet?'."""
    fake_envs = [
        {"nemo_gym_env": "genrm_compare", "mix": "rlhf", "pref_dataset_candidate": "helpsteer2", "status": "blocked_external"},
        {"nemo_gym_env": "single_step_tool_use_with_argument_comparison", "mix": "rlhf", "status": "m0_missing"},
    ]
    fake_pref = [
        {"id": "helpsteer2", "hf_dataset": "nvidia/HelpSteer2", "license": "cc-by-4.0"},
        {"id": "ultrafeedback", "hf_dataset": "openbmb/UltraFeedback", "license": "mit"},
    ]
    coverage = coverage_report(fake_envs, fake_pref)
    assert coverage["mix"] == "rlhf"
    assert coverage["counts"]["blocked_external"] == 1
    assert coverage["counts"]["m0_missing"] == 1
    assert coverage["pref_dataset_breakdown"] == {"helpsteer2": {"blocked_external": 1}}
    assert coverage["known_pref_candidates"] == ["helpsteer2", "ultrafeedback"]


def test_coverage_report_today_reflects_main() -> None:
    """Today's main: genrm_compare blocked_external (model + data),
    tool-call validity m0_missing."""
    coverage = coverage_report(load_rlhf_env_registry(), load_rlhf_pref_data_registry())
    assert coverage["counts"]["active"] == 0
    assert coverage["counts"]["blocked_external"] >= 1
    assert coverage["counts"]["m0_missing"] >= 1
    # known_pref_candidates surfaces the candidate registry.
    assert "helpsteer2" in coverage["known_pref_candidates"]


# ---------- tag_record ----------


def test_tag_record_preserves_m0_payload_and_adds_rlhf_tags() -> None:
    record = _m0_record("rlhf_helpsteer2")
    tagged = tag_record(
        record,
        nemo_gym_env="genrm_compare",
        pref_dataset="helpsteer2",
        row_index=2,
        split="train",
    )
    assert tagged["nemo_gym_env"] == "genrm_compare"
    assert tagged["nemo_gym_mix"] == "rlhf"
    assert tagged["pref_dataset"] == "helpsteer2"
    assert tagged["environment"] == "rlhf_helpsteer2"
    assert tagged["responses_create_params"] == record["responses_create_params"]
    assert tagged["metadata"]["m0_environment"] == "rlhf_helpsteer2"
    assert tagged["metadata"]["pref_dataset"] == "helpsteer2"
    assert tagged["metadata"]["rlhf_row_index"] == 2
    assert tagged["metadata"]["rlhf_split"] == "train"


# ---------- prepare() error and happy paths ----------


def test_prepare_raises_coverage_aware_error_today(tmp_path: Path) -> None:
    env_rows = {"rlhf_helpsteer2": {"train": [], "val": []}}
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlhf_out"

    with pytest.raises(ValueError, match="no active M0"):
        prepare(_args(m0_root, out_dir))


def test_prepare_happy_path_with_synthetic_active_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: monkeypatch a synthetic active row → JSONL + manifest
    + lineage tagged RLHF_ARTIFACT + coverage active=1 + pref_dataset
    tag flows through to every row."""
    fake_envs = [
        {
            "nemo_gym_env": "genrm_compare",
            "mix": "rlhf",
            "m0_env_id": "rlhf_helpsteer2",
            "status": "active",
            "pref_dataset_candidate": "helpsteer2",
            "license": "cc-by-4.0",
        },
    ]
    fake_profile = build_mix_profile(fake_envs)
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_rlhf.prepare_m1_rlhf_jsonl._REGISTRY",
        fake_envs,
    )
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.m1_rlhf.prepare_m1_rlhf_jsonl.RLHF_PROFILE",
        fake_profile,
    )

    env_rows = {
        "rlhf_helpsteer2": {
            "train": [_m0_record("rlhf_helpsteer2") for _ in range(2)],
            "val": [_m0_record("rlhf_helpsteer2")],
        }
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlhf_out"

    manifest = prepare(_args(m0_root, out_dir))

    assert manifest["mix"] == "rlhf"
    train_rows = [
        json.loads(line)
        for line in (out_dir / "train.jsonl").read_text().splitlines()
        if line
    ]
    assert len(train_rows) == 2
    for row in train_rows:
        assert row["nemo_gym_env"] == "genrm_compare"
        assert row["nemo_gym_mix"] == "rlhf"
        assert row["pref_dataset"] == "helpsteer2"

    lineage = LineageRecord.from_jsonable(manifest["lineage"])
    assert lineage.artifact_type == RLHF_ARTIFACT
    assert lineage.produced_by == "prepare_m1_rlhf_jsonl.py"
    manifest_inputs = [inp for inp in lineage.inputs if inp.kind == "manifest"]
    assert len(manifest_inputs) == 1
    assert Path(manifest_inputs[0].ref).resolve() == (m0_root / "manifest.json").resolve()
    output_kinds = {out.kind for out in lineage.outputs}
    assert {"m1_rlhf_train_jsonl", "m1_rlhf_val_jsonl"}.issubset(output_kinds)

    coverage = manifest["coverage"]
    assert coverage["counts"]["active"] == 1
    assert coverage["active"] == ["genrm_compare"]
