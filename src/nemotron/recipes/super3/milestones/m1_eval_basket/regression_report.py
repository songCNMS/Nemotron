# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Generate a regression report comparing two NeMo Evaluator runs.

Roadmap §1.7 task019 acceptance: ``nemotron super3 eval -c m1_basket``
runs against an SFT checkpoint and produces ``regression_report.md``
showing per-task gain/loss vs the previous checkpoint. This module is
the offline part — it reads two NeMo Evaluator output JSONs (one
current, one baseline) and emits the markdown report.

NeMo Evaluator JSON format (per task) follows the shape::

    {
      "model": {"name": "super3-sft:v2", "checkpoint": "iter_5000"},
      "tasks": {
        "<benchmark_id>": {
          "metrics": {"<metric_name>": <float>, ...},
          "samples": <int>,
          "runtime_s": <float>
        },
        ...
      }
    }

The report calls each benchmark *improved* / *regressed* /
*unchanged* / *new* / *dropped* based on the diff against the
baseline. ``gate_metric`` from ``m1_eval_basket_registry.yaml``
selects which metric matters per benchmark (so the same JSON can
serve multiple metric audits).

Pure stdlib + pyyaml; sandbox-runnable. Wiring the CLI
``nemotron super3 eval`` invocation to produce the JSONs and call
this module is Session 2 — needs cluster access.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]


# Floating-point comparisons with tolerance — eval runs aren't bit-exact.
# Default tolerance picks up nontrivial drift while ignoring run-to-run
# noise from sampling. Operators can override at call time.
DEFAULT_REGRESSION_TOLERANCE = 1e-4


@dataclass(frozen=True)
class BenchmarkDelta:
    """One per-benchmark row in the regression report."""

    benchmark_id: str
    metric: str
    baseline: float | None
    current: float | None
    delta: float | None       # current - baseline, or None when one side is missing
    status: str               # "improved" / "regressed" / "unchanged" / "new" / "dropped"

    def to_jsonable(self) -> JsonDict:
        return {
            "benchmark_id": self.benchmark_id,
            "metric": self.metric,
            "baseline": self.baseline,
            "current": self.current,
            "delta": self.delta,
            "status": self.status,
        }


def load_eval_results(path: Path | str) -> JsonDict:
    """Read a NeMo Evaluator output JSON.

    Returns the top-level dict as-is. Caller is responsible for
    interpreting the ``tasks`` block. Raises ``FileNotFoundError`` /
    ``ValueError`` (via json.JSONDecodeError) if the file is missing
    or malformed.
    """
    target = Path(path)
    with target.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "tasks" not in data:
        raise ValueError(
            f"{target}: NeMo Evaluator JSON must declare a 'tasks' dict at top level"
        )
    return data


def _gate_metric_lookup(registry_rows: list[Mapping[str, Any]]) -> dict[str, str]:
    """Build a ``{benchmark_id: gate_metric}`` map for the report."""
    return {row["benchmark_id"]: row["gate_metric"] for row in registry_rows}


