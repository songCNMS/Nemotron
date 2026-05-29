"""Tests for the M0 → M1 RLVR data bridge (task014 Session 1, task015 Session 1).

Covers:

- Registry loader returns 21 NeMo-Gym envs with valid statuses
- ``RLVR1_ENV_MAP`` matches the post-audit registry (task015 Session 1 corrected
  the task014-era names against ``stage1_rlvr/config/default.yaml``)
- RLVR2 has registry-derived active mappings (math_with_judge + structured_outputs_json)
- ``prepare()`` writes ``train.jsonl`` / ``val.jsonl`` / ``manifest.json``
- Output rows carry ``nemo_gym_env`` + ``nemo_gym_mix`` tags
- M0 envs outside the mix are filtered out
- Missing splits surface in ``manifest.errors``
- Lineage block declares the correct RLVR{1,2,3} artifact pointing at the M0 manifest
- ``coverage`` block reports per-status env lists in the manifest + report
- Unknown mix raises with clear message
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from nemotron.recipes.super3.milestones.lineage import (
    RLVR1_ARTIFACT,
    RLVR2_ARTIFACT,
    LineageRecord,
)
from nemotron.recipes.super3.milestones.m1_rlhf.prepare_m1_rlhf_jsonl import (
    load_rlhf_env_registry,
)
from nemotron.recipes.super3.milestones.m1_rlvr.prepare_m1_rlvr_jsonl import (
    KNOWN_STATUSES,
    MIX_PROFILES,
    REGISTRY_PATH,
    RLVR1_ENV_MAP,
    RLVR2_ENV_MAP,
    RLVR3_ENV_MAP,
    coverage_report,
    derive_env_map,
    load_rlvr_env_registry,
    prepare,
    tag_record,
)
from nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl import (
    load_swe1_env_registry,
)
from nemotron.recipes.super3.milestones.m1_swe2.prepare_m1_swe2_jsonl import (
    load_swe2_env_registry,
)

ACTIVE_ROW_METADATA_FIELDS = (
    "m0_env_id",
    "m0_verifier",
    "nemo_gym_verifier",
    "license",
)
PLACEHOLDER_LICENSES = (
    "unknown",
    "unknown-pending-review",
    "unknown_pending_legal_review",
    "license-pending-legal-review",
    "placeholder-pending-source-selection",
    "placeholder-pending-source-pin",
)
BRIDGE_REGISTRY_LOADERS = (
    ("rlvr", load_rlvr_env_registry),
    ("swe1", load_swe1_env_registry),
    ("swe2", load_swe2_env_registry),
    ("rlhf", load_rlhf_env_registry),
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


def _write_registry(path: Path, row: Mapping[str, Any]) -> None:
    lines = ["schema_version: 1", "envs:", "  -"]
    for field, value in row.items():
        rendered = "null" if value is None else json.dumps(value)
        lines.append(f"    {field}: {rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _args(m0_root: Path, out_dir: Path, *, mix: str = "rlvr1") -> argparse.Namespace:
    return argparse.Namespace(
        m0_input_dir=m0_root,
        output_dir=out_dir,
        mix=mix,
        max_records_per_env=None,
        max_val_records_per_env=None,
    )


# ---------- Registry-level tests (task015 Session 1) ----------


def test_registry_loads_with_expected_shape() -> None:
    """The on-disk registry must parse, declare ≥ 21 envs (one per
    NeMo-Gym server config in `stage1_rlvr/config/default.yaml`), and
    use only the four known statuses."""
    registry = load_rlvr_env_registry()
    assert len(registry) >= 21, "expected ≥ 21 envs (one per stage1_rlvr default.yaml config)"
    # Every row has the contract fields.
    for row in registry:
        assert {"nemo_gym_env", "mix", "status"} <= row.keys()
        assert row["status"] in KNOWN_STATUSES
        assert row["mix"] in {"rlvr1", "rlvr2", "rlvr3"}


def test_bundled_active_bridge_rows_have_complete_source_metadata() -> None:
    """All active rows across bridge registries must carry lineage metadata."""
    active_counts: dict[str, int] = {}
    for label, loader in BRIDGE_REGISTRY_LOADERS:
        active_rows = [row for row in loader() if row["status"] == "active"]
        active_counts[label] = len(active_rows)
        assert active_rows, f"{label} registry should have at least one active row"
        for row in active_rows:
            missing = [
                field
                for field in ACTIVE_ROW_METADATA_FIELDS
                if row.get(field) is None or str(row.get(field)).strip() == ""
            ]
            assert missing == [], f"{label} active row {row['nemo_gym_env']!r} missing {missing}"
            assert str(row["license"]).strip().lower() not in PLACEHOLDER_LICENSES

    assert set(active_counts) == {"rlvr", "swe1", "swe2", "rlhf"}


def test_registry_path_resolves_to_yaml_in_module() -> None:
    """The bundled registry must live next to the script so direct-script
    execution (PEP 723 banner) and packaged import both find it."""
    assert REGISTRY_PATH.is_file()
    assert REGISTRY_PATH.suffix == ".yaml"
    assert REGISTRY_PATH.parent.name == "m1_rlvr"


def test_registry_rejects_unknown_status(tmp_path: Path) -> None:
    """Authorship sanity check — typos in `status` must be caught at load
    time so a bad commit doesn't make the bridge silently skip rows."""
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
envs:
  - nemo_gym_env: stub
    mix: rlvr1
    status: definitely-not-a-status
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="status"):
        load_rlvr_env_registry(bad)


