#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 SWE1 JSONL by bridging M0 SWE pivot data into the
``swe_pivot_single_step_tool_use_with_argument_comparison`` env.

Structure mirrors ``m1_rlvr/prepare_m1_rlvr_jsonl.py``: the M0 prepare
script emits records in the NeMo-Gym contract shape, this bridge just
filters + tags + emits manifest/lineage. SWE1 differs from RLVR in two
ways:

- single NeMo-Gym env (``swe_pivot_single_step_tool_use_with_argument_comparison``)
  loaded by ``stage2_rl/stage2_swe1/config/default.yaml``;
- the only currently registered M0 source (``swe_pivot_patch_supervision``)
  uses a different verifier shape (``patch_diff_match`` vs the NeMo-Gym
  side's ``argument_match``), so the registry marks it
  ``verifier_mismatch``. Session 2 lands a proper M0 SWE pivot env and
  flips a registry row to ``active``; the bridge auto-picks it up with
  no Python edits required.

The implementation duplicates ~80% of the RLVR bridge. A
``_bridge_base.py`` extraction makes sense once task017 SWE2 lands a
third copy — flagged in roadmap §1.4 / §1.5 follow-up.
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
    from nemotron.recipes.super3.milestones.lineage import (
        SWE1_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lineage import (  # type: ignore[no-redef]
        SWE1_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

JsonDict = dict[str, Any]

MILESTONE = "M1"
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_swe1")
USED_IN_TAG = "super3_swe1_v0"
MIX_NAME = "swe1"

REGISTRY_PATH = Path(__file__).with_name("swe1_env_registry.yaml")

STATUS_ACTIVE = "active"
STATUS_M0_MISSING = "m0_missing"
STATUS_VERIFIER_MISMATCH = "verifier_mismatch"
STATUS_BLOCKED_EXTERNAL = "blocked_external"
KNOWN_STATUSES = frozenset(
    {STATUS_ACTIVE, STATUS_M0_MISSING, STATUS_VERIFIER_MISMATCH, STATUS_BLOCKED_EXTERNAL}
)


def load_swe1_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the SWE1 registry. Same shape as the RLVR registry loader."""
    import yaml

    target = path or REGISTRY_PATH
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
                f"— SWE1 registry should only carry swe1 rows"
            )
    return rows


def derive_env_map(registry: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """Pull ``{m0_env_id: nemo_gym_env}`` for the single SWE1 mix."""
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
    """Per-mix counts + gap lists. Mirrors RLVR coverage_report."""
    by_status: dict[str, list[str]] = defaultdict(list)
    for row in registry:
        by_status[row["status"]].append(row["nemo_gym_env"])
    return {
        "mix": MIX_NAME,
        "total_target_envs": len(registry),
        "counts": {status: len(by_status.get(status, [])) for status in sorted(KNOWN_STATUSES)},
        "active": sorted(by_status.get(STATUS_ACTIVE, [])),
        "m0_missing": sorted(by_status.get(STATUS_M0_MISSING, [])),
        "verifier_mismatch": sorted(by_status.get(STATUS_VERIFIER_MISMATCH, [])),
        "blocked_external": sorted(by_status.get(STATUS_BLOCKED_EXTERNAL, [])),
    }


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
    row_index: int,
    split: str,
) -> JsonDict:
    """Tag an M0 row with the SWE1 NeMo-Gym env name + mix metadata."""
    tagged = dict(record)
    tagged["nemo_gym_env"] = nemo_gym_env
    tagged["nemo_gym_mix"] = MIX_NAME
    metadata = dict(tagged.get("metadata") or {})
    metadata.setdefault("m0_environment", record.get("environment"))
    metadata["nemo_gym_env"] = nemo_gym_env
    metadata["nemo_gym_mix"] = MIX_NAME
    metadata["swe1_row_index"] = row_index
    metadata["swe1_split"] = split
    tagged["metadata"] = metadata
    return tagged


def collect_rows(
    files_by_env: Mapping[str, Mapping[str, Path]],
    *,
    env_map: Mapping[str, str],
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
        for row_index, record in enumerate(env_rows):
            try:
                tagged = tag_record(
                    record,
                    nemo_gym_env=nemo_gym_env,
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

    files_by_env = discover_m0_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    train_rows, train_errors, train_counts = collect_rows(
        files_by_env,
        env_map=env_map,
        split="train",
        max_records_per_env=args.max_records_per_env,
    )
    val_rows, val_errors, val_counts = collect_rows(
        files_by_env,
        env_map=env_map,
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
        "stage": SWE1_PROFILE["stage"],
        "mix": MIX_NAME,
        "used_in_tag": SWE1_PROFILE["used_in_tag"],
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
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
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
