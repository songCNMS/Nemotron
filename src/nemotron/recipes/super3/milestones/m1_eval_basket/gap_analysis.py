# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""M1 per-category gap analysis (roadmap §1.7 task020 Session 4).

Complements ``promotion_gate.py``:

- ``promotion_gate.evaluate_promotion_gate`` answers
  *"is this checkpoint good enough to promote?"* (binary decision).
- ``gap_analysis.analyze_gaps`` answers *"where should the next
  training run focus?"* (prescriptive ranking of where the
  checkpoint is behind Super3 and which individual benchmarks are
  dragging each category down).

The two consume the same dict-of-scores inputs and the same registry
rows, so the operator can run all three reports off one eval JSON.

Sandbox-runnable; pure stdlib. Real cluster data flows in once
task020 Session 3 wires the `nemotron super3 eval -c m1_full_basket`
CLI to produce the JSONs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


# Default threshold for "this category is meaningfully behind Super3".
# Matches the plan §5.7 / promotion_gate "1-2 %" language. A category
# whose gap is more negative than -threshold shows up in the
# "categories_below_threshold" tally on the markdown report.
DEFAULT_GAP_THRESHOLD = 0.02


@dataclass(frozen=True)
class BenchmarkGap:
    """One benchmark's contribution to its category's gap.

    ``gap = current - super3``; negative means current is below Super3.
    Either value may be None if the eval run / Super3 baseline didn't
    report that benchmark — gap is then None and the benchmark is
    surfaced but doesn't enter the category mean.
    """

    benchmark_id: str
    current: float | None
    super3: float | None
    gap: float | None


@dataclass(frozen=True)
class CategoryGap:
    """Aggregate gap for one category, with per-benchmark drill-down.

    ``benchmark_gaps`` is sorted by gap ascending (most negative first)
    so the markdown report can list the worst contributors at the top
    of each category section.
    """

    category: str
    current_mean: float | None
    super3_mean: float | None
    gap: float | None  # current_mean - super3_mean, or None when uncomputable
    benchmark_gaps: tuple[BenchmarkGap, ...]