def diff_eval_runs(
    current: Mapping[str, Any],
    baseline: Mapping[str, Any],
    *,
    gate_metric_by_id: Mapping[str, str],
    tolerance: float = DEFAULT_REGRESSION_TOLERANCE,
) -> list[BenchmarkDelta]:
    """Compute per-benchmark deltas between two eval runs.

    Iterates the union of benchmark_ids in ``current.tasks`` ∪
    ``baseline.tasks``. For each:

    - ``new``: present in current, absent in baseline (no delta)
    - ``dropped``: present in baseline, absent in current (no delta)
    - ``unchanged``: both present, |delta| <= tolerance
    - ``improved``: both present, current > baseline beyond tolerance
    - ``regressed``: both present, current < baseline beyond tolerance

    Benchmarks not in ``gate_metric_by_id`` are skipped — the registry
    is the authoritative list of benchmarks the gate cares about.

    Output is sorted by ``benchmark_id`` for stable diff-friendly
    markdown.
    """
    current_tasks = current.get("tasks", {})
    baseline_tasks = baseline.get("tasks", {})
    all_ids = (set(current_tasks.keys()) | set(baseline_tasks.keys())) & set(
        gate_metric_by_id.keys()
    )

    deltas: list[BenchmarkDelta] = []
    for benchmark_id in sorted(all_ids):
        metric = gate_metric_by_id[benchmark_id]
        baseline_value = _extract_metric(baseline_tasks.get(benchmark_id), metric)
        current_value = _extract_metric(current_tasks.get(benchmark_id), metric)

        if current_value is None and baseline_value is None:
            # Both runs lack the metric — skip rather than emit a
            # vacuous row.
            continue
        if baseline_value is None:
            deltas.append(
                BenchmarkDelta(
                    benchmark_id=benchmark_id,
                    metric=metric,
                    baseline=None,
                    current=current_value,
                    delta=None,
                    status="new",
                )
            )
            continue
        if current_value is None:
            deltas.append(
                BenchmarkDelta(
                    benchmark_id=benchmark_id,
                    metric=metric,
                    baseline=baseline_value,
                    current=None,
                    delta=None,
                    status="dropped",
                )
            )
            continue
        delta = current_value - baseline_value
        if abs(delta) <= tolerance:
            status = "unchanged"
        elif delta > 0:
            status = "improved"
        else:
            status = "regressed"
        deltas.append(
            BenchmarkDelta(
                benchmark_id=benchmark_id,
                metric=metric,
                baseline=baseline_value,
                current=current_value,
                delta=delta,
                status=status,
            )
        )
    return deltas


def _extract_metric(task_block: Any, metric: str) -> float | None:
    """Pull *metric* out of a single NeMo Evaluator task block.

    Returns None when the task is absent, the metrics dict is missing,
    or the metric isn't present. Non-numeric values also return None
    (caller can flag separately if needed).
    """
    if not isinstance(task_block, Mapping):
        return None
    metrics = task_block.get("metrics")
    if not isinstance(metrics, Mapping):
        return None
    value = metrics.get(metric)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


STATUS_MARKERS = {
    "improved": "↑",
    "regressed": "↓",
    "unchanged": "·",
    "new": "+",
    "dropped": "-",
}


def format_regression_report(
    deltas: list[BenchmarkDelta],
    *,
    current_label: str = "current",
    baseline_label: str = "baseline",
) -> str:
    """Render the regression report as markdown.

    Layout: summary header + per-benchmark table. Each row shows the
    status marker (↑ / ↓ / · / + / -) so a quick visual scan tells
    the operator whether the gate held. Delta column carries the raw
    number for precise review.
    """
    if not deltas:
        return (
            f"# Regression report — {current_label} vs {baseline_label}\n\n"
            "(no benchmarks compared — eval JSONs share no benchmarks that "
            "appear in the M1 eval basket registry)\n"
        )
    counts: dict[str, int] = {}
    for delta in deltas:
        counts[delta.status] = counts.get(delta.status, 0) + 1
    summary_parts = [
        f"{counts[status]} {status}"
        for status in ("improved", "regressed", "unchanged", "new", "dropped")
        if counts.get(status, 0) > 0
    ]
    summary = ", ".join(summary_parts) or "no findings"

    lines = [
        f"# Regression report — {current_label} vs {baseline_label}",
        "",
        f"**Summary**: {summary}",
        "",
        "| Status | Benchmark | Metric | Baseline | Current | Δ |",
        "|---|---|---|---|---|---|",
    ]
    for delta in deltas:
        marker = STATUS_MARKERS.get(delta.status, "?")
        baseline_cell = _fmt(delta.baseline)
        current_cell = _fmt(delta.current)
        delta_cell = _fmt(delta.delta, signed=True)
        lines.append(
            f"| {marker} {delta.status} | `{delta.benchmark_id}` | "
            f"{delta.metric} | {baseline_cell} | {current_cell} | {delta_cell} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def _fmt(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "—"
    if signed:
        return f"{value:+.4f}"
    return f"{value:.4f}"


__all__ = [
    "BenchmarkDelta",
    "DEFAULT_REGRESSION_TOLERANCE",
    "STATUS_MARKERS",
    "diff_eval_runs",
    "format_regression_report",
    "load_eval_results",
]
