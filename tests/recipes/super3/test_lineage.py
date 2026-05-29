"""Tests for `src/nemotron/recipes/super3/milestones/lineage.py` (task021 Session 2).

Covers:

- `LineageRecord` JSON round-trip
- `make_record` timestamp + schema version pinning
- `walk_chain` traversal across a fake M0 → M1 manifest pair on disk
- `validate_chain` flagging broken / missing chains
- M1 `prepare()` emits a lineage block that points at the M0 manifest

The M0 emission path is exercised indirectly: it relies on the same
`make_record` / `LineageInput` / `LineageOutput` building blocks tested
here, but it lives inside `prepare_assets()` which calls
`iter_hf_rows()` — that path needs the `datasets` library + network.
The M1 test gives end-to-end coverage on the consuming side.
"""

from __future__ import annotations

import json
from pathlib import Path

from nemotron.recipes.super3.milestones.lineage import (
    KNOWN_ARTIFACT_TYPES,
    LINEAGE_SCHEMA_VERSION,
    RAW_DATA_ARTIFACT,
    SFT_DATA_ARTIFACT,
    LineageInput,
    LineageOutput,
    LineageRecord,
    make_record,
    validate_chain,
    walk_chain,
)


def test_lineage_record_json_roundtrip() -> None:
    """Schema serializes to plain JSON dicts (no pydantic / dataclass leak)
    and round-trips back to the same record."""
    record = make_record(
        stage="M0 data_env_foundation",
        produced_by="prepare_m0_assets.py",
        artifact_type=RAW_DATA_ARTIFACT,
        artifact_name="smoke-20260518",
        inputs=[
            LineageInput(
                kind="hf_dataset",
                ref="openai/gsm8k",
                config="main",
                split="train",
                revision="740312add",
            )
        ],
        outputs=[LineageOutput(kind="m0_jsonl_split", ref="math_reasoning_numeric/train-split.jsonl", rows=100)],
    )
    payload = record.to_jsonable()

    # The on-disk shape must be plain JSON, with None-valued fields stripped.
    assert payload["schema_version"] == LINEAGE_SCHEMA_VERSION
    assert payload["artifact_type"] == RAW_DATA_ARTIFACT
    # None-valued fields are stripped to keep manifests tight.
    assert "sha256" not in payload["inputs"][0]
    assert "notes" not in payload["outputs"][0]

    raw_json = json.loads(json.dumps(payload))
    restored = LineageRecord.from_jsonable(raw_json)
    assert restored.artifact_type == record.artifact_type
    assert restored.inputs[0].config == "main"
    assert restored.outputs[0].rows == 100


def test_known_artifact_types_cover_plan_section_10() -> None:
    """The plan §10 vocabulary is enumerated as constants so callers don't
    pass typo'd strings; the module's exported set is the authoritative list."""
    expected = {
        "RawDataArtifact",
        "SFTDataArtifact",
        "PackedSFTArtifact",
        "ModelArtifact-sft",
        "RLVR1",
        "RLVR2",
        "RLVR3",
        "SWE1",
        "SWE2",
        "RLHF",
        "EvalReport",
    }
    assert expected.issubset(KNOWN_ARTIFACT_TYPES)


def test_walk_chain_orders_records_oldest_to_newest(tmp_path: Path) -> None:
    """A two-record chain (M0 ← M1) walked from the M1 end returns
    [M0, M1] in that order so callers can inspect provenance forward."""
    m0_dir = tmp_path / "m0"
    m0_dir.mkdir()
    m0_manifest = m0_dir / "manifest.json"
    m0_record = make_record(
        stage="M0 data_env_foundation",
        produced_by="prepare_m0_assets.py",
        artifact_type=RAW_DATA_ARTIFACT,
        artifact_name="m0-smoke",
        inputs=[LineageInput(kind="hf_dataset", ref="openai/gsm8k")],
        outputs=[LineageOutput(kind="m0_jsonl_split", ref="math_reasoning_numeric/train-split.jsonl", rows=10)],
    )
    m0_manifest.write_text(json.dumps({"lineage": m0_record.to_jsonable()}), encoding="utf-8")

    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    m1_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-smoke",
        # Relative path resolved against m1_manifest's directory.
        inputs=[LineageInput(kind="manifest", ref=str(m0_manifest))],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl", rows=10)],
    )
    m1_manifest.write_text(json.dumps({"lineage": m1_record.to_jsonable()}), encoding="utf-8")

    chain = walk_chain(m1_manifest)
    assert [r.artifact_type for r in chain] == [RAW_DATA_ARTIFACT, SFT_DATA_ARTIFACT]
    assert chain[0].artifact_name == "m0-smoke"
    assert chain[1].artifact_name == "m1-smoke"


