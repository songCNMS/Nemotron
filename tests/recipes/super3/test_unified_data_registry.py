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
    m0_contamination_against_validator,
    pref_contamination_against_validator,
    validate_rows,
    validate_top_level,
)
from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
    INDEX_PATH,
    hf_dataset_inventory,
    licenses_inventory,
    load_unified_index,
    m0_to_downstream_inventory,
    validate_unified_index,
)

yaml = pytest.importorskip("yaml")


def _write_minimal_index(
    index_path: Path,
    *,
    registry_path: str,
    kind: str = "bridge_env_registry",
    registry_id: str = "fixture_registry",
) -> Path:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "milestone": "M1",
                "registries": [
                    {
                        "id": registry_id,
                        "kind": kind,
                        "path": registry_path,
                        "summary": "path guard fixture",
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return index_path


def _write_minimal_bridge_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """schema_version: 1
milestone: M1
envs: []
""",
        encoding="utf-8",
    )


# ---------- Schema validators ----------


def test_known_kinds_covers_today_registry_families() -> None:
    """The schema layer must enumerate every registry family the
    pipeline ships with — adding a new kind is a one-validator +
    one-index-row change."""
    assert KNOWN_KINDS == frozenset(
        {
            "m0_data_registry",
            "m0_environment_registry",
            "bridge_env_registry",
            "sif_registry",
            "pref_data_registry",
            "sandbox_image_registry",  # task021 Session 3
            "swe_harness_registry",    # task026 Session 1
            "eval_basket_registry",    # task019 Session 1
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


def test_m0_contamination_against_validator_enforces_list_of_strings() -> None:
    assert m0_contamination_against_validator({"contamination_against": []}, 0) is None
    assert m0_contamination_against_validator({"contamination_against": ["GSM8K test"]}, 0) is None
    assert "must be a list" in (
        m0_contamination_against_validator({"contamination_against": "GSM8K test"}, 0) or ""
    )
    assert "non-empty strings" in (
        m0_contamination_against_validator({"contamination_against": ["GSM8K test", ""]}, 0) or ""
    )


def test_pref_contamination_against_validator_enforces_required_rows() -> None:
    exploratory = {"hf_revision_pin_required": False}
    assert pref_contamination_against_validator(exploratory, 0) is None
    assert "non-empty list" in (
        pref_contamination_against_validator({"hf_revision_pin_required": True}, 0) or ""
    )
    assert "non-empty" in (
        pref_contamination_against_validator(
            {"m0_landed": True, "contamination_against": []}, 0
        )
        or ""
    )
    assert "entries must be non-empty strings" in (
        pref_contamination_against_validator(
            {
                "hf_revision_pin_required": True,
                "contamination_against": ["MT-Bench", ""],
            },
            0,
        )
        or ""
    )
    assert (
        pref_contamination_against_validator(
            {
                "hf_revision_pin_required": True,
                "contamination_against": ["MT-Bench"],
            },
            0,
        )
        is None
    )


# ---------- task030 Session 4: schema API surfaces (fail_fast + strict) ----------


def test_validate_rows_fail_fast_raises_on_first_issue() -> None:
    """Runtime loaders consume schema via ``fail_fast=True`` — a single
    bad row aborts immediately instead of writing partial bad data.
    Catches the regression where validate_rows accidentally falls back
    to collect-all under fail_fast=True."""
    data = {
        "schema_version": 1,
        "milestone": "M1",
        "envs": [
            {"nemo_gym_env": "x", "mix": "rlhf", "status": "active"},  # clean
            {"nemo_gym_env": "y", "mix": "rlhf"},  # missing status
            {"nemo_gym_env": "z", "mix": "rlhf"},  # missing status — should never be reached
        ],
    }
    with pytest.raises(ValueError, match=r"envs\[1\] missing required field 'status'"):
        validate_rows(data, kind="bridge_env_registry", fail_fast=True)


def test_validate_rows_fail_fast_with_source_path_includes_path_prefix() -> None:
    """Runtime loaders pass ``source_path`` so error messages name the
    offending YAML — operators can grep for the path in logs."""
    data = {
        "schema_version": 1,
        "milestone": "M1",
        "envs": [{"nemo_gym_env": "y", "mix": "rlhf"}],  # missing status
    }
    with pytest.raises(
        ValueError, match=r"/path/to/registry\.yaml: envs\[0\] missing required field 'status'"
    ):
        validate_rows(
            data,
            kind="bridge_env_registry",
            fail_fast=True,
            source_path="/path/to/registry.yaml",
        )


def test_validate_rows_collect_all_still_returns_full_issue_list() -> None:
    """Audit mode (default) collects every issue. Catches a regression
    where a future change accidentally short-circuits."""
    data = {
        "schema_version": 1,
        "milestone": "M1",
        "envs": [
            {"nemo_gym_env": "y", "mix": "rlhf"},  # missing status
            {"nemo_gym_env": "z", "mix": "rlhf"},  # missing status
        ],
    }
    issues = validate_rows(data, kind="bridge_env_registry")
    assert len(issues) == 2
    assert all("missing required field 'status'" in issue for issue in issues)


def test_validate_top_level_strict_requires_schema_version_and_milestone() -> None:
    """Audit mode (default ``strict=True``) enforces top-level
    schema_version + milestone for unified-index discovery."""
    bad = {"envs": []}  # missing both schema_version and milestone
    with pytest.raises(ValueError, match=r"missing top-level 'schema_version'"):
        validate_top_level(bad, kind="bridge_env_registry")


def test_validate_top_level_runtime_mode_skips_documentation_fields() -> None:
    """Runtime loaders pass ``strict=False`` because schema_version /
    milestone are documentation, not runtime contract. Only the
    rows_key must be present."""
    runtime_minimal = {"envs": []}  # no schema_version / milestone
    # Should not raise — strict=False skips those checks.
    validate_top_level(runtime_minimal, kind="bridge_env_registry", strict=False)


def test_validate_top_level_runtime_mode_still_requires_rows_key() -> None:
    """Even in lenient (strict=False) mode, the rows_key remains
    mandatory — bridges can't operate on a registry that doesn't have
    the data list."""
    bad = {}  # missing envs key
    with pytest.raises(ValueError, match=r"missing rows key 'envs'"):
        validate_top_level(bad, kind="bridge_env_registry", strict=False)


def test_known_bridge_statuses_still_double_aligned_after_session_4() -> None:
    """Session 4 merge keeps the bridge runtime and schema layer
    *aligned* on KNOWN_STATUSES — schema's `KNOWN_BRIDGE_STATUSES`
    and bridge_base's `KNOWN_STATUSES` must stay in sync (drift
    detected by this test rather than at runtime)."""
    from nemotron.recipes.super3.milestones._bridge_base import (
        KNOWN_STATUSES as BRIDGE_KNOWN_STATUSES,
    )

    assert KNOWN_BRIDGE_STATUSES == BRIDGE_KNOWN_STATUSES


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
        "m2_swe_harnesses",
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


def test_unified_index_rejects_non_string_contamination_targets(tmp_path: Path) -> None:
    data_registry = tmp_path / "data_registry.yaml"
    data_registry.write_text(
        """schema_version: 1
milestone: M0
description: synthetic invalid M0 data registry
datasets:
  - id: bad_contamination
    environment: stub_env
    hf_dataset: stub/dataset
    hf_split: train
    hf_revision: deadbeef
    license: mit
    contamination_against:
      - valid target
      - 123
    converter: stub
    use_stage:
      - M0 data_env_foundation
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M0
registries:
  - id: m0_data_bad
    kind: m0_data_registry
    path: {data_registry.name}
    summary: bad contamination target fixture
""",
        encoding="utf-8",
    )

    issues = validate_unified_index(index)
    assert any("contamination_against entries must be non-empty strings" in issue for issue in issues)


def test_unified_index_rejects_required_pref_without_contamination_targets(
    tmp_path: Path,
) -> None:
    pref_registry = tmp_path / "pref_registry.yaml"
    pref_registry.write_text(
        """schema_version: 1
milestone: M1
description: synthetic invalid pref data registry
datasets:
  - id: pref_missing_targets
    hf_dataset: stub/pref
    hf_revision_pin_required: true
    license: mit
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: pref_data_bad
    kind: pref_data_registry
    path: {pref_registry.name}
    summary: bad pref contamination target fixture
""",
        encoding="utf-8",
    )

    issues = validate_unified_index(index)
    assert any("contamination_against must be a non-empty list" in issue for issue in issues)


def test_unified_index_accepts_clean_relative_registry_path(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    registry = index_dir / "registry.yaml"
    _write_minimal_bridge_registry(registry)
    index = _write_minimal_index(index_dir / "unified_index.yaml", registry_path=registry.name)

    assert validate_unified_index(index) == []


@pytest.mark.parametrize(
    ("registry_path", "expected_issue"),
    [
        ("", "must be a non-empty string"),
        (".", "must use normal relative path components"),
        ("./registry.yaml", "must use normal relative path components"),
        ("nested//registry.yaml", "must use normal relative path components"),
        ("registry.yaml/", "must use normal relative path components"),
    ],
)
def test_unified_index_rejects_empty_or_dot_path_components(
    tmp_path: Path,
    registry_path: str,
    expected_issue: str,
) -> None:
    index = _write_minimal_index(
        tmp_path / "index" / "unified_index.yaml",
        registry_path=registry_path,
    )

    issues = validate_unified_index(index)

    assert any(expected_issue in issue for issue in issues)


def test_unified_index_rejects_traversal_outside_index_dir(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    outside = tmp_path / "outside_registry.yaml"
    _write_minimal_bridge_registry(outside)
    index = _write_minimal_index(
        index_dir / "unified_index.yaml",
        registry_path="../outside_registry.yaml",
    )

    issues = validate_unified_index(index)

    assert any("must stay under registry root" in issue for issue in issues)


def test_unified_index_rejects_absolute_registry_path(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    _write_minimal_bridge_registry(registry)
    index = _write_minimal_index(
        tmp_path / "index" / "unified_index.yaml",
        registry_path=str(registry),
    )

    issues = validate_unified_index(index)

    assert any("must be relative to the unified index" in issue for issue in issues)


def test_unified_index_rejects_symlink_escape(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    outside = tmp_path / "outside_registry.yaml"
    _write_minimal_bridge_registry(outside)
    index_dir.mkdir()
    (index_dir / "linked_registry.yaml").symlink_to(outside)
    index = _write_minimal_index(
        index_dir / "unified_index.yaml",
        registry_path="linked_registry.yaml",
    )

    issues = validate_unified_index(index)

    assert any("must stay under registry root" in issue for issue in issues)


def test_unified_index_rejects_missing_registry_path(tmp_path: Path) -> None:
    index = _write_minimal_index(
        tmp_path / "index" / "unified_index.yaml",
        registry_path="missing_registry.yaml",
    )

    issues = validate_unified_index(index)

    assert any("does not exist" in issue for issue in issues)


def test_unified_index_rejects_directory_registry_path(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    (index_dir / "registry_dir").mkdir(parents=True)
    index = _write_minimal_index(
        index_dir / "unified_index.yaml",
        registry_path="registry_dir",
    )

    issues = validate_unified_index(index)

    assert any("must resolve to a file" in issue for issue in issues)


def test_inventories_do_not_read_registry_path_escape(tmp_path: Path) -> None:
    outside_data = tmp_path / "outside_data_registry.yaml"
    outside_data.write_text(
        """schema_version: 1
milestone: M0
datasets:
  - id: escaped_data
    environment: escaped_env
    hf_dataset: escaped/dataset
    hf_split: train
    hf_revision: deadbeef
    license: escaped-license
    contamination_against: []
    converter: escaped
    use_stage:
      - M0 data_env_foundation
""",
        encoding="utf-8",
    )
    outside_bridge = tmp_path / "outside_bridge_registry.yaml"
    outside_bridge.write_text(
        """schema_version: 1
milestone: M1
envs:
  - nemo_gym_env: escaped_nemo_env
    mix: rlhf
    status: active
    m0_env_id: escaped_env
""",
        encoding="utf-8",
    )
    index = tmp_path / "index" / "unified_index.yaml"
    index.parent.mkdir()
    index.write_text(
        """schema_version: 1
milestone: M1
registries:
  - id: escaped_data_registry
    kind: m0_data_registry
    path: ../outside_data_registry.yaml
    summary: escaped data fixture
  - id: escaped_bridge_registry
    kind: bridge_env_registry
    path: ../outside_bridge_registry.yaml
    summary: escaped bridge fixture
""",
        encoding="utf-8",
    )

    issues = validate_unified_index(index)

    assert len(issues) == 2
    assert all("must stay under registry root" in issue for issue in issues)
    assert "escaped-license" not in licenses_inventory(index)
    assert "escaped/dataset" not in hf_dataset_inventory(index)
    assert "escaped_env" not in m0_to_downstream_inventory(index)


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
    """M0 production datasets and required pref candidates carry pins.

    Post-task018-Session-2 ``nvidia/HelpSteer2`` appears in *two*
    registries — the m0_data row and the pref_data candidate row. The
    pref candidate keeps ``hf_revision_pin_required: true`` and now also
    carries its HF revision pin for source-lineage stability."""
    inventory = hf_dataset_inventory()
    gsm8k_entry = inventory["openai/gsm8k"][0]
    assert gsm8k_entry["hf_revision"], "gsm8k should be revision-pinned"

    helpsteer_pref_entries = [
        e for e in inventory["nvidia/HelpSteer2"]
        if e["kind"] == "pref_data_registry"
    ]
    assert helpsteer_pref_entries, "pref_data_registry entry for HelpSteer2 missing"
    assert helpsteer_pref_entries[0].get("hf_revision_pin_required") is True
    assert helpsteer_pref_entries[0].get("hf_revision") == (
        "990b2711a36180dd19d9c94b8627844866f8982a"
    )


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