def _group_by_category(
    registry_rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in registry_rows:
        bid = row.get("benchmark_id")
        cat = row.get("category")
        if not bid or not cat:
            continue
        out.setdefault(cat, []).append(bid)
    return out


def _mean(values: Iterable[float]) -> float | None:
    bucket = list(values)
    if not bucket:
        return None
    return sum(bucket) / len(bucket)


def analyze_gaps(
    current_results: Mapping[str, float],
    super3_baseline: Mapping[str, float],
    registry_rows: Iterable[Mapping[str, Any]],
) -> list[CategoryGap]:
    """Return per-category gap analysis, sorted worst-first.

    "Worst" = most negative ``gap``; categories with no computable gap
    (either side empty) sort to the bottom so the most actionable
    findings stay at the top. Within a category, ``benchmark_gaps`` is
    sorted by per-benchmark gap ascending so the operator immediately
    sees which benchmarks contribute most to the deficit.
    """
    rows = list(registry_rows)
    category_to_benchmarks = _group_by_category(rows)

    results: list[CategoryGap] = []
    for category, benchmark_ids in category_to_benchmarks.items():
        benchmark_gaps: list[BenchmarkGap] = []
        for bid in benchmark_ids:
            cur = current_results.get(bid)
            ref = super3_baseline.get(bid)
            gap = (cur - ref) if (cur is not None and ref is not None) else None
            benchmark_gaps.append(
                BenchmarkGap(
                    benchmark_id=bid,
                    current=cur,
                    super3=ref,
                    gap=gap,
                )
            )

        cur_mean = _mean(bg.current for bg in benchmark_gaps if bg.current is not None)
        ref_mean = _mean(bg.super3 for bg in benchmark_gaps if bg.super3 is not None)
        if cur_mean is None or ref_mean is None:
            cat_gap: float | None = None
        else:
            cat_gap = cur_mean - ref_mean

        # Sort benchmarks within the category by gap ascending; benchmarks
        # with no gap (one side missing) sort to the end since they have
        # no actionable signal.
        sorted_benchmarks = tuple(
            sorted(
                benchmark_gaps,
                key=lambda bg: (bg.gap is None, bg.gap if bg.gap is not None else 0.0),
            )
        )

        results.append(
            CategoryGap(
                category=category,
                current_mean=cur_mean,
                super3_mean=ref_mean,
                gap=cat_gap,
                benchmark_gaps=sorted_benchmarks,
            )
        )

    # Sort categories: those with a computable gap, sorted ascending
    # (worst gap first); then those without (None) at the end, by name
    # for stability.
    results.sort(
        key=lambda cg: (cg.gap is None, cg.gap if cg.gap is not None else 0.0, cg.category)
    )
    return results


def count_categories_below_threshold(
    gaps: Iterable[CategoryGap], *, threshold: float = DEFAULT_GAP_THRESHOLD
) -> int:
    """Return how many categories have ``gap < -threshold``.

    Convenience for the markdown summary line. Categories with no
    computable gap don't count toward this tally (you can't say they're
    "behind" without data).
    """
    return sum(1 for cg in gaps if cg.gap is not None and cg.gap < -threshold)


def format_gap_analysis(
    gaps: list[CategoryGap], *, threshold: float = DEFAULT_GAP_THRESHOLD
) -> str:
    """Render the gap analysis as markdown.

    Two sections:

    1. Ranked category table — every category with its gap vs Super3,
       sorted worst-first. Marker column flags categories below the
       threshold.
    2. Drill-down — for categories below threshold, per-benchmark
       contributions so the operator sees which individual benchmarks
       are dragging the mean down.
    """
    if not gaps:
        return (
            "# Gap analysis vs Super3\n\n"
            "(no categories — registry empty or eval ran zero benchmarks)\n"
        )

    below = count_categories_below_threshold(gaps, threshold=threshold)
    lines = [
        "# Gap analysis vs Super3",
        "",
        f"**Summary**: {below} category/categories more than "
        f"{threshold:.2%} behind Super3 (of {len(gaps)} total)",
        "",
        "| Category | Current mean | Super3 mean | Gap | Status |",
        "|---|---|---|---|---|",
    ]
    for cg in gaps:
        if cg.gap is None:
            status = "no data"
        elif cg.gap < -threshold:
            status = "behind"
        elif cg.gap > threshold:
            status = "ahead"
        else:
            status = "on par"
        lines.append(
            f"| `{cg.category}` | {_fmt(cg.current_mean)} | "
            f"{_fmt(cg.super3_mean)} | {_fmt(cg.gap, signed=True)} | {status} |"
        )
    lines.append("")

    # Drill-down for the categories that need attention.
    drill_down = [cg for cg in gaps if cg.gap is not None and cg.gap < -threshold]
    if drill_down:
        lines.append("## Drill-down — categories behind threshold")
        lines.append("")
        for cg in drill_down:
            lines.append(f"### `{cg.category}` ({_fmt(cg.gap, signed=True)})")
            lines.append("")
            lines.append("| Benchmark | Current | Super3 | Gap |")
            lines.append("|---|---|---|---|")
            for bg in cg.benchmark_gaps:
                lines.append(
                    f"| `{bg.benchmark_id}` | {_fmt(bg.current)} | "
                    f"{_fmt(bg.super3)} | {_fmt(bg.gap, signed=True)} |"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _fmt(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "—"
    if signed:
        return f"{value:+.4f}"
    return f"{value:.4f}"


__all__ = [
    "BenchmarkGap",
    "CategoryGap",
    "DEFAULT_GAP_THRESHOLD",
    "analyze_gaps",
    "count_categories_below_threshold",
    "format_gap_analysis",
]
