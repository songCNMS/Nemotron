#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 RLHF JSONL — fourth registry-driven bridge copy.

`stage2_rl/stage3_rlhf/config/default.yaml::nemo_gym.config_paths` loads
two env configs:

- ``genrm_compare`` (GenRM preference judge)
- ``single_step_tool_use_with_argument_comparison`` (parallel tool-call
  validity check per plan §5.6)

Both are ``blocked_external`` / ``m0_missing`` today. Session 2 lands an
M0 preference-data converter (HelpSteer-2 / UltraFeedback / orca DPO
pairs per ``rlhf_pref_data_registry.yaml``) plus a cluster-side GenRM
model deployment; the bridge flips registry rows to ``active`` with no
Python edits required.

Module structure mirrors ``m1_swe2/prepare_m1_swe2_jsonl.py``: load env
registry → derive env_map → coverage_report → tag_record → prepare.
The RLHF-specific extension is ``pref_dataset_breakdown`` in the
coverage block — operators see at a glance which preference source is
backing which env row.

Code duplication note: this is the fourth registry-driven bridge after
RLVR + SWE1 + SWE2. `_bridge_base.py` extraction (task017 Session 4)
will generalise the common scaffolding once the per-stage variations
stop moving.
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
        RLHF_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lineage import (  # type: ignore[no-redef]
        RLHF_ARTIFACT,
        LineageInput,
        LineageOutput,
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

STATUS_ACTIVE = "active"
STATUS_M0_MISSING = "m0_missing"
STATUS_VERIFIER_MISMATCH = "verifier_mismatch"
STATUS_BLOCKED_EXTERNAL = "blocked_external"
KNOWN_STATUSES = frozenset(
    {STATUS_ACTIVE, STATUS_M0_MISSING, STATUS_VERIFIER_MISMATCH, STATUS_BLOCKED_EXTERNAL}
)


# --- Preference-data candidate registry -----------------------------------


def load_rlhf_pref_data_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the preference-data candidate registry.

    Each row points at a HF dataset that could back the RLHF training
    (HelpSteer-2 / UltraFeedback / Orca DPO pairs / …). The bridge does
    not consume the registry directly — it surfaces a `known_candidates`
    list in the coverage block so coverage explains which source still
    needs an M0 transformer.
    """
    import yaml

    target = path or PREF_DATA_REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "datasets" not in data:
        raise ValueError(f"{target}: pref-data registry must declare a 'datasets' list")
    rows = data["datasets"]
    if not isinstance(rows, list):
        raise ValueError(f"{target}: 'datasets' must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{target}: datasets[{index}] must be a mapping")
        for required in ("id", "hf_dataset", "license"):
            if required not in row:
                raise ValueError(
                    f"{target}: datasets[{index}] missing required field {required!r}"
                )
    return rows


def pref_candidate_ids(registry: Sequence[Mapping[str, Any]]) -> list[str]:
    return sorted(str(row["id"]) for row in registry)


# --- RLHF env registry / mix profile --------------------------------------


def load_rlhf_env_registry(path: Path | None = None) -> list[JsonDict]:
    """Load the RLHF env registry. Same shape as RLVR / SWE1 / SWE2 loaders."""
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
                f"— RLHF registry should only carry rlhf rows"
            )
    return rows


def derive_env_map(registry: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """Pull ``{m0_env_id: nemo_gym_env}`` for the single RLHF mix."""
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


def coverage_report(
    registry: Sequence[Mapping[str, Any]],
    pref_data_registry: Sequence[Mapping[str, Any]] | None = None,
) -> JsonDict:
    """Per-mix counts + gap lists. RLHF-specific extension:
    ``pref_dataset_breakdown`` maps each ``pref_dataset_candidate`` named
    in the env registry to its current status, plus a ``known_candidates``
    list of all pref sources the candidate registry knows about. Together
    they answer "which env rows have a pref source already? which pref
    sources have no env row yet?".
    """
    by_status: dict[str, list[str]] = defaultdict(list)
    by_pref_dataset: dict[str, list[str]] = defaultdict(list)
    for row in registry:
        by_status[row["status"]].append(row["nemo_gym_env"])
        pref = row.get("pref_dataset_candidate")
        if pref:
            by_pref_dataset[pref].append(row["status"])
    pref_dataset_breakdown = {
        pref: dict(sorted({s: by_pref_dataset[pref].count(s) for s in by_pref_dataset[pref]}.items()))
        for pref in sorted(by_pref_dataset)
    }
    known_candidates: list[str] = []
    if pref_data_registry is not None:
        known_candidates = pref_candidate_ids(pref_data_registry)
    return {
        "mix": MIX_NAME,
        "total_target_envs": len(registry),
        "counts": {status: len(by_status.get(status, [])) for status in sorted(KNOWN_STATUSES)},
        "active": sorted(by_status.get(STATUS_ACTIVE, [])),
        "m0_missing": sorted(by_status.get(STATUS_M0_MISSING, [])),
        "verifier_mismatch": sorted(by_status.get(STATUS_VERIFIER_MISMATCH, [])),
        "blocked_external": sorted(by_status.get(STATUS_BLOCKED_EXTERNAL, [])),
        "pref_dataset_breakdown": pref_dataset_breakdown,
        "known_pref_candidates": known_candidates,
    }


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


# --- JSONL helpers (parallel to RLVR / SWE1 / SWE2) -----------------------


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
    pref_dataset: str | None,
    row_index: int,
    split: str,
) -> JsonDict:
    """Tag an M0 row with RLHF NeMo-Gym env name + mix metadata + pref hint."""
    tagged = dict(record)
    tagged["nemo_gym_env"] = nemo_gym_env
    tagged["nemo_gym_mix"] = MIX_NAME
    if pref_dataset is not None:
        tagged["pref_dataset"] = pref_dataset
    metadata = dict(tagged.get("metadata") or {})
    metadata.setdefault("m0_environment", record.get("environment"))
    metadata["nemo_gym_env"] = nemo_gym_env
    metadata["nemo_gym_mix"] = MIX_NAME
    if pref_dataset is not None:
        metadata["pref_dataset"] = pref_dataset
    metadata["rlhf_row_index"] = row_index
    metadata["rlhf_split"] = split
    tagged["metadata"] = metadata
    return tagged


def _m0_env_to_pref_dataset(registry: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for row in registry:
        if row["status"] != STATUS_ACTIVE:
            continue
        m0_env = row.get("m0_env_id")
        if not m0_env:
            continue
        out[m0_env] = row.get("pref_dataset_candidate")
    return out


def collect_rows(
    files_by_env: Mapping[str, Mapping[str, Path]],
    *,
    env_map: Mapping[str, str],
    pref_lookup: Mapping[str, str | None],
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
        pref_dataset = pref_lookup.get(m0_env)
        for row_index, record in enumerate(env_rows):
            try:
                tagged = tag_record(
                    record,
                    nemo_gym_env=nemo_gym_env,
                    pref_dataset=pref_dataset,
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
            f"- m0_missing: {len(coverage['m0_missing'])} — {', '.join(f'`{e}`' for e in coverage['m0_missing']) or '(none)'}",
            f"- verifier_mismatch: {len(coverage['verifier_mismatch'])} — {', '.join(f'`{e}`' for e in coverage['verifier_mismatch']) or '(none)'}",
            f"- blocked_external: {len(coverage['blocked_external'])} — {', '.join(f'`{e}`' for e in coverage['blocked_external']) or '(none)'}",
            f"- known pref candidates: {', '.join(f'`{c}`' for c in coverage['known_pref_candidates']) or '(none)'}",
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

    files_by_env = discover_m0_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    pref_lookup = _m0_env_to_pref_dataset(_REGISTRY)

    train_rows, train_errors, train_counts = collect_rows(
        files_by_env,
        env_map=env_map,
        pref_lookup=pref_lookup,
        split="train",
        max_records_per_env=args.max_records_per_env,
    )
    val_rows, val_errors, val_counts = collect_rows(
        files_by_env,
        env_map=env_map,
        pref_lookup=pref_lookup,
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
        "stage": RLHF_PROFILE["stage"],
        "mix": MIX_NAME,
        "used_in_tag": RLHF_PROFILE["used_in_tag"],
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
        "coverage": coverage_report(_REGISTRY, _PREF_DATA_REGISTRY),
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
