#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 SWE2 JSONL + SIF resolver for the OpenHands SWE-Bench loop.

Two pieces:

1. **SIF image mapping registry** (roadmap §1.5 task017 first deliverable):
   ``swe2_sif_registry.yaml`` declares the three SIF filename families per
   ``stage2_swe2/config/default.yaml::container_formatter``. Python helpers
   ``resolve_sif_path`` / ``validate_sif_exists`` join a per-deployment
   ``sif_dir`` with the template and check the file exists before the
   cluster spends a slot waiting on a missing image.

2. **SWE2 bridge skeleton** using the shared ``_bridge_base`` scaffolding
   (task017 Session 4 extraction). SWE2-specific extensions on top of the
   base: ``sif_source`` row tag (from active registry rows) and
   ``sif_source_breakdown`` in the coverage block (per-family status
   histogram so coverage shows *which* container family still needs an
   M0 source).

Today active=0 → ``prepare()`` raises a coverage-aware error rather than
emitting empty files. Session 2 lands an M0 SWE pivot env and flips a
registry row to ``active``.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from nemotron.recipes.super3.milestones._bridge_base import (
        KNOWN_STATUSES,
        audit_bridge_data_quality,
        base_coverage_report,
        base_tag_record,
        collect_mix_rows,
        derive_env_map,
        discover_m0_split_files,
        load_env_registry,
        output_fingerprints_for_paths,
        read_jsonl,
        render_bridge_quality_report_sections,
        write_json,
        write_jsonl,
    )
    from nemotron.recipes.super3.milestones.lineage import (
        SWE2_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _bridge_base import (  # type: ignore[no-redef]
        KNOWN_STATUSES,
        audit_bridge_data_quality,
        base_coverage_report,
        base_tag_record,
        collect_mix_rows,
        derive_env_map,
        discover_m0_split_files,
        load_env_registry,
        output_fingerprints_for_paths,
        read_jsonl,
        render_bridge_quality_report_sections,
        write_json,
        write_jsonl,
    )
    from lineage import (  # type: ignore[no-redef]
        SWE2_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

JsonDict = dict[str, Any]

MILESTONE = "M1"
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_swe2")
USED_IN_TAG = "super3_swe2_v0"
MIX_NAME = "swe2"

ENV_REGISTRY_PATH = Path(__file__).with_name("swe2_env_registry.yaml")
SIF_REGISTRY_PATH = Path(__file__).with_name("swe2_sif_registry.yaml")

KNOWN_SIF_SOURCES = frozenset({"swebench", "swegym", "r2egym"})

# SWE-Bench instance ids are `<org>__<repo>-<number>` (e.g.,
# `astropy__astropy-12907`). Allow lowercase + digits + `_` + `-` only;
# anything else risks path-injection into the SIF filename.
_INSTANCE_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


# --- SIF image registry / resolver ---------------------------------------


def load_swe2_sif_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the SIF filename-template registry.

    task030 Session 4: row shape delegated to
    ``data_registries.schema.validate_rows`` (with ``fail_fast=True``).
    SWE2-specific source-vocabulary + filename-template format checks
    stay inline as ``extra_validators`` closures.
    """
    import yaml

    from nemotron.recipes.super3.milestones.data_registries.schema import (
        validate_rows,
        validate_top_level,
    )

    target = path or SIF_REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    validate_top_level(data, kind="sif_registry", source_path=target, strict=False)

    def _source_validator(row: JsonDict, index: int) -> str | None:
        source = row.get("source")
        if source is not None and source not in KNOWN_SIF_SOURCES:
            return (
                f"source {source!r} not in {sorted(KNOWN_SIF_SOURCES)} "
                "(extend KNOWN_SIF_SOURCES if a new family is added)"
            )
        return None

    def _template_validator(row: JsonDict, index: int) -> str | None:
        template = row.get("filename_template")
        if template is not None and "{instance_id}" not in template:
            return (
                f"filename_template {template!r} must contain '{{instance_id}}'"
            )
        return None

    validate_rows(
        data,
        kind="sif_registry",
        fail_fast=True,
        source_path=target,
        extra_validators=[_source_validator, _template_validator],
    )
    return data["sif_sources"]


def _sif_template_map(registry: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    return {row["source"]: row["filename_template"] for row in registry}


def resolve_sif_path(
    *,
    instance_id: str,
    source: str,
    sif_dir: Path | str,
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> Path:
    """Resolve an instance to its SIF path under *sif_dir*.

    Example:
        >>> resolve_sif_path(
        ...     instance_id="astropy__astropy-12907",
        ...     source="swebench",
        ...     sif_dir="/lustre/sif",
        ... )
        PosixPath('/lustre/sif/swebench_sweb.eval.x86_64.astropy__astropy-12907.sif')
    """
    if registry is None:
        registry = load_swe2_sif_registry()
    templates = _sif_template_map(registry)
    if source not in templates:
        raise ValueError(
            f"unknown SIF source {source!r}; known sources: {sorted(templates)}"
        )
    if not instance_id or not _INSTANCE_ID_RE.match(instance_id):
        raise ValueError(
            f"invalid instance_id {instance_id!r}: must match {_INSTANCE_ID_RE.pattern}"
        )
    filename = templates[source].format(instance_id=instance_id)
    return Path(sif_dir) / filename


def validate_sif_exists(path: Path) -> bool:
    """Check that an SIF file is reachable on disk."""
    return Path(path).is_file()


# --- SWE2 env registry / mix profile -------------------------------------


def _validate_sif_source_field(row: JsonDict, index: int) -> None:
    sif_source = row.get("sif_source")
    if sif_source is not None and sif_source not in KNOWN_SIF_SOURCES:
        raise ValueError(
            f"envs[{index}] sif_source {sif_source!r} not in {sorted(KNOWN_SIF_SOURCES)}"
        )


def load_swe2_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load ``swe2_env_registry.yaml`` with sif_source validation."""
    return load_env_registry(
        path or ENV_REGISTRY_PATH,
        expected_mix=MIX_NAME,
        extra_row_validator=_validate_sif_source_field,
    )


def coverage_report(registry: Sequence[Mapping[str, Any]]) -> JsonDict:
    """SWE2 coverage report with the SWE2-specific
    ``sif_source_breakdown`` extension on top of the base report."""
    report = base_coverage_report(registry, mix_name=MIX_NAME)
    by_sif_source: dict[str, list[str]] = defaultdict(list)
    for row in registry:
        sif_source = row.get("sif_source")
        if sif_source:
            by_sif_source[sif_source].append(row["status"])
    report["sif_source_breakdown"] = {
        source: dict(sorted({s: by_sif_source[source].count(s) for s in by_sif_source[source]}.items()))
        for source in sorted(by_sif_source)
    }
    return report


def build_mix_profile(
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compose the single SWE2 mix profile. Called at module import."""
    if registry is None:
        registry = load_swe2_env_registry()
    return {
        "artifact_type": SWE2_ARTIFACT,
        "stage": "M1 SWE2",
        "env_map": derive_env_map(registry),
        "used_in_tag": USED_IN_TAG,
    }


try:
    _REGISTRY = load_swe2_env_registry()
    SWE2_PROFILE: dict[str, Any] = build_mix_profile(_REGISTRY)
except (FileNotFoundError, ImportError):
    _REGISTRY = []
    SWE2_PROFILE = {}

SWE2_ENV_MAP: dict[str, str] = SWE2_PROFILE.get("env_map", {})


# --- Row tagging ---------------------------------------------------------


def tag_record(
    record: Mapping[str, Any],
    *,
    nemo_gym_env: str,
    sif_source: str | None,
    row_index: int,
    split: str,
) -> JsonDict:
    """SWE2 row tagger. Adds ``sif_source`` extra field (when an active
    registry row supplies it) so the OpenHands agent knows which
    container family to try."""
    extras = {"sif_source": sif_source} if sif_source is not None else None
    return base_tag_record(
        record,
        nemo_gym_env=nemo_gym_env,
        mix_name=MIX_NAME,
        row_index=row_index,
        split=split,
        extra_row_fields=extras,
        extra_metadata_fields=extras,
        row_index_key="swe2_row_index",
        split_key="swe2_split",
    )


def _m0_env_to_sif_source(registry: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    """Build a `{m0_env_id: sif_source}` lookup from active registry rows."""
    out: dict[str, str | None] = {}
    for row in registry:
        if row["status"] != "active":
            continue
        m0_env = row.get("m0_env_id")
        if not m0_env:
            continue
        out[m0_env] = row.get("sif_source")
    return out


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        "# M1 SWE2 Bridge — swe2 report",
        "",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- M0 input: `{manifest['m0_input_dir']}`",
        f"- Output: `{manifest['output_dir']}`",
        f"- Used-in tag: `{manifest['used_in_tag']}`",
        "",
        "## Counts (train)",
        "",
    ]
    for env, count in manifest["counts"]["train"].items():
        lines.append(f"- `{env}` → `{manifest['env_map'][env]}`: {count}")
    lines += ["", "## Counts (val)", ""]
    for env, count in manifest["counts"]["val"].items():
        lines.append(f"- `{env}` → `{manifest['env_map'][env]}`: {count}")
    coverage = manifest.get("coverage")
    if coverage:
        lines += [
            "",
            f"## Coverage ({coverage['total_target_envs']} target envs)",
            "",
            f"- active: {len(coverage['active'])} — {', '.join(f'`{e}`' for e in coverage['active']) or '(none)'}",
            (
                f"- m0_missing: {len(coverage['m0_missing'])} — "
                f"{', '.join(f'`{e}`' for e in coverage['m0_missing']) or '(none)'}"
            ),
            (
                f"- verifier_mismatch: {len(coverage['verifier_mismatch'])} — "
                f"{', '.join(f'`{e}`' for e in coverage['verifier_mismatch']) or '(none)'}"
            ),
            (
                f"- blocked_external: {len(coverage['blocked_external'])} — "
                f"{', '.join(f'`{e}`' for e in coverage['blocked_external']) or '(none)'}"
            ),
        ]
    lines.extend(
        render_bridge_quality_report_sections(
            manifest,
            fingerprint_keys=("train_path", "val_path"),
        )
    )
    if manifest["errors"]:
        lines += ["", "## Errors", ""]
        for error in manifest["errors"]:
            location = f"{error.get('environment', 'unknown')}/{error.get('split', 'unknown')}"
            lines.append(f"- `{location}`: {error['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(args: argparse.Namespace) -> JsonDict:
    if args.m0_input_dir is None:
        raise ValueError("--m0-input-dir is required")
    if not SWE2_PROFILE:
        raise RuntimeError(
            "SWE2 profile unavailable (registry failed to load); reinstall pyyaml or check "
            f"{ENV_REGISTRY_PATH}"
        )
    env_map = SWE2_PROFILE["env_map"]
    if not env_map:
        coverage = coverage_report(_REGISTRY)
        raise ValueError(
            f"SWE2 mix has no active M0 → NeMo-Gym mappings yet; "
            f"coverage: {coverage['counts']}. Unblocked by registering an "
            f"M0 source for one of: "
            f"{coverage['m0_missing'] + coverage['verifier_mismatch'] + coverage['blocked_external']}"
        )

    files_by_env = discover_m0_split_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    sif_source_lookup = _m0_env_to_sif_source(_REGISTRY)

    def _tag(record, m0_env, nemo_gym_env, row_index, split):
        return tag_record(
            record,
            nemo_gym_env=nemo_gym_env,
            sif_source=sif_source_lookup.get(m0_env),
            row_index=row_index,
            split=split,
        )

    train_rows, train_errors, train_counts = collect_mix_rows(
        files_by_env,
        env_map=env_map,
        split="train",
        max_records_per_env=args.max_records_per_env,
        tag_fn=_tag,
    )
    val_rows, val_errors, val_counts = collect_mix_rows(
        files_by_env,
        env_map=env_map,
        split="val",
        max_records_per_env=args.max_val_records_per_env,
        tag_fn=_tag,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.jsonl"
    val_path = args.output_dir / "val.jsonl"
    write_jsonl(train_path, train_rows)
    write_jsonl(val_path, val_rows)
    output_fingerprints = output_fingerprints_for_paths(
        {
            "train_path": train_path,
            "val_path": val_path,
        }
    )

    manifest: JsonDict = {
        "schema_version": 1,
        "milestone": MILESTONE,
        "stage": SWE2_PROFILE["stage"],
        "mix": MIX_NAME,
        "used_in_tag": SWE2_PROFILE["used_in_tag"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "m0_input_dir": str(args.m0_input_dir),
        "output_dir": str(args.output_dir),
        "train_path": str(train_path),
        "val_path": str(val_path),
        "env_map": dict(env_map),
        "counts": {
            "train": train_counts,
            "val": val_counts,
        },
        "coverage": coverage_report(_REGISTRY),
        "data_quality": audit_bridge_data_quality(
            train_rows=train_rows,
            val_rows=val_rows,
        ),
        "output_fingerprints": output_fingerprints,
        "errors": [*train_errors, *val_errors],
    }

    lineage_inputs = [
        LineageInput(
            kind="manifest",
            ref=str(args.m0_input_dir / "manifest.json"),
            notes="M0 RawDataArtifact",
        ),
    ]
    lineage_outputs = [
        LineageOutput(
            kind="m1_swe2_train_jsonl",
            ref=str(train_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()),
            notes="NemoGymDataset train input for swe2 (OpenHands loop)",
        ),
        LineageOutput(
            kind="m1_swe2_val_jsonl",
            ref=str(val_path.relative_to(args.output_dir)),
            rows=sum(val_counts.values()),
            notes="NemoGymDataset val input for swe2 (OpenHands loop)",
        ),
    ]
    lineage_record = make_lineage_record(
        stage=SWE2_PROFILE["stage"],
        produced_by="prepare_m1_swe2_jsonl.py",
        artifact_type=SWE2_PROFILE["artifact_type"],
        artifact_name=args.output_dir.name or "m1_swe2",
        inputs=lineage_inputs,
        outputs=lineage_outputs,
    )
    manifest["lineage"] = lineage_record.to_jsonable()

    write_json(args.output_dir / "manifest.json", manifest)
    write_report(args.output_dir / "report.md", manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m0-input-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-records-per-env", type=int, default=None)
    parser.add_argument("--max-val-records-per-env", type=int, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare(args)
    except Exception as exc:  # noqa: BLE001
        print(f"prepare_m1_swe2_jsonl.py: error: {exc}", file=sys.stderr)
        return 1
    # task069 Session 2: auto-publish lineage to W&B (no-op without active run).
    try:
        from nemotron.recipes.super3.milestones.lineage_publisher import (
            maybe_publish_lineage_from_manifest,
        )
        maybe_publish_lineage_from_manifest(args.output_dir / "manifest.json")
    except Exception:  # noqa: BLE001
        pass
    print(
        json.dumps(
            {
                "mix": manifest["mix"],
                "train_rows": sum(manifest["counts"]["train"].values()),
                "val_rows": sum(manifest["counts"]["val"].values()),
                "train_path": manifest["train_path"],
                "val_path": manifest["val_path"],
                "errors": len(manifest["errors"]),
            },
            indent=2,
        )
    )
    return 0 if not manifest["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
