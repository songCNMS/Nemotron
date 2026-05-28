#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 RLHF JSONL — fourth registry-driven bridge.

`stage2_rl/stage3_rlhf/config/default.yaml::nemo_gym.config_paths` loads
two env configs:

- ``genrm_compare`` (GenRM preference judge)
- ``single_step_tool_use_with_argument_comparison`` (parallel tool-call
  validity check per plan §5.6)

Shared scaffolding lives in
``src/nemotron/recipes/super3/milestones/_bridge_base.py`` (task017
Session 4). RLHF-specific extensions on top of the base:
``pref_dataset`` row tag (from active env_registry rows) +
``pref_dataset_breakdown`` + ``known_pref_candidates`` in the coverage
block. Today active=0 → ``prepare()`` raises a coverage-aware error
listing the gap and the candidate registry's known sources.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from nemotron.recipes.super3.milestones._bridge_base import (
        KNOWN_STATUSES as KNOWN_STATUSES,
    )
    from nemotron.recipes.super3.milestones._bridge_base import (
        audit_bridge_data_quality,
        base_coverage_report,
        base_tag_record,
        collect_mix_rows,
        derive_env_map,
        discover_m0_split_files,
        load_env_registry,
        output_fingerprints_for_paths,
        render_bridge_quality_report_sections,
        write_json,
        write_jsonl,
    )
    from nemotron.recipes.super3.milestones.lineage import (
        RLHF_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from nemotron.recipes.super3.milestones.lineage import (
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _bridge_base import (  # type: ignore[no-redef]
        KNOWN_STATUSES as KNOWN_STATUSES,
    )
    from _bridge_base import (
        audit_bridge_data_quality,
        base_coverage_report,
        base_tag_record,
        collect_mix_rows,
        derive_env_map,
        discover_m0_split_files,
        load_env_registry,
        output_fingerprints_for_paths,
        render_bridge_quality_report_sections,
        write_json,
        write_jsonl,
    )
    from lineage import (  # type: ignore[no-redef]
        RLHF_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from lineage import (
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

JsonDict = dict[str, Any]

MILESTONE = "M1"
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_rlhf")
USED_IN_TAG = "super3_rlhf_v0"
MIX_NAME = "rlhf"

ENV_REGISTRY_PATH = Path(__file__).with_name("rlhf_env_registry.yaml")
PREF_DATA_REGISTRY_PATH = Path(__file__).with_name("rlhf_pref_data_registry.yaml")


# --- Preference-data candidate registry ----------------------------------


def load_rlhf_pref_data_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the preference-data candidate registry (HelpSteer-2 /
    UltraFeedback / Orca DPO pairs).

    task030 Session 4: row shape delegated to
    ``data_registries.schema.validate_rows`` (fail_fast=True). The
    pref-data registry has no module-specific row checks today;
    schema-layer ``required_row_fields`` covers id / hf_dataset /
    license enforcement.
    """
    import yaml

    from nemotron.recipes.super3.milestones.data_registries.schema import (
        validate_rows,
        validate_top_level,
    )

    target = path or PREF_DATA_REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    validate_top_level(data, kind="pref_data_registry", source_path=target, strict=False)
    validate_rows(
        data,
        kind="pref_data_registry",
        fail_fast=True,
        source_path=target,
    )
    return data["datasets"]


def pref_candidate_ids(registry: Sequence[Mapping[str, Any]]) -> list[str]:
    return sorted(str(row["id"]) for row in registry)


# --- RLHF env registry + mix profile -------------------------------------


def load_rlhf_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load ``rlhf_env_registry.yaml``."""
    return load_env_registry(path or ENV_REGISTRY_PATH, expected_mix=MIX_NAME)


def coverage_report(
    registry: Sequence[Mapping[str, Any]],
    pref_data_registry: Sequence[Mapping[str, Any]] | None = None,
) -> JsonDict:
    """RLHF coverage report with ``pref_dataset_breakdown`` (per-candidate
    status histogram derived from env registry rows) + ``known_pref_candidates``
    (id list from the pref-data registry) on top of the base report."""
    report = base_coverage_report(registry, mix_name=MIX_NAME)
    by_pref: dict[str, list[str]] = defaultdict(list)
    for row in registry:
        pref = row.get("pref_dataset_candidate")
        if pref:
            by_pref[pref].append(row["status"])
    report["pref_dataset_breakdown"] = {
        pref: dict(sorted({s: by_pref[pref].count(s) for s in by_pref[pref]}.items()))
        for pref in sorted(by_pref)
    }
    report["known_pref_candidates"] = (
        pref_candidate_ids(pref_data_registry) if pref_data_registry is not None else []
    )
    return report


def build_mix_profile(
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compose the single RLHF mix profile. Called at module import."""
    if registry is None:
        registry = load_rlhf_env_registry()
    return {
        "artifact_type": RLHF_ARTIFACT,
        "stage": "M1 RLHF",
        "env_map": derive_env_map(registry),
        "used_in_tag": USED_IN_TAG,
    }


try:
    _REGISTRY = load_rlhf_env_registry()
    _PREF_DATA_REGISTRY = load_rlhf_pref_data_registry()
    RLHF_PROFILE: dict[str, Any] = build_mix_profile(_REGISTRY)
except (FileNotFoundError, ImportError):
    _REGISTRY = []
    _PREF_DATA_REGISTRY = []
    RLHF_PROFILE = {}

RLHF_ENV_MAP: dict[str, str] = RLHF_PROFILE.get("env_map", {})


# --- Row tagging ---------------------------------------------------------


def tag_record(
    record: Mapping[str, Any],
    *,
    nemo_gym_env: str,
    pref_dataset: str | None,
    row_index: int,
    split: str,
) -> JsonDict:
    """RLHF row tagger. Adds ``pref_dataset`` when an active registry
    row supplies it — the NeMo-Gym GenRM env routes by env name plus the
    pref dataset hint for analytics."""
    extras = {"pref_dataset": pref_dataset} if pref_dataset is not None else None
    return base_tag_record(
        record,
        nemo_gym_env=nemo_gym_env,
        mix_name=MIX_NAME,
        row_index=row_index,
        split=split,
        extra_row_fields=extras,
        extra_metadata_fields=extras,
        row_index_key="rlhf_row_index",
        split_key="rlhf_split",
    )


def _m0_env_to_pref_dataset(registry: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for row in registry:
        if row["status"] != "active":
            continue
        m0_env = row.get("m0_env_id")
        if not m0_env:
            continue
        out[m0_env] = row.get("pref_dataset_candidate")
    return out


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        "# M1 RLHF Bridge — rlhf report",
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
            f"- known pref candidates: {', '.join(f'`{c}`' for c in coverage['known_pref_candidates']) or '(none)'}",
        ]
    lines.extend(
        render_bridge_quality_report_sections(
            manifest,
            fingerprint_keys=("train_path", "val_path", "combined_path"),
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
    if not RLHF_PROFILE:
        raise RuntimeError(
            "RLHF profile unavailable (registry failed to load); reinstall pyyaml or check "
            f"{ENV_REGISTRY_PATH}"
        )
    env_map = RLHF_PROFILE["env_map"]
    if not env_map:
        coverage = coverage_report(_REGISTRY, _PREF_DATA_REGISTRY)
        raise ValueError(
            f"RLHF mix has no active M0 → NeMo-Gym mappings yet; "
            f"coverage: {coverage['counts']}. Unblocked by registering an "
            f"M0 source for one of: "
            f"{coverage['m0_missing'] + coverage['verifier_mismatch'] + coverage['blocked_external']}. "
            f"Candidate pref data sources: {coverage['known_pref_candidates']}"
        )

    files_by_env = discover_m0_split_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    pref_lookup = _m0_env_to_pref_dataset(_REGISTRY)

    def _tag(record, m0_env, nemo_gym_env, row_index, split):
        return tag_record(
            record,
            nemo_gym_env=nemo_gym_env,
            pref_dataset=pref_lookup.get(m0_env),
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
    combined_path = args.output_dir / "combined.jsonl"
    write_jsonl(train_path, train_rows)
    write_jsonl(val_path, val_rows)
    write_jsonl(combined_path, [*train_rows, *val_rows])
    output_fingerprints = output_fingerprints_for_paths(
        {
            "train_path": train_path,
            "val_path": val_path,
            "combined_path": combined_path,
        }
    )

    manifest: JsonDict = {
        "schema_version": 1,
        "milestone": MILESTONE,
        "stage": RLHF_PROFILE["stage"],
        "mix": MIX_NAME,
        "used_in_tag": RLHF_PROFILE["used_in_tag"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "m0_input_dir": str(args.m0_input_dir),
        "output_dir": str(args.output_dir),
        "train_path": str(train_path),
        "val_path": str(val_path),
        "combined_path": str(combined_path),
        "env_map": dict(env_map),
        "counts": {
            "train": train_counts,
            "val": val_counts,
        },
        "coverage": coverage_report(_REGISTRY, _PREF_DATA_REGISTRY),
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
            kind="m1_rlhf_train_jsonl",
            ref=str(train_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()),
            notes="NemoGymDataset train input for RLHF (GenRM judge)",
        ),
        LineageOutput(
            kind="m1_rlhf_val_jsonl",
            ref=str(val_path.relative_to(args.output_dir)),
            rows=sum(val_counts.values()),
            notes="NemoGymDataset val input for RLHF",
        ),
        LineageOutput(
            kind="m1_rlhf_combined_jsonl",
            ref=str(combined_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()) + sum(val_counts.values()),
            notes=(
                "Combined train+val jsonl for RLHF input to "
                "stage2_rl/_data_prep_base.split_local_jsonl"
            ),
        ),
    ]
    lineage_record = make_lineage_record(
        stage=RLHF_PROFILE["stage"],
        produced_by="prepare_m1_rlhf_jsonl.py",
        artifact_type=RLHF_PROFILE["artifact_type"],
        artifact_name=args.output_dir.name or "m1_rlhf",
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
        print(f"prepare_m1_rlhf_jsonl.py: error: {exc}", file=sys.stderr)
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
