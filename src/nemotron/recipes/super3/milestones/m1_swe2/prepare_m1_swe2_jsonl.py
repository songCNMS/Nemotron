#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 SWE2 JSONL + SIF resolver for the OpenHands SWE-Bench loop.

Two pieces in one module:

1. **SIF image mapping registry** (roadmap §1.5 task017 first deliverable):
   ``swe2_sif_registry.yaml`` declares the three SIF filename families per
   ``stage2_swe2/config/default.yaml::container_formatter``. Python helpers
   ``resolve_sif_path`` / ``validate_sif_exists`` join a per-deployment
   ``sif_dir`` with the template and check the file exists before the
   cluster spends a slot waiting on a missing image.

2. **SWE2 bridge skeleton** (third copy of the bridge — RLVR + SWE1 are
   the prior two). Reads M0 split files, filters + tags rows for the
   ``swe_agents`` NeMo-Gym agent, emits ``train.jsonl`` / ``val.jsonl`` /
   ``manifest.json`` with a ``coverage`` block + a ``SWE2_ARTIFACT``
   lineage record pointing at the M0 manifest. Today active=0 → ``prepare()``
   raises a coverage-aware error rather than emitting empty files.

Code duplication note: ~80% overlap with m1_rlvr + m1_swe1 bridges.
Extraction to `_bridge_base.py` deserves its own PR after this lands;
inline-as-third-copy keeps task017 reviewable and avoids reshaping during
the SWE2 infra build-out.
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

# SWE-Bench instance ids are `<org>__<repo>-<number>` (e.g.,
# `astropy__astropy-12907`). Allow lowercase + digits + `_` + `-` only;
# anything else risks path-injection into the SIF filename.
_INSTANCE_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")

