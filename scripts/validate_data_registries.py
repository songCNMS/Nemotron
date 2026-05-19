#!/usr/bin/env python3
# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""CLI entry point for the unified data registry validator.

task030 Session 2 — schema enforcement at write time. Wraps
``data_registries.unified_index_loader.validate_unified_index`` and
exits non-zero when any registered YAML drifts from its declared
shape. Designed to be called from pre-commit hooks and CI workflows so
schema drift gets caught the moment it's authored, not when a cluster
run tries to load the registry an hour into a job.

Two layers of validation exist by design:

- **Bridge runtime loaders** (`_bridge_base.load_env_registry`, etc.)
  fail-fast on first issue so a single broken row aborts the prepare
  step instead of silently building bad data.
- **This script + unified schema** collect all issues at once so an
  audit pass surfaces every problem in a single report. Useful for
  PR review and CI gating.

The two layers intentionally don't merge: fail-fast and collect-all
serve different consumers. Documented in
``docs/implementation-roadmap.md`` §3 W1 row.

Usage:
    scripts/validate_data_registries.py
    scripts/validate_data_registries.py --quiet     # pre-commit mode (no stdout on clean)
    scripts/validate_data_registries.py --paths     # print only the offending paths

Exit codes:
    0  — every registry validates clean
    1  — one or more registries drift from their declared shape
    2  — the validator itself failed (missing index, bad import, etc.)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="On clean validation, exit silently (no stdout). Issues still go to stderr.",
    )
    parser.add_argument(
        "--paths",
        action="store_true",
        help="When issues are found, print only the offending registry ids (one per line) for easier downstream filtering.",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=None,
        help="Override the default unified_index.yaml location. Mostly useful for tests.",
    )
    parser.add_argument(
        "--license-cascade",
        action="store_true",
        help=(
            "Print the share-alike license cascade audit (task058 Session 2). "
            "Walks the unified index for CC-BY-SA-* / GPL / etc. data sources "
            "and traces each one through the bridge env_registry to find which "
            "downstream RL mix rows inherit the share-alike obligation. "
            "Informational only (exit 0 even with findings)."
        ),
    )
    parser.add_argument(
        "--check-revision-pins",
        action="store_true",
        help=(
            "Audit HuggingFace `hf_revision` pins on production data rows "
            "(task030 Session 6, task058 follow-up). Two categories: "
            "BLOCKERS = m0_data_registry rows whose hf_revision is missing "
            "or a floating ref (main/master/head/latest) → exit 1; "
            "informational = pref_data_registry candidate rows with "
            "hf_revision_pin_required:true awaiting task018 Session 2 pin "
            "→ exit 0."
        ),
    )
    args = parser.parse_args(argv)

    try:
        from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
            validate_unified_index,
        )
    except ImportError as exc:
        print(
            f"validate_data_registries: cannot import validate_unified_index: {exc}",
            file=sys.stderr,
        )
        return 2

    # Audit-only modes short-circuit the validate path. Return code is
    # 0 even if findings exist — these are informational, not blocking.
    if args.license_cascade:
        try:
            from nemotron.recipes.super3.milestones.data_registries.license_audit import (
                format_cascade_report,
                license_cascade,
            )
            cascade = license_cascade(args.index_path)
        except Exception as exc:  # noqa: BLE001
            print(
                f"validate_data_registries: license-cascade audit raised: {exc}",
                file=sys.stderr,
            )
            return 2
        # Always emit to stdout — audit reports are content, not noise.
        sys.stdout.write(format_cascade_report(cascade))
        return 0

    if args.check_revision_pins:
        try:
            from nemotron.recipes.super3.milestones.data_registries.revision_audit import (
                find_unpinned_revisions,
                format_revision_audit_report,
            )
            audit = find_unpinned_revisions(args.index_path)
        except Exception as exc:  # noqa: BLE001
            print(
                f"validate_data_registries: revision-pin audit raised: {exc}",
                file=sys.stderr,
            )
            return 2
        sys.stdout.write(format_revision_audit_report(audit))
        if audit.get("blockers"):
            print(
                f"validate_data_registries: {len(audit['blockers'])} unpinned "
                "production data row(s) — fix or pin a hf_revision SHA",
                file=sys.stderr,
            )
            return 1
        return 0

    try:
        issues = validate_unified_index(args.index_path)
    except Exception as exc:  # noqa: BLE001
        print(
            f"validate_data_registries: validator raised: {exc}",
            file=sys.stderr,
        )
        return 2

    if not issues:
        if not args.quiet:
            print("validate_data_registries: all registries clean ✓")
        return 0

    if args.paths:
        # One registry-id per line for easy filtering. Registry ids
        # are the prefix before the first ": " in each issue string
        # (matches the format unified_index_loader emits).
        seen: set[str] = set()
        for issue in issues:
            registry_id, _, _ = issue.partition(": ")
            if registry_id and registry_id not in seen:
                seen.add(registry_id)
                print(registry_id)
        return 1

    print(
        f"validate_data_registries: {len(issues)} issue(s) across the unified index:",
        file=sys.stderr,
    )
    for issue in issues:
        print(f"  - {issue}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
