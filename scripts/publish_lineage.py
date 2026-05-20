#!/usr/bin/env python3
# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Publish a lineage block from a manifest.json to W&B (task069 Session 1 CLI).

Reads `manifest.json` produced by a prep / training stage
(`prepare_m0_assets.py`, `prepare_m1_*_jsonl.py`,
`stage1_sft/train.py`, etc.), extracts the embedded
``lineage`` block, and pushes it to W&B as
``wandb.Artifact`` calls via ``WandbArtifactPublisher``.

Dry-run mode (default in sandbox / CI without W&B credentials) reports
what WOULD have been published without actually calling W&B.

Usage::

    # Real publish (requires WANDB_API_KEY + an active wandb.init run)
    python scripts/publish_lineage.py \\
        output/super3/m0/manifest.json \\
        --wandb-project nemotron-super3 \\
        --wandb-run-id <run-id>

    # Dry-run (sandbox / planning)
    python scripts/publish_lineage.py \\
        output/super3/m0/manifest.json --dry-run

Exit codes:
- 0: publish succeeded (or dry-run completed cleanly)
- 1: manifest.json missing or malformed
- 2: lineage block missing or malformed
- 3: real publish requested but wandb import / credentials unavailable
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nemotron.recipes.super3.milestones.lineage import LineageRecord
from nemotron.recipes.super3.milestones.lineage_publisher import (
    WandbArtifactPublisher,
)


def load_lineage_record(manifest_path: Path) -> LineageRecord:
    """Read a manifest.json, return its embedded LineageRecord.

    Raises FileNotFoundError if the manifest is missing, ValueError if
    it's malformed or has no lineage block.
    """
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    with manifest_path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{manifest_path}: top-level JSON must be a mapping")
    lineage_block = data.get("lineage")
    if not isinstance(lineage_block, dict):
        raise ValueError(
            f"{manifest_path}: missing or non-mapping 'lineage' block; "
            "this manifest may pre-date task021 Session 2"
        )
    return LineageRecord.from_jsonable(lineage_block)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish a lineage block from manifest.json to W&B."
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to manifest.json produced by a prep / training stage.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be published without calling W&B "
        "(default in environments without W&B credentials).",
    )
    parser.add_argument(
        "--file-root",
        type=Path,
        default=None,
        help="Directory under which lineage outputs[i].ref is resolved. "
        "Defaults to the manifest's parent directory.",
    )
    args = parser.parse_args(argv)

    try:
        record = load_lineage_record(args.manifest)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: lineage block invalid: {exc}", file=sys.stderr)
        return 2

    file_root = args.file_root or args.manifest.parent

    if args.dry_run:
        publisher = WandbArtifactPublisher(wandb_run=None)
    else:
        # Real publish path — lazy import wandb so dry-run can run in
        # environments without it.
        try:
            import wandb  # noqa: F401
        except ImportError:
            print(
                "error: wandb not installed; install it or pass --dry-run",
                file=sys.stderr,
            )
            return 3
        active_run = wandb.run
        if active_run is None:
            print(
                "error: no active wandb run; call wandb.init() before "
                "invoking this script, or pass --dry-run",
                file=sys.stderr,
            )
            return 3
        publisher = WandbArtifactPublisher(wandb_run=active_run)

    result = publisher.publish(record, file_root=file_root)

    print("publish:", "(dry-run)" if result.dry_run else "(live)")
    print(f"  artifact_name: {result.artifact_name}")
    print(f"  artifact_type: {result.artifact_type}")
    print(f"  upstream resolved ({len(result.upstream_resolved)}):")
    for name in result.upstream_resolved:
        print(f"    - {name}")
    if result.upstream_unresolved:
        print(f"  upstream unresolved ({len(result.upstream_unresolved)}):")
        for ref in result.upstream_unresolved:
            print(f"    - {ref}")
    print(f"  outputs attached ({len(result.outputs_attached)}):")
    for path in result.outputs_attached:
        print(f"    - {path}")
    if result.outputs_missing:
        print(f"  outputs missing on disk ({len(result.outputs_missing)}):")
        for path in result.outputs_missing:
            print(f"    - {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