@pytest.mark.parametrize("missing_field", ACTIVE_ROW_METADATA_FIELDS)
def test_registry_rejects_active_rows_missing_source_metadata(
    tmp_path: Path,
    missing_field: str,
) -> None:
    row: dict[str, Any] = {
        "nemo_gym_env": "stub",
        "mix": "rlvr1",
        "m0_env_id": "m0_stub",
        "m0_verifier": "exact_match",
        "nemo_gym_verifier": "exact_match",
        "license": "apache-2.0",
        "status": "active",
    }
    row.pop(missing_field)
    bad = tmp_path / "registry.yaml"
    _write_registry(bad, row)

    with pytest.raises(ValueError, match=rf"active row requires non-empty '{missing_field}'"):
        load_rlvr_env_registry(bad)


@pytest.mark.parametrize("license_value", (*PLACEHOLDER_LICENSES, "   "))
def test_registry_rejects_active_rows_with_placeholder_license(
    tmp_path: Path,
    license_value: str,
) -> None:
    bad = tmp_path / "registry.yaml"
    _write_registry(
        bad,
        {
            "nemo_gym_env": "stub",
            "mix": "rlvr1",
            "m0_env_id": "m0_stub",
            "m0_verifier": "exact_match",
            "nemo_gym_verifier": "exact_match",
            "license": license_value,
            "status": "active",
        },
    )

    with pytest.raises(ValueError, match="active row .*license"):
        load_rlvr_env_registry(bad)


