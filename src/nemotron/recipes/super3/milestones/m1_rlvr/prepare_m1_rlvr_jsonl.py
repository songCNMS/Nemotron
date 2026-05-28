#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 RLVR JSONL by bridging M0 NeMo-Gym JSONL into the RLVR mix.

M0 → RLVR{1,2,3} data bridge from `docs/implementation-roadmap.md` §1.3
(task014 + task015). M0 records already carry the NeMo-Gym contract
shape (``environment``, ``responses_create_params.{input,tools}``,
``reward_config``, ``extra_env_info``), so this bridge is *mapping +
slicing*, not converting.

Shared scaffolding lives in
``src/nemotron/recipes/super3/milestones/_bridge_base.py`` — this
module only carries RLVR-specific bits:

- 3 mixes (rlvr1 / rlvr2 / rlvr3) via ``MIX_ARTIFACTS`` → ``MIX_PROFILES``
- ``rlvr_env_registry.yaml`` is the source of truth (task015 Session 1
  registry-driven design). ``MIX_PROFILES`` is derived at import time;
  flipping a row from ``m0_missing`` to ``active`` lights up that env
  without Python edits.
"""

from __future__ import annotations

import argparse
import json
import logging
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
        RLVR1_ARTIFACT,
        RLVR2_ARTIFACT,
        RLVR3_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from nemotron.recipes.super3.milestones.lineage import (
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    # Fallback for direct-script execution (PEP 723 banner enables that).
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
        RLVR1_ARTIFACT,
        RLVR2_ARTIFACT,
        RLVR3_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from lineage import (
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

JsonDict = dict[str, Any]

MILESTONE = "M1"
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_rlvr")
USED_IN_TAG = "super3_rlvr1_v0"

REGISTRY_PATH = Path(__file__).with_name("rlvr_env_registry.yaml")
VALID_MIXES = frozenset({"rlvr1", "rlvr2", "rlvr3"})

MIX_ARTIFACTS: dict[str, str] = {
    "rlvr1": RLVR1_ARTIFACT,
    "rlvr2": RLVR2_ARTIFACT,
    "rlvr3": RLVR3_ARTIFACT,
}


def load_rlvr_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load ``rlvr_env_registry.yaml``."""
    return load_env_registry(path or REGISTRY_PATH, expected_mix=VALID_MIXES)


def coverage_report(registry: Sequence[Mapping[str, Any]], mix: str) -> JsonDict:
    """RLVR coverage report (per-mix view via base helper)."""
    return base_coverage_report(registry, mix_name=mix, filter_to_mix=True)