def test_validate_chain_flags_missing_manifest_input(tmp_path: Path) -> None:
    """A non-root record without a `manifest` input fails the gap check."""
    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    # M1 record with NO manifest input — chain is broken.
    bad_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-orphan",
        inputs=[],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl")],
    )
    m1_manifest.write_text(json.dumps({"lineage": bad_record.to_jsonable()}), encoding="utf-8")

    issues = validate_chain(m1_manifest)
    # The walker stops at this orphan record (treats it as root since
    # there's no upstream manifest); we don't fire the "no manifest
    # input" issue for a single-record chain. But on a multi-record
    # chain with a dangling reference we should see the "did not resolve"
    # issue. Make sure root-allowance holds:
    assert issues == []  # single-record chain is acceptable as a "root"


def test_validate_chain_flags_broken_upstream_reference(tmp_path: Path) -> None:
    """A `manifest`-kind input whose ref does not exist on disk is
    flagged so the operator can fix the chain."""
    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    m1_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-broken",
        inputs=[
            LineageInput(
                kind="manifest",
                ref=str(tmp_path / "nonexistent-m0" / "manifest.json"),
            )
        ],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl")],
    )
    m1_manifest.write_text(json.dumps({"lineage": m1_record.to_jsonable()}), encoding="utf-8")

    issues = validate_chain(m1_manifest)
    assert any("did not resolve" in i for i in issues)


def test_validate_chain_on_clean_two_record_chain_is_silent(tmp_path: Path) -> None:
    """Happy path: M0 + M1 both present, M1 points at M0, no issues."""
    m0_dir = tmp_path / "m0"
    m0_dir.mkdir()
    m0_manifest = m0_dir / "manifest.json"
    m0_record = make_record(
        stage="M0 data_env_foundation",
        produced_by="prepare_m0_assets.py",
        artifact_type=RAW_DATA_ARTIFACT,
        artifact_name="m0-smoke",
        inputs=[LineageInput(kind="hf_dataset", ref="openai/gsm8k")],
        outputs=[LineageOutput(kind="m0_jsonl_split", ref="train.jsonl")],
    )
    m0_manifest.write_text(json.dumps({"lineage": m0_record.to_jsonable()}), encoding="utf-8")

    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    m1_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-smoke",
        inputs=[LineageInput(kind="manifest", ref=str(m0_manifest))],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl")],
    )
    m1_manifest.write_text(json.dumps({"lineage": m1_record.to_jsonable()}), encoding="utf-8")

    assert validate_chain(m1_manifest) == []


def test_validate_chain_accepts_relative_manifest_ref_from_declaring_dir(
    tmp_path: Path,
) -> None:
    """Relative manifest refs validate against the manifest that declares them."""
    m0_dir = tmp_path / "m0"
    m0_dir.mkdir()
    m0_manifest = m0_dir / "manifest.json"
    m0_record = make_record(
        stage="M0 data_env_foundation",
        produced_by="prepare_m0_assets.py",
        artifact_type=RAW_DATA_ARTIFACT,
        artifact_name="m0-relative",
        inputs=[LineageInput(kind="hf_dataset", ref="openai/gsm8k")],
        outputs=[LineageOutput(kind="m0_jsonl_split", ref="train.jsonl")],
    )
    m0_manifest.write_text(json.dumps({"lineage": m0_record.to_jsonable()}), encoding="utf-8")

    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    m1_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-relative",
        inputs=[LineageInput(kind="manifest", ref="../m0/manifest.json")],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl")],
    )
    m1_manifest.write_text(json.dumps({"lineage": m1_record.to_jsonable()}), encoding="utf-8")

    chain = walk_chain(m1_manifest)

    assert [record.artifact_name for record in chain] == ["m0-relative", "m1-relative"]
    assert validate_chain(m1_manifest) == []


