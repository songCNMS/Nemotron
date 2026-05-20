#!/usr/bin/env python3
# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""CLI for the RLHF tool-call pairing harness (task068 Session 3).

Wires the stream converter from task068 Session 2
(`m0_data_env.rlhf_toolcall_pairing.transform_rlhf_toolcall_pairing`)
into a runnable script.

The pairing is a STREAM operation that consumes TWO M0 sources
(HelpSteer-2 prompts + Hermes function-calling rows) plus an
optional eval-prompt JSONL for decontamination. This script doesn't
fit the per-row converter pattern in `prepare_m0_assets.py`, so it
lives as its own CLI.

Output: a `paired.jsonl` of NeMo-Gym
`single_step_tool_use_with_argument_comparison` rows (argument_match
verifier), plus a `manifest.json` carrying lineage and counts.

Usage::

    python scripts/prepare_rlhf_toolcall_pairing.py \\
        --helpsteer2-jsonl <path>/m0_helpsteer2_pref/train-split.jsonl \\
        --hermes-jsonl <path>/m0_tool_calling_hermes/train-split.jsonl \\
        --eval-prompts-jsonl <path>/m1_eval/prompts_union.jsonl \\
        --output-dir <out>

Dry-run friendly: passes through sandbox without external deps.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from nemotron.recipes.super3.milestones.lineage import (
    LineageInput,
    LineageOutput,
    make_record as make_lineage_record,
)
from nemotron.recipes.super3.milestones.m0_data_env.rlhf_toolcall_pairing import (
    build_eval_prompt_set,
    transform_rlhf_toolcall_pairing,
)


def _iter_jsonl(path: Path) -> Iterator[dict]:
    """Stream-load a JSONL file line by line."""
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_no}: malformed JSONL row: {exc}"
                ) from exc


def _load_jsonl(path: Path) -> list[dict]:
    return list(_iter_jsonl(path))


def _eval_prompts(path: Path | None) -> frozenset[str]:
    """Build the eval-prompt 5-gram set from a JSONL of {prompt: str}.

    Empty set when *path* is None — converter falls through to no
    contamination filtering (useful for sandbox / smoke runs).
    """
    if path is None:
        return frozenset()
    prompts: list[str] = []
    for row in _iter_jsonl(path):
        for key in ("prompt", "question", "inputs"):
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                prompts.append(value)
                break
    return build_eval_prompt_set(prompts)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pair HelpSteer-2 prompts with Hermes tool calls for RLHF tool-call validity."
    )
    parser.add_argument(
        "--helpsteer2-jsonl",
        type=Path,
        required=True,
        help="Path to M0 HelpSteer-2 split JSONL (each row has at least `prompt`).",
    )
    parser.add_argument(
        "--hermes-jsonl",
        type=Path,
        required=True,
        help="Path to M0 Hermes function-calling split JSONL.",
    )
    parser.add_argument(
        "--eval-prompts-jsonl",
        type=Path,
        default=None,
        help="Optional path to eval-prompt JSONL used for decontamination. "
        "Empty set if omitted (no contamination filter).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for paired.jsonl + manifest.json.",
    )
    return parser


def prepare(args: argparse.Namespace) -> dict:
    """Run the pairing pipeline; return manifest dict.

    Caller responsibility: pass arguments via argparse; receive manifest
    (already written to disk too). Tests call this directly with a
    constructed `argparse.Namespace`.
    """
    helpsteer_rows = _load_jsonl(args.helpsteer2_jsonl)
    hermes_rows = _load_jsonl(args.hermes_jsonl)
    eval_set = _eval_prompts(args.eval_prompts_jsonl)

    paired = list(
        transform_rlhf_toolcall_pairing(
            helpsteer_rows,
            hermes_corpus=hermes_rows,
            eval_prompt_set=eval_set,
        )
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_jsonl = args.output_dir / "paired.jsonl"
    _write_jsonl(output_jsonl, paired)

    lineage_inputs = [
        LineageInput(
            kind="manifest",
            ref=str(args.helpsteer2_jsonl.parent / "manifest.json"),
            notes="M0 HelpSteer-2 source (task018 Session 2)",
        ),
        LineageInput(
            kind="manifest",
            ref=str(args.hermes_jsonl.parent / "manifest.json"),
            notes="M0 Hermes function-calling source (task005)",
        ),
    ]
    if args.eval_prompts_jsonl is not None:
        lineage_inputs.append(
            LineageInput(
                kind="eval_prompts",
                ref=str(args.eval_prompts_jsonl),
                notes="Decontamination 5-gram set (BFCL / TauBench airline / MCP-Mark / HelpSteer1)",
            )
        )
    lineage_outputs = [
        LineageOutput(
            kind="rlhf_toolcall_paired_jsonl",
            ref="paired.jsonl",
            rows=len(paired),
            notes="Argument-match rows ready for RLHF tool-call validity env",
        ),
    ]
    lineage_record = make_lineage_record(
        stage="M0 data_env_foundation",
        produced_by="prepare_rlhf_toolcall_pairing.py",
        artifact_type="RawDataArtifact",
        artifact_name=args.output_dir.name or "rlhf_toolcall_paired",
        inputs=lineage_inputs,
        outputs=lineage_outputs,
    )

    manifest = {
        "schema_version": 1,
        "milestone": "M0",
        "stage": "M0 data_env_foundation",
        "produced_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "produced_by": "prepare_rlhf_toolcall_pairing.py",
        "helpsteer2_input": str(args.helpsteer2_jsonl),
        "hermes_input": str(args.hermes_jsonl),
        "eval_prompts_input": (
            str(args.eval_prompts_jsonl)
            if args.eval_prompts_jsonl is not None
            else None
        ),
        "output_dir": str(args.output_dir),
        "counts": {
            "helpsteer2_rows": len(helpsteer_rows),
            "hermes_rows": len(hermes_rows),
            "eval_prompt_5grams": len(eval_set),
            "paired_rows": len(paired),
        },
        "lineage": lineage_record.to_jsonable(),
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare(args)
    except FileNotFoundError as exc:
        print(f"prepare_rlhf_toolcall_pairing: error: {exc}", file=sys.stderr)
        return 1
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"prepare_rlhf_toolcall_pairing: error: {exc}", file=sys.stderr)
        return 2

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
                "output_dir": manifest["output_dir"],
                "paired_rows": manifest["counts"]["paired_rows"],
                "helpsteer2_rows": manifest["counts"]["helpsteer2_rows"],
                "hermes_rows": manifest["counts"]["hermes_rows"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