def test_registry_allows_inactive_rows_with_pending_source_metadata(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yaml"
    _write_registry(
        registry_path,
        {
            "nemo_gym_env": "stub",
            "mix": "rlvr1",
            "m0_env_id": None,
            "m0_verifier": None,
            "nemo_gym_verifier": "",
            "license": "unknown-pending-review",
            "status": "m0_missing",
        },
    )

    registry = load_rlvr_env_registry(registry_path)

    assert registry[0]["status"] == "m0_missing"


def test_derive_env_map_filters_to_active_with_m0_source(tmp_path: Path) -> None:
    """Only `active` rows with a concrete `m0_env_id` count."""
    fake_registry = [
        {"nemo_gym_env": "ngym_a", "mix": "rlvr1", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "ngym_b", "mix": "rlvr1", "m0_env_id": None, "status": "m0_missing"},
        {"nemo_gym_env": "ngym_c", "mix": "rlvr1", "m0_env_id": "m0_c", "status": "verifier_mismatch"},
        {"nemo_gym_env": "ngym_d", "mix": "rlvr2", "m0_env_id": "m0_d", "status": "active"},
    ]
    assert derive_env_map(fake_registry, "rlvr1") == {"m0_a": "ngym_a"}
    assert derive_env_map(fake_registry, "rlvr2") == {"m0_d": "ngym_d"}
    assert derive_env_map(fake_registry, "rlvr3") == {}


def test_derive_env_map_rejects_conflicting_active_rows() -> None:
    """Two `active` rows claiming the same M0 env for different NeMo-Gym
    targets is an authorship bug — must raise instead of silently picking one."""
    fake_registry = [
        {"nemo_gym_env": "ngym_a", "mix": "rlvr1", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "ngym_other", "mix": "rlvr1", "m0_env_id": "m0_a", "status": "active"},
    ]
    with pytest.raises(ValueError, match="two active mappings"):
        derive_env_map(fake_registry, "rlvr1")


def test_coverage_report_counts_statuses_per_mix() -> None:
    fake_registry = [
        {"nemo_gym_env": "a", "mix": "rlvr2", "m0_env_id": "m0_a", "status": "active"},
        {"nemo_gym_env": "b", "mix": "rlvr2", "m0_env_id": None, "status": "m0_missing"},
        {"nemo_gym_env": "c", "mix": "rlvr2", "m0_env_id": "m0_c", "status": "verifier_mismatch"},
        {"nemo_gym_env": "d", "mix": "rlvr2", "m0_env_id": None, "status": "blocked_external"},
        {"nemo_gym_env": "x", "mix": "rlvr3", "m0_env_id": None, "status": "m0_missing"},
    ]
    coverage = coverage_report(fake_registry, "rlvr2")
    assert coverage["mix"] == "rlvr2"
    assert coverage["total_target_envs"] == 4
    assert coverage["counts"] == {
        "active": 1,
        "m0_missing": 1,
        "verifier_mismatch": 1,
        "blocked_external": 1,
    }
    assert coverage["active"] == ["a"]
    assert coverage["m0_missing"] == ["b"]


# ---------- RLVR1 / RLVR2 mix shape (post-audit) ----------


def test_rlvr1_env_map_post_audit_matches_default_yaml() -> None:
    """task015 Session 1 audited RLVR1_ENV_MAP against
    `stage1_rlvr/config/default.yaml::nemo_gym.config_paths` and corrected
    two task014-era names that did not exist on the NeMo-Gym side:

      - `general_tool_calling` was renamed to
        `single_step_tool_use_with_argument_comparison` (verifier semantics
        match: both compare emitted tool-call arguments against a schema)
      - `search_grounded_qa` was removed from active rlvr1 — there is no
        single-hop QA env in `default.yaml`, and HotpotQA shape does not
        fit `search_pivot_single_step_tool_use_with_argument_comparison`.
        It now lives in the registry as `m0_missing` so the gap is visible
        in the coverage report.
    """
    assert RLVR1_ENV_MAP == {
        "math_reasoning_numeric": "math_with_judge",
        "code_execution_python": "code_gen",
        "general_tool_calling": "single_step_tool_use_with_argument_comparison",
    }
    assert MIX_PROFILES["rlvr1"]["env_map"] == RLVR1_ENV_MAP
    assert MIX_PROFILES["rlvr1"]["artifact_type"] == RLVR1_ARTIFACT


def test_rlvr2_now_has_active_envs_from_m0_today() -> None:
    """task015 Session 1: rlvr2 is no longer empty. Whatever M0 envs the
    registry marks `active` for `mix: rlvr2` make it in, even before
    task057 finishes M0 expansion."""
    assert RLVR2_ENV_MAP, "rlvr2 should have at least one active mapping from M0 today"
    # Math competition and structured outputs already exist in M0 main.
    assert "math_competition_numeric" in RLVR2_ENV_MAP
    assert RLVR2_ENV_MAP["math_competition_numeric"] == "math_with_judge"
    assert "structured_outputs_json" in RLVR2_ENV_MAP
    assert RLVR2_ENV_MAP["structured_outputs_json"] == "structured_outputs_json"
    assert MIX_PROFILES["rlvr2"]["artifact_type"] == RLVR2_ARTIFACT


def test_rlvr3_active_map_reflects_registry_judgement() -> None:
    """rlvr3 currently has no `active` rows (everything is m0_missing,
    verifier_mismatch, or blocked_external) — calling prepare on rlvr3
    should raise a coverage-aware error rather than emit an empty file."""
    assert RLVR3_ENV_MAP == {}


# ---------- tag_record + prepare end-to-end ----------


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
    """End-to-end happy path: 2 rows per env across the 3-env post-audit
    rlvr1 mix (math, code, single-step tool use)."""
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
    expected_envs = len(RLVR1_ENV_MAP)
    assert len(train_rows) == 2 * expected_envs
    assert len(val_rows) == 1 * expected_envs
    assert manifest["mix"] == "rlvr1"
    assert manifest["counts"]["train"] == {env: 2 for env in RLVR1_ENV_MAP}
    assert manifest["counts"]["val"] == {env: 1 for env in RLVR1_ENV_MAP}
    assert manifest["errors"] == []
    assert manifest["data_quality"]["source_metadata"]["train"]["rows"] == len(train_rows)
    assert manifest["data_quality"]["source_metadata"]["val"]["rows"] == len(val_rows)
    assert set(manifest["output_fingerprints"]) == {
        "train_path",
        "val_path",
        "combined_path",
    }
    assert manifest["output_fingerprints"]["train_path"] == hashlib.sha256(
        train_path.read_bytes()
    ).hexdigest()
    report_md = (out_dir / "report.md").read_text(encoding="utf-8")
    assert "## Data quality audit" in report_md
    assert "## Output fingerprints" in report_md
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
    # Other rlvr1 envs absent from M0 → "not in M0 mix" on both splits.
    for missing_env in (env for env in RLVR1_ENV_MAP if env != "math_reasoning_numeric"):
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


def test_prepare_manifest_includes_coverage_block(tmp_path: Path) -> None:
    """task015 Session 1: every emitted manifest carries a `coverage` block
    summarising registry status counts for the mix being prepared."""
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

    coverage = manifest["coverage"]
    assert coverage["mix"] == "rlvr1"
    # The active count must match the post-audit env_map cardinality.
    assert coverage["counts"]["active"] == len(RLVR1_ENV_MAP)
    # search_pivot_... is registered as m0_missing in rlvr1.
    assert "search_pivot_single_step_tool_use_with_argument_comparison" in coverage["m0_missing"]


def test_prepare_rlvr2_emits_correct_artifact_and_coverage(tmp_path: Path) -> None:
    """rlvr2 with the M0 envs the registry marks active (math_competition_numeric
    + structured_outputs_json) writes a real artifact and a coverage report."""
    env_rows = {
        m0_env: {
            "train": [_m0_record(m0_env, "q", "a") for _ in range(3)],
            "val": [_m0_record(m0_env, "q", "a") for _ in range(2)],
        }
        for m0_env in RLVR2_ENV_MAP
    }
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr2_out"

    manifest = prepare(_args(m0_root, out_dir, mix="rlvr2"))

    assert manifest["mix"] == "rlvr2"
    lineage = LineageRecord.from_jsonable(manifest["lineage"])
    assert lineage.artifact_type == RLVR2_ARTIFACT
    # Coverage reports the m0_missing rlvr2 envs so the operator sees what
    # task057 still owes.
    assert manifest["coverage"]["counts"]["active"] == len(RLVR2_ENV_MAP)
    assert manifest["coverage"]["m0_missing"], "rlvr2 should still have m0_missing envs (task057)"


def test_prepare_rlvr3_raises_coverage_aware_error(tmp_path: Path) -> None:
    """rlvr3 has no active rows yet — calling prepare must raise an error
    that lists the gap (which envs are missing / blocked) so the operator
    can act on it."""
    env_rows = {"math_reasoning_numeric": {"train": [], "val": []}}
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr3_out"

    with pytest.raises(ValueError, match="no active M0"):
        prepare(_args(m0_root, out_dir, mix="rlvr3"))


def test_prepare_rejects_unknown_mix(tmp_path: Path) -> None:
    env_rows = {env: {"train": [], "val": []} for env in RLVR1_ENV_MAP}
    m0_root = _build_m0_dir(tmp_path, env_rows=env_rows)
    out_dir = tmp_path / "rlvr1_out"

    # argparse `choices=` would catch this at CLI parse time; calling prepare
    # directly bypasses argparse and lands inside the MIX_PROFILES lookup.
    with pytest.raises(ValueError, match="unknown mix"):
        prepare(_args(m0_root, out_dir, mix="not_a_mix"))
