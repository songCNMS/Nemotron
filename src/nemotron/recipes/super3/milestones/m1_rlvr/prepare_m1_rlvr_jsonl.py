#!/usr/bin/env python3
# /// script
# dependencies = []
# ///

"""Prepare M1 RLVR JSONL by bridging M0 NeMo-Gym JSONL into the RLVR mix.

This is the M0 → RLVR1 data bridge from `docs/implementation-roadmap.md`
§1.3 / task014. The M0 prepare script already emits records in the NeMo-Gym
contract shape (``environment``, ``responses_create_params.{input,tools}``,
``reward_config``, ``extra_env_info``), so the bridge here is *mostly mapping
and slicing*, not converting:

- read M0 split files (one ``<env>/<split>-split.jsonl`` per environment),
- keep only the four environments the RLVR1 mix calls for (math, code,
  search, tool-calling) — see ``RLVR1_ENV_MAP``,
- tag every kept row with the NeMo-Gym env name the server side recognises
  via a fresh ``nemo_gym_env`` field, leaving M0 ``environment`` intact so
  health-baseline / lineage stay self-consistent,
- write a single combined ``train.jsonl`` / ``val.jsonl`` plus a
  ``manifest.json`` that downstream ``SplitJsonlDataArtifact`` consumers
  (``stage2_rl/_data_prep_base.py``) can point at,
- emit a ``lineage`` block declaring this as an ``RLVR1`` artifact with the
  M0 manifest as the upstream ``manifest`` input.

Session 1 ships the RLVR1 mix only. RLVR2 / RLVR3 mixes (extra 17 envs)
are task015 territory; ``MIX_PROFILES`` makes the slot explicit so future
sessions plug in without reshaping the script.
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
        RLVR1_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    # Fallback for direct-script execution (PEP 723 banner enables that).
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lineage import (  # type: ignore[no-redef]
        RLVR1_ARTIFACT,
        LineageInput,
        LineageOutput,
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

JsonDict = dict[str, Any]

MILESTONE = "M1"
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_rlvr")
USED_IN_TAG = "super3_rlvr1_v0"

# M0 environment id → NeMo-Gym env name that the RLVR1 server side recognises.
# Source: roadmap §1.3 task014 ("math_with_judge (gsm8k), code_gen (mbpp),
# search_grounded_qa (hotpot), general_tool_calling (hermes)").
RLVR1_ENV_MAP: dict[str, str] = {
    "math_reasoning_numeric": "math_with_judge",
    "code_execution_python": "code_gen",
    "search_grounded_qa": "search_grounded_qa",
    "general_tool_calling": "general_tool_calling",
}

# Future RLVR2 / RLVR3 mixes (task015). The dict is intentionally empty —
# wiring extra envs requires per-env reward verifier registration on the
# NeMo-Gym side (license audit + hf_revision pin). Until that lands, those
# mixes are unbuildable; this slot just declares the shape.
RLVR2_ENV_MAP: dict[str, str] = {}
RLVR3_ENV_MAP: dict[str, str] = {}

MIX_PROFILES: dict[str, dict[str, Any]] = {
    "rlvr1": {
        "artifact_type": RLVR1_ARTIFACT,
        "stage": "M1 RLVR1",
        "env_map": RLVR1_ENV_MAP,
        "used_in_tag": "super3_rlvr1_v0",
    },
    # rlvr2 / rlvr3 are reserved slots filled by task015.
}


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
    """Return ``{environment: {split: path}}`` for every ``<env>/<split>-split.jsonl``.

    Mirrors ``prepare_m1_agentic_sft.discover_m0_files`` so the M1 RLVR bridge
    consumes the exact same M0 layout.
    """
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
    mix_name: str,
    row_index: int,
    split: str,
) -> JsonDict:
    """Return a copy of *record* with NeMo-Gym mix tags applied.

    The M0 record already carries the contract shape the NemoGymDataset
    consumes (``responses_create_params``, ``reward_config``, etc.). We just
    layer mix-level metadata on top without touching ground-truth fields.
    """
    tagged = dict(record)
    tagged["nemo_gym_env"] = nemo_gym_env
    tagged["nemo_gym_mix"] = mix_name
    metadata = dict(tagged.get("metadata") or {})
    metadata.setdefault("m0_environment", record.get("environment"))
    metadata["nemo_gym_env"] = nemo_gym_env
    metadata["nemo_gym_mix"] = mix_name
    metadata["rlvr_row_index"] = row_index
    metadata["rlvr_split"] = split
    tagged["metadata"] = metadata
    return tagged


def collect_mix_rows(
    files_by_env: Mapping[str, Mapping[str, Path]],
    *,
    env_map: Mapping[str, str],
    split: str,
    mix_name: str,
    max_records_per_env: int | None,
) -> tuple[list[JsonDict], list[JsonDict], dict[str, int]]:
    """Slice M0 records into the mix and tag them.

    Returns ``(rows, errors, per_env_counts)``. ``errors`` collects per-env
    issues (missing split file, malformed row) so the manifest can surface
    them without aborting the run.
    """
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
                    mix_name=mix_name,
                    row_index=row_index,
                    split=split,
                )
            except Exception as exc:  # noqa: BLE001 - keep mixing on row failure
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
        raise ValueError(
            f"mix {args.mix!r} has no env_map yet (task015 territory)"
        )

    files_by_env = discover_m0_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    train_rows, train_errors, train_counts = collect_mix_rows(
        files_by_env,
        env_map=env_map,
        split="train",
        mix_name=args.mix,
        max_records_per_env=args.max_records_per_env,
    )
    val_rows, val_errors, val_counts = collect_mix_rows(
        files_by_env,
        env_map=env_map,
        split="val",
        mix_name=args.mix,
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
        "stage": profile["stage"],
        "mix": args.mix,
        "used_in_tag": profile["used_in_tag"],
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
        "errors": [*train_errors, *val_errors],
    }

    # task014 Session 1: cross-stage lineage block. Upstream is the M0
    # manifest (RawDataArtifact); outputs are the combined train / val
    # JSONLs that the NeMo-Gym data loader points its `data_path` at.
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
        help="Which RLVR mix to build (Session 1 ships rlvr1 only).",
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
