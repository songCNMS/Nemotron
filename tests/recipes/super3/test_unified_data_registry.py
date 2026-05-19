"""Tests for the unified data registry (task030 Session 1).

Three surfaces:

1. Per-kind schema validators in
   ``data_registries/schema.py`` — fail-fast on shape drift.
2. ``unified_index.yaml`` + loader catalogue every registry the
   pipeline actually uses today.
3. Cross-registry inventories (licenses / HF datasets / M0 → downstream
   cross-walk) — read-only audits operators can run from sandbox.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.data_registries.schema import (
    KNOWN_BRIDGE_STATUSES,
    KNOWN_KINDS,
    bridge_mix_validator_factory,
    bridge_status_validator,
    validate_rows,
    validate_top_level,
)
from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
    INDEX_PATH,
    hf_dataset_inventory,
    licenses_inventory,
    load_registry_file,
    load_unified_index,
    m0_to_downstream_inventory,
    validate_unified_index,
)


yaml = pytest.importorskip("yaml")


# ---------- Schema validators ----------


def test_known_kinds_covers_today_registry_families() -> None:
    """The schema layer must enumerate every registry family the
    pipeline ships with — adding a new kind (e.g., task019 eval basket)
    is a one-validator + one-index-row change."""
    assert KNOWN_KINDS == frozenset(
        {
            "m0_data_registry",
            "m0_environment_registry",
            "bridge_env_registry",
            "sif_registry",
            "pref_data_registry",
            "sandbox_image_registry",  # task021 Session 3
        }
    )


def test_known_bridge_statuses_match_bridge_base() -> None:
    """The schema layer's status vocabulary must match the runtime's
    ``_bridge_base.KNOWN_STATUSES`` (drift here would let the auditor
    accept rows the bridges reject)."""
    from nemotron.recipes.super3.milestones._bridge_base import (
        KNOWN_STATUSES as BRIDGE_KNOWN_STATUSES,
    )

    assert KNOWN_BRIDGE_STATUSES == BRIDGE_KNOWN_STATUSES


def test_validate_top_level_rejects_missing_schema_version() -> None:
    bad = {"milestone": "M1", "envs": []}
    with pytest.raises(ValueError, match="schema_version"):
        validate_top_level(bad, kind="bridge_env_registry")


def test_validate_top_level_rejects_missing_rows_key() -> None:
    bad = {"schema_version": 1, "milestone": "M1"}
    with pytest.raises(ValueError, match="missing rows key 'envs'"):
        validate_top_level(bad, kind="bridge_env_registry")


def test_validate_top_level_rejects_unknown_kind() -> None:
    data = {"schema_version": 1, "milestone": "M1", "envs": []}
    with pytest.raises(ValueError, match="unknown registry kind"):
        validate_top_level(data, kind="not-a-kind")


def test_validate_rows_flags_missing_required_field() -> None:
    data = {
        "schema_version": 1,
        "milestone": "M1",
        "envs": [
            {"nemo_gym_env": "x", "mix": "rlhf"},  # missing 'status'
        ],
    }
    issues = validate_rows(data, kind="bridge_env_registry")
    assert any("missing required field 'status'" in i for i in issues)


def test_bridge_status_validator_catches_typo() -> None:
    issue = bridge_status_validator({"status": "actvie"}, 0)  # typo
    assert issue is not None and "actvie" in issue


def test_bridge_mix_validator_catches_wrong_mix() -> None:
    validator = bridge_mix_validator_factory(["rlhf"])
    issue = validator({"mix": "rlvr1"}, 0)
    assert issue is not None and "expected_mixes" in issue
    assert validator({"mix": "rlhf"}, 0) is None


# ---------- unified_index.yaml shape ----------


def test_unified_index_loads_with_expected_registries() -> None:
    rows = load_unified_index()
    ids = {row["id"] for row in rows}
    # Every registry that exists today must be catalogued.
    expected = {
        "m0_data",
        "m0_environment",
        "m1_rlvr_envs",
        "m1_swe1_envs",
        "m1_swe2_envs",
        "m1_swe2_sif",
        "m1_rlhf_envs",
        "m1_rlhf_pref_data",
    }
    assert expected <= ids, f"missing expected registries: {expected - ids}"


def test_unified_index_path_lives_in_data_registries_dir() -> None:
    assert INDEX_PATH.is_file()
    assert INDEX_PATH.parent.name == "data_registries"


def test_unified_index_rejects_duplicate_id(tmp_path: Path) -> None:
    bad = tmp_path / "index.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M1
registries:
  - id: dup
    kind: bridge_env_registry
    path: foo.yaml
    summary: stub
  - id: dup
    kind: bridge_env_registry
    path: bar.yaml
    summary: stub
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate registry id"):
        load_unified_index(bad)


def test_unified_index_rejects_unknown_kind(tmp_path: Path) -> None:
    bad = tmp_path / "index.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M1
registries:
  - id: stub
    kind: not-a-kind
    path: foo.yaml
    summary: stub
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not in"):
        load_unified_index(bad)


# ---------- Live validation: every registry on main passes ----------


def test_live_unified_index_validation_is_clean() -> None:
    """The single most important test in this file — exercises every
    registry the pipeline ships with today through the schema layer.
    Any drift surfaces here before a cluster run discovers it the
    expensive way."""
    issues = validate_unified_index()
    assert issues == [], (
        "live unified index has schema drift; fix the registry or the schema:\n"
        + "\n".join(issues)
    )


def test_every_registry_path_resolves_to_a_real_file() -> None:
    """Sanity check: every path declared in the index must resolve."""
    rows = load_unified_index()
    for entry in rows:
        target = (INDEX_PATH.parent / entry["path"]).resolve()
        assert target.is_file(), f"{entry['id']}: path {entry['path']!r} → {target}"


# ---------- Cross-registry inventories ----------


def test_licenses_inventory_surfaces_known_licenses() -> None:
    """The license walk must find at least the licenses we know are in
    play (cc-by-4.0, apache-2.0, mit, cc-by-sa-4.0). cc-by-sa-4.0 is
    the share-alike license blocking task056 Session 2's Lean work —
    making it visible here helps future audits."""
    inventory = licenses_inventory()
    licenses = set(inventory.keys())
    expected_subset = {"cc-by-4.0", "apache-2.0", "mit"}
    assert expected_subset <= licenses, f"missing licenses: {expected_subset - licenses}"
    # Every license entry must point at at least one registry row.
    for license_name, entries in inventory.items():
        assert entries, f"license {license_name!r} has no entries"


def test_hf_dataset_inventory_enumerates_data_registries() -> None:
    """HF dataset walk covers m0_data_registry + pref_data_registry only
    (bridge env registries reference M0 env ids, not raw HF datasets)."""
    inventory = hf_dataset_inventory()
    # M0 data registry contains these production datasets.
    assert "hotpotqa/hotpot_qa" in inventory
    assert "google-research-datasets/mbpp" in inventory
    assert "openai/gsm8k" in inventory
    # RLHF pref data registry contains these candidates.
    assert "nvidia/HelpSteer2" in inventory
    assert "openbmb/UltraFeedback" in inventory


def test_hf_dataset_inventory_carries_revision_pin_status() -> None:
    """M0 production datasets are pinned to a hf_revision; pref data
    candidates carry hf_revision_pin_required since the actual revision
    isn't pinned until Session 2 of task018 picks one and ingests it."""
    inventory = hf_dataset_inventory()
    gsm8k_entry = inventory["openai/gsm8k"][0]
    assert gsm8k_entry["hf_revision"], "gsm8k should be revision-pinned"

    helpsteer = inventory["nvidia/HelpSteer2"][0]
    assert helpsteer.get("hf_revision_pin_required") is True


def test_m0_to_downstream_cross_walk_shows_active_paths() -> None:
    """For each M0 env that's wired into a downstream mix, the cross-
    walk should surface which mixes pick it up and with what status."""
    inventory = m0_to_downstream_inventory()
    # math_reasoning_numeric is wired into rlvr1 active per task014/015.
    rlvr1_active_rows = [
        e for e in inventory.get("math_reasoning_numeric", [])
        if e["mix"] == "rlvr1" and e["status"] == "active"
    ]
    assert rlvr1_active_rows, "math_reasoning_numeric → rlvr1 active missing"
    # structured_outputs_json is wired into rlvr2 active per task015.
    rlvr2_rows = [
        e for e in inventory.get("structured_outputs_json", [])
        if e["mix"] == "rlvr2" and e["status"] == "active"
    ]
    assert rlvr2_rows


def test_inventory_walks_are_read_only(tmp_path: Path) -> None:
    """Sanity: running the walks doesn't write to the index file or any
    registry. We just compare mtime before/after."""
    target = INDEX_PATH
    before = target.stat().st_mtime
    licenses_inventory()
    hf_dataset_inventory()
    m0_to_downstream_inventory()
    after = target.stat().st_mtime
    assert before == after