def build_mix_profiles(
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Compose ``MIX_PROFILES`` from the registry. Called at module import."""
    if registry is None:
        registry = load_rlvr_env_registry()
    profiles: dict[str, dict[str, Any]] = {}
    for mix, artifact in MIX_ARTIFACTS.items():
        profiles[mix] = {
            "artifact_type": artifact,
            "stage": f"M1 {mix.upper()}",
            "env_map": derive_env_map(registry, mix_name=mix),
            "used_in_tag": f"super3_{mix}_v0",
        }
    return profiles


try:
    _REGISTRY = load_rlvr_env_registry()
    MIX_PROFILES: dict[str, dict[str, Any]] = build_mix_profiles(_REGISTRY)
except (FileNotFoundError, ImportError):
    _REGISTRY = []
    MIX_PROFILES = {}

# Backward-compatible exports — registry-derived module-level constants.
RLVR1_ENV_MAP: dict[str, str] = MIX_PROFILES.get("rlvr1", {}).get("env_map", {})
RLVR2_ENV_MAP: dict[str, str] = MIX_PROFILES.get("rlvr2", {}).get("env_map", {})
RLVR3_ENV_MAP: dict[str, str] = MIX_PROFILES.get("rlvr3", {}).get("env_map", {})


def tag_record(
    record: Mapping[str, Any],
    *,
    nemo_gym_env: str,
    mix_name: str,
    row_index: int,
    split: str,
) -> JsonDict:
    """RLVR row tagger. No extra row fields beyond the base contract."""
    return base_tag_record(
        record,
        nemo_gym_env=nemo_gym_env,
        mix_name=mix_name,
        row_index=row_index,
        split=split,
        row_index_key="rlvr_row_index",
        split_key="rlvr_split",
    )


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        f"# M1 RLVR Bridge — {manifest['mix']} report",
        "",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- M0 input: `{manifest['m0_input_dir']}`",
        f"- Output: `{manifest['output_dir']}`",
        f"- Used-in tag: `{manifest['used_in_tag']}`",
        "",
        "## Mix counts (train)",
        "",
    ]
    for env, count in manifest["counts"]["train"].items():
        lines.append(f"- `{env}` → `{manifest['env_map'][env]}`: {count}")
    lines += ["", "## Mix counts (val)", ""]
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
    profile = MIX_PROFILES.get(args.mix)
    if profile is None:
        raise ValueError(
            f"unknown mix {args.mix!r}; known mixes: {sorted(MIX_PROFILES)}"
        )
    env_map = profile["env_map"]
    if not env_map:
        coverage = coverage_report(_REGISTRY, args.mix)
        raise ValueError(
            f"mix {args.mix!r} has no active M0 → NeMo-Gym mappings yet; "
            f"coverage: {coverage['counts']}. Unblocked by registering an "
            f"M0 source for one of: {coverage['m0_missing'] + coverage['blocked_external']}"
        )

    files_by_env = discover_m0_split_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    def _tag(record, m0_env, nemo_gym_env, row_index, split):
        return tag_record(
            record,
            nemo_gym_env=nemo_gym_env,
            mix_name=args.mix,
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

    # Also emit a combined jsonl (train rows first, val rows last) so
    # the existing ``stage2_rl/_data_prep_base.split_local_jsonl``
    # consumer can re-split at the same boundary idempotently. This is
    # the path ``data_prep/rlvr1.yaml`` ``input_path`` points at after
    # task014 Session 2; the pre-split train/val files remain for
    # downstream consumers that prefer them directly. (task014 Session 2)
    combined_path = args.output_dir / "combined.jsonl"
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
        "stage": profile["stage"],
        "mix": args.mix,
        "used_in_tag": profile["used_in_tag"],
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
        "coverage": coverage_report(_REGISTRY, args.mix),
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
            kind="m1_rlvr_train_jsonl",
            ref=str(train_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()),
            notes=f"NemoGymDataset train input for {args.mix}",
        ),
        LineageOutput(
            kind="m1_rlvr_val_jsonl",
            ref=str(val_path.relative_to(args.output_dir)),
            rows=sum(val_counts.values()),
            notes=f"NemoGymDataset val input for {args.mix}",
        ),
        LineageOutput(
            kind="m1_rlvr_combined_jsonl",
            ref=str(combined_path.relative_to(args.output_dir)),
            rows=sum(train_counts.values()) + sum(val_counts.values()),
            notes=(
                f"Combined train+val jsonl for {args.mix} — input to "
                "stage2_rl/_data_prep_base.split_local_jsonl"
            ),
        ),
    ]
    lineage_record = make_lineage_record(
        stage=profile["stage"],
        produced_by="prepare_m1_rlvr_jsonl.py",
        artifact_type=profile["artifact_type"],
        artifact_name=args.output_dir.name or f"m1_{args.mix}",
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
    parser.add_argument(
        "--mix",
        choices=sorted(MIX_PROFILES),
        default="rlvr1",
        help="Which RLVR mix to build. Available mixes derived from rlvr_env_registry.yaml.",
    )
    parser.add_argument("--max-records-per-env", type=int, default=None)
    parser.add_argument("--max-val-records-per-env", type=int, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare(args)
    except Exception as exc:  # noqa: BLE001 - CLI should render concise failures.
        print(f"prepare_m1_rlvr_jsonl.py: error: {exc}", file=sys.stderr)
        return 1
    # task069 Session 2: publish lineage to W&B if a run is active.
    # Auto-detects wandb.run; no-ops in sandbox / when wandb isn't installed.
    # Failure-tolerant — publishing never fails the prep.
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