try:
    from nemotron.recipes.super3.milestones.lineage import (
        SWE2_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
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

STATUS_ACTIVE = "active"
STATUS_M0_MISSING = "m0_missing"
STATUS_VERIFIER_MISMATCH = "verifier_mismatch"
STATUS_BLOCKED_EXTERNAL = "blocked_external"
KNOWN_STATUSES = frozenset(
    {STATUS_ACTIVE, STATUS_M0_MISSING, STATUS_VERIFIER_MISMATCH, STATUS_BLOCKED_EXTERNAL}
)

KNOWN_SIF_SOURCES = frozenset({"swebench", "swegym", "r2egym"})


# --- SIF image registry / resolver ---------------------------------------


def load_swe2_sif_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the SIF filename-template registry."""
    import yaml

    target = path or SIF_REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "sif_sources" not in data:
        raise ValueError(f"{target}: SIF registry must declare a 'sif_sources' list")
    rows = data["sif_sources"]
    if not isinstance(rows, list):
        raise ValueError(f"{target}: 'sif_sources' must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{target}: sif_sources[{index}] must be a mapping")
        for required in ("source", "filename_template"):
            if required not in row:
                raise ValueError(
                    f"{target}: sif_sources[{index}] missing required field {required!r}"
                )
        if row["source"] not in KNOWN_SIF_SOURCES:
            raise ValueError(
                f"{target}: sif_sources[{index}] source {row['source']!r} "
                f"not in {sorted(KNOWN_SIF_SOURCES)} "
                f"(extend KNOWN_SIF_SOURCES if a new family is added)"
            )
        if "{instance_id}" not in row["filename_template"]:
            raise ValueError(
                f"{target}: sif_sources[{index}] filename_template "
                f"{row['filename_template']!r} must contain '{{instance_id}}'"
            )
    return rows


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
        # Path-injection guard: instance_ids come from M0 data and end up
        # interpolated into filesystem paths. SWE-Bench instance ids are
        # `<org>__<repo>-<number>` (alphanumeric + `_` + `-`) — anything
        # else risks escaping `sif_dir` (`..`, `/`, `\\`, …).
        raise ValueError(
            f"invalid instance_id {instance_id!r}: must match {_INSTANCE_ID_RE.pattern}"
        )
    filename = templates[source].format(instance_id=instance_id)
    return Path(sif_dir) / filename


def validate_sif_exists(path: Path) -> bool:
    """Check that an SIF file is reachable on disk."""
    return Path(path).is_file()


# --- SWE2 env registry / mix profile -------------------------------------


def load_swe2_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the SWE2 env registry. Same shape as RLVR / SWE1 registries."""
    import yaml

    target = path or ENV_REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "envs" not in data:
        raise ValueError(f"{target}: registry must be a mapping with an 'envs' key")
    rows = data["envs"]
    if not isinstance(rows, list):
        raise ValueError(f"{target}: 'envs' must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{target}: envs[{index}] must be a mapping")
        for required in ("nemo_gym_env", "mix", "status"):
            if required not in row:
                raise ValueError(
                    f"{target}: envs[{index}] missing required field {required!r}"
                )
        if row["status"] not in KNOWN_STATUSES:
            raise ValueError(
                f"{target}: envs[{index}] status {row['status']!r} not in {sorted(KNOWN_STATUSES)}"
            )
        if row["mix"] != MIX_NAME:
            raise ValueError(
                f"{target}: envs[{index}] mix {row['mix']!r} not in {{{MIX_NAME!r}}} "
                f"— SWE2 registry should only carry swe2 rows"
            )
        sif_source = row.get("sif_source")
        if sif_source is not None and sif_source not in KNOWN_SIF_SOURCES:
            raise ValueError(
                f"{target}: envs[{index}] sif_source {sif_source!r} "
                f"not in {sorted(KNOWN_SIF_SOURCES)}"
            )
    return rows


def derive_env_map(registry: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """Pull ``{m0_env_id: nemo_gym_env}`` for the single SWE2 mix."""
    env_map: dict[str, str] = {}
    for row in registry:
        if row["status"] != STATUS_ACTIVE:
            continue
        m0_env = row.get("m0_env_id")
        if not m0_env:
            continue
        if m0_env in env_map and env_map[m0_env] != row["nemo_gym_env"]:
            raise ValueError(
                f"registry has two active mappings for M0 env {m0_env!r}: "
                f"{env_map[m0_env]} vs {row['nemo_gym_env']}"
            )
        env_map[m0_env] = row["nemo_gym_env"]
    return env_map


def coverage_report(registry: Sequence[Mapping[str, Any]]) -> JsonDict:
    """Per-mix counts + gap lists. Mirrors SWE1 / RLVR coverage_report."""
    by_status: dict[str, list[str]] = defaultdict(list)
    by_sif_source: dict[str, list[str]] = defaultdict(list)
    for row in registry:
        by_status[row["status"]].append(row["nemo_gym_env"])
        sif_source = row.get("sif_source")
        if sif_source:
            by_sif_source[sif_source].append(row["status"])
    return {
        "mix": MIX_NAME,
        "total_target_envs": len(registry),
        "counts": {status: len(by_status.get(status, [])) for status in sorted(KNOWN_STATUSES)},
        "active": sorted(by_status.get(STATUS_ACTIVE, [])),
        "m0_missing": sorted(by_status.get(STATUS_M0_MISSING, [])),
        "verifier_mismatch": sorted(by_status.get(STATUS_VERIFIER_MISMATCH, [])),
        "blocked_external": sorted(by_status.get(STATUS_BLOCKED_EXTERNAL, [])),
        # SWE2 extra: count target rows by SIF family so coverage explains
        # *which* container family still needs an M0 source.
        "sif_source_breakdown": {
            source: dict(sorted(defaultdict(int, {s: by_sif_source[source].count(s) for s in by_sif_source[source]}).items()))
            for source in sorted(by_sif_source)
        },
    }


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


# --- JSONL helpers (parallel to RLVR / SWE1) ------------------------------


def read_jsonl(path: Path) -> list[JsonDict]:
    rows: list[JsonDict] = []
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            json.dump(row, f, ensure_ascii=False, sort_keys=True)
            f.write("\n")


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def discover_m0_files(input_dir: Path) -> dict[str, dict[str, Path]]:
    files: dict[str, dict[str, Path]] = defaultdict(dict)
    for path in sorted(input_dir.glob("*/*-split.jsonl")):
        environment = path.parent.name
        split = path.name.replace("-split.jsonl", "")
        files[environment][split] = path
    return dict(files)


def tag_record(
    record: Mapping[str, Any],
    *,
    nemo_gym_env: str,
    sif_source: str | None,
    row_index: int,
    split: str,
) -> JsonDict:
    """Tag an M0 row with SWE2 NeMo-Gym env name + mix metadata + SIF hint."""
    tagged = dict(record)
    tagged["nemo_gym_env"] = nemo_gym_env
    tagged["nemo_gym_mix"] = MIX_NAME
    if sif_source is not None:
        tagged["sif_source"] = sif_source
    metadata = dict(tagged.get("metadata") or {})
    metadata.setdefault("m0_environment", record.get("environment"))
    metadata["nemo_gym_env"] = nemo_gym_env
    metadata["nemo_gym_mix"] = MIX_NAME
    if sif_source is not None:
        metadata["sif_source"] = sif_source
    metadata["swe2_row_index"] = row_index
    metadata["swe2_split"] = split
    tagged["metadata"] = metadata
    return tagged


def _m0_env_to_sif_source(registry: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    """Build a `{m0_env_id: sif_source}` lookup from active registry rows."""
    out: dict[str, str | None] = {}
    for row in registry:
        if row["status"] != STATUS_ACTIVE:
            continue
        m0_env = row.get("m0_env_id")
        if not m0_env:
            continue
        out[m0_env] = row.get("sif_source")
    return out


def collect_rows(
    files_by_env: Mapping[str, Mapping[str, Path]],
    *,
    env_map: Mapping[str, str],
    sif_source_lookup: Mapping[str, str | None],
    split: str,
    max_records_per_env: int | None,
) -> tuple[list[JsonDict], list[JsonDict], dict[str, int]]:
    rows: list[JsonDict] = []
    errors: list[JsonDict] = []
    counts: dict[str, int] = defaultdict(int)
    for m0_env, nemo_gym_env in sorted(env_map.items()):
        split_files = files_by_env.get(m0_env)
        if split_files is None:
            errors.append(
                {
                    "environment": m0_env,
                    "split": split,
                    "error": "M0 has no rows for this environment (not in M0 mix)",
                }
            )
            continue
        path = split_files.get(split)
        if path is None:
            errors.append(
                {
                    "environment": m0_env,
                    "split": split,
                    "error": f"missing {split}-split.jsonl",
                }
            )
            continue
        env_rows = read_jsonl(path)
        if max_records_per_env is not None:
            env_rows = env_rows[:max_records_per_env]
        sif_source = sif_source_lookup.get(m0_env)
        for row_index, record in enumerate(env_rows):
            try:
                tagged = tag_record(
                    record,
                    nemo_gym_env=nemo_gym_env,
                    sif_source=sif_source,
                    row_index=row_index,
                    split=split,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(
                    {
                        "environment": m0_env,
                        "split": split,
                        "row_index": row_index,
                        "error": str(exc),
                    }
                )
                continue
            rows.append(tagged)
            counts[m0_env] += 1
    return rows, errors, dict(sorted(counts.items()))


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
            f"- m0_missing: {len(coverage['m0_missing'])} — {', '.join(f'`{e}`' for e in coverage['m0_missing']) or '(none)'}",
            f"- verifier_mismatch: {len(coverage['verifier_mismatch'])} — {', '.join(f'`{e}`' for e in coverage['verifier_mismatch']) or '(none)'}",
            f"- blocked_external: {len(coverage['blocked_external'])} — {', '.join(f'`{e}`' for e in coverage['blocked_external']) or '(none)'}",
        ]
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

    files_by_env = discover_m0_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    sif_source_lookup = _m0_env_to_sif_source(_REGISTRY)

    train_rows, train_errors, train_counts = collect_rows(
        files_by_env,
        env_map=env_map,
        sif_source_lookup=sif_source_lookup,
        split="train",
        max_records_per_env=args.max_records_per_env,
    )
    val_rows, val_errors, val_counts = collect_rows(
        files_by_env,
        env_map=env_map,
        sif_source_lookup=sif_source_lookup,
        split="val",
        max_records_per_env=args.max_val_records_per_env,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.jsonl"
    val_path = args.output_dir / "val.jsonl"
    write_jsonl(train_path, train_rows)
    write_jsonl(val_path, val_rows)

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