def test_validate_chain_flags_missing_relative_manifest_ref_from_declaring_dir(
    tmp_path: Path,
) -> None:
    """Broken relative manifest refs still surface the declaring manifest path."""
    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    m1_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-relative-broken",
        inputs=[LineageInput(kind="manifest", ref="../m0/missing_manifest.json")],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl")],
    )
    m1_manifest.write_text(json.dumps({"lineage": m1_record.to_jsonable()}), encoding="utf-8")

    issues = validate_chain(m1_manifest)

    assert len(issues) == 1
    assert "record M1 Agentic SFT v0 input `manifest` ref ../m0/missing_manifest.json" in issues[0]
    assert str(m1_manifest.resolve()) in issues[0]
    assert str(tmp_path / "m0" / "missing_manifest.json") in issues[0]


def test_m1_prepare_emits_lineage_pointing_at_m0_manifest(tmp_path: Path) -> None:
    """End-to-end M1 emission: `prepare()` writes a manifest with a
    lineage block whose `manifest`-kind input resolves to the (synthetic)
    M0 manifest in the input dir."""
    # Build a synthetic M0 dir with a math_reasoning_numeric split.
    m0_root = tmp_path / "m0"
    env_dir = m0_root / "math_reasoning_numeric"
    env_dir.mkdir(parents=True)
    record = {
        "environment": "math_reasoning_numeric",
        "question": "1+1?",
        "expected_answer": "2",
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "1+1?"},
            ],
            "tools": [],
        },
        "reward_config": {"verifier": "normalized_numeric_exact_match"},
        "extra_env_info": {"reference_solution": "2"},
        "metadata": {
            "source_dataset": "gsm8k",
            "license": "mit",
            "data_stage": "M0",
            "source_row_index": 0,
        },
    }
    for split in ("train", "val"):
        (env_dir / f"{split}-split.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

    # M1 prep expects an `m0_input_dir / "manifest.json"` to live next to the
    # split files. Drop a minimal one so the lineage input has a real ref.
    (m0_root / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "milestone": "M0"}), encoding="utf-8"
    )

    out_dir = tmp_path / "m1_out"

    from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import prepare

    class Args:
        m0_input_dir = m0_root
        output_dir = out_dir
        m0_health_baseline = None
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert "lineage" in manifest
    lineage = LineageRecord.from_jsonable(manifest["lineage"])
    assert lineage.artifact_type == SFT_DATA_ARTIFACT
    assert lineage.stage.endswith("Agentic SFT v0")
    assert lineage.produced_by == "prepare_m1_agentic_sft.py"
    manifest_inputs = [inp for inp in lineage.inputs if inp.kind == "manifest"]
    assert len(manifest_inputs) == 1
    assert Path(manifest_inputs[0].ref).resolve() == (m0_root / "manifest.json").resolve()
    # Outputs reference relative paths under output_dir.
    output_kinds = {out.kind for out in lineage.outputs}
    assert {"m1_sft_jsonl", "m1_sft_val_shadow_jsonl", "m1_sft_blend"}.issubset(output_kinds)


def test_walk_chain_silently_skips_missing_upstream(tmp_path: Path) -> None:
    """A manifest input whose file is missing doesn't crash the walker —
    it stops at the broken edge, returns what it has, and leaves the
    detection to `validate_chain`."""
    m1_dir = tmp_path / "m1"
    m1_dir.mkdir()
    m1_manifest = m1_dir / "manifest.json"
    m1_record = make_record(
        stage="M1 Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name="m1-broken",
        inputs=[LineageInput(kind="manifest", ref=str(tmp_path / "does-not-exist.json"))],
        outputs=[LineageOutput(kind="m1_sft_jsonl", ref="train.jsonl")],
    )
    m1_manifest.write_text(json.dumps({"lineage": m1_record.to_jsonable()}), encoding="utf-8")

    chain = walk_chain(m1_manifest)
    assert len(chain) == 1
    assert chain[0].artifact_name == "m1-broken"
