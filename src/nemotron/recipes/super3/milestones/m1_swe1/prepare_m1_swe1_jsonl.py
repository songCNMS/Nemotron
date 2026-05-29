#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 SWE1 JSONL by bridging M0 SWE pivot data into the
``swe_pivot_single_step_tool_use_with_argument_comparison`` env.

Shared scaffolding lives in
``src/nemotron/recipes/super3/milestones/_bridge_base.py``. This
module only carries SWE1-specific bits: single ``swe1`` mix, single
NeMo-Gym env target, ``swe1_env_registry.yaml`` source of truth.

Session 1 (task016) shipped this bridge as a verbatim copy of the
RLVR pattern. Session 4 (task017) factored the common helpers into
``_bridge_base``; from here, M0 SWE pivot data converter work
(task016 Session 2) only needs to flip a registry row to ``active``.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
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
        SWE1_ARTIFACT,
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
        SWE1_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from lineage import (
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

JsonDict = dict[str, Any]

MILESTONE = "M1"


def _output_base() -> Path:
    return Path(os.environ.get("NEMO_RUN_DIR", "."))


def _default_output_dir() -> Path:
    return _output_base() / "output/super3/m1_swe1"


DEFAULT_OUTPUT_DIR = _default_output_dir()
USED_IN_TAG = "super3_swe1_v0"
MIX_NAME = "swe1"

REGISTRY_PATH = Path(__file__).with_name("swe1_env_registry.yaml")


def load_swe1_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load ``swe1_env_registry.yaml``."""
    return load_env_registry(path or REGISTRY_PATH, expected_mix=MIX_NAME)


def coverage_report(registry: Sequence[Mapping[str, Any]]) -> JsonDict:
    """SWE1 coverage report (single mix, no extension fields)."""
    return base_coverage_report(registry, mix_name=MIX_NAME)


def build_mix_profile(
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compose the single SWE1 mix profile. Called at module import."""
    if registry is None:
        registry = load_swe1_env_registry()
    return {
        "artifact_type": SWE1_ARTIFACT,
        "stage": "M1 SWE1",
        "env_map": derive_env_map(registry),
        "used_in_tag": USED_IN_TAG,
    }


try:
    _REGISTRY = load_swe1_env_registry()
    SWE1_PROFILE: dict[str, Any] = build_mix_profile(_REGISTRY)
except (FileNotFoundError, ImportError):
    _REGISTRY = []
    SWE1_PROFILE = {}

SWE1_ENV_MAP: dict[str, str] = SWE1_PROFILE.get("env_map", {})


def tag_record(
    record: Mapping[str, Any],
    *,
    nemo_gym_env: str,
    row_index: int,
    split: str,
) -> JsonDict:
    """SWE1 row tagger. No extra row fields beyond the base contract."""
    return base_tag_record(
        record,
        nemo_gym_env=nemo_gym_env,
        mix_name=MIX_NAME,
        row_index=row_index,
        split=split,
        row_index_key="swe1_row_index",
        split_key="swe1_split",
    )


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        "# M1 SWE1 Bridge — swe1 report",
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
    if not SWE1_PROFILE:
        raise RuntimeError(
            "SWE1 profile unavailable (registry failed to load); reinstall pyyaml or check "
            f"{REGISTRY_PATH}"
        )
    env_map = SWE1_PROFILE["env_map"]
    if not env_map:
        coverage = coverage_report(_REGISTRY)
        raise ValueError(
            f"SWE1 mix has no active M0 → NeMo-Gym mappings yet; "
            f"coverage: {coverage['counts']}. Unblocked by registering an "
            f"M0 source for one of: "
            f"{coverage['m0_missing'] + coverage['verifier_mismatch'] + coverage['blocked_external']}"
        )

    files_by_env = discover_m0_split_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    def _tag(record, m0_env, nemo_gym_env, row_index, split):
        return tag_record(
            record,
            nemo_gym_env=nemo_gym_env,
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
        "stage": SWE1_PROFILE["stage"],
        "mix": MIX_NAME,
        "used_in_tag": SWE1_PROFILE["used_in_tag"],
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
            kind="m1_swe1_train_jsonl",
            ref=str(train_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()),
            notes="NemoGymDataset train input for swe1",
        ),
        LineageOutput(
            kind="m1_swe1_val_jsonl",
            ref=str(val_path.relative_to(args.output_dir)),
            rows=sum(val_counts.values()),
            notes="NemoGymDataset val input for swe1",
        ),
        LineageOutput(
            kind="m1_swe1_combined_jsonl",
            ref=str(combined_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()) + sum(val_counts.values()),
            notes=(
                "Combined train+val jsonl for swe1 input to "
                "stage2_rl/_data_prep_base.split_local_jsonl"
            ),
        ),
    ]
    lineage_record = make_lineage_record(
        stage=SWE1_PROFILE["stage"],
        produced_by="prepare_m1_swe1_jsonl.py",
        artifact_type=SWE1_PROFILE["artifact_type"],
        artifact_name=args.output_dir.name or "m1_swe1",
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
    parser.add_argument("--output-dir", type=Path, default=_default_output_dir())
    parser.add_argument("--max-records-per-env", type=int, default=None)
    parser.add_argument("--max-val-records-per-env", type=int, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare(args)
    except Exception as exc:  # noqa: BLE001
        print(f"prepare_m1_swe1_jsonl.py: error: {exc}", file=sys.stderr)
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
