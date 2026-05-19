# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""M1 promotion gate per plan §5.7 / roadmap §1.7 task020.

The M1 acceptance criterion is

    "Match or approach Super3 on the repo Super3 eval basket. Target
    weighted average within 1-2% of Super3 with no major category
    regression."

plus the roadmap-specific rule

    "Promotion gate logic: weighted-mean Super3 parity, no key-category
    regression > 1-2 %, rollback rule on safety / SWE / tool / IF."

This module turns the eval JSON into a promote / hold / rollback
decision. Inputs are pure dicts so the module is sandbox-runnable and
exercised entirely from pytest — Session 3 wires it into the
``nemotron super3 eval`` CLI against real Super3 numbers.

Decision precedence (most severe wins):

1. **Rollback** — any benchmark whose ``category`` is in
   ``DEFAULT_ROLLBACK_CATEGORIES`` regressed vs Super3 beyond
   ``regression_tolerance``. These are the categories the plan names as
   critical (safety / SWE / tool use / instruction following).
2. **Hold** — non-rollback category regressed by more than
   ``category_regression_threshold`` OR overall weighted parity drift
   exceeds ``weighted_parity_threshold``.
3. **Promote** — neither rollback nor hold conditions tripped.

Weighting policy: uniform within category, uniform across categories.
A category with 5 benchmarks doesn't get 5× the influence on the
weighted mean. This protects against accidental category dominance
when the basket grows asymmetrically.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any


# Defaults pulled from plan §5.7 + roadmap §1.7. Operators may tighten
# per-run; loosening below these defaults should be a deliberate
# decision recorded in the run config.
DEFAULT_WEIGHTED_PARITY_THRESHOLD = 0.02     # 2% — "within 1-2% of Super3"
DEFAULT_CATEGORY_REGRESSION_THRESHOLD = 0.02  # 2% — "no key-category regression > 1-2%"
DEFAULT_ROLLBACK_REGRESSION_TOLERANCE = 1e-4  # rollback triggers on *any* drop beyond noise

# Critical categories: ANY regression beyond noise here triggers rollback
# instead of just hold. Per plan §5.7: "rollback rule on safety / SWE /
# tool / IF". Safety is M2 territory (no category in our M1 basket yet),
# but we list a forward-compatible name so adding `safety_*` rows later
# auto-triggers the rollback path.
DEFAULT_ROLLBACK_CATEGORIES: frozenset[str] = frozenset({
    "swe_repo_repair",
    "tool_use_agentic",
    "tool_use_terminal",
    "tool_use_function_call",
    "tool_use_mcp",
    "instruction_following",
    "multi_turn_instruction",
    "safety",
    "safety_jailbreak",
    "safety_overrefusal",
})


GATE_STATUSES = ("promote", "hold", "rollback")


@dataclass(frozen=True)
class PromotionDecision:
    """The output of one promotion-gate evaluation.

    ``status`` is the headline decision; the other fields surface the
    inputs the decision is based on so a human reviewer can sanity
    check (and so the markdown report can render an evidence table).
    """

    status: str                                  # promote / hold / rollback
    weighted_parity_delta: float | None          # current - super3 across all categories
    weighted_parity_within_threshold: bool
    category_deltas: dict[str, float]            # category -> (current_mean - super3_mean)
    categories_in_regression: tuple[str, ...]    # category names that exceeded regression threshold
    rollback_triggers: tuple[str, ...]           # rollback-categories that regressed (any amount)
    benchmarks_missing_in_current: tuple[str, ...]
    benchmarks_missing_in_super3: tuple[str, ...]
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "weighted_parity_delta": self.weighted_parity_delta,
            "weighted_parity_within_threshold": self.weighted_parity_within_threshold,
            "category_deltas": dict(self.category_deltas),
            "categories_in_regression": list(self.categories_in_regression),
            "rollback_triggers": list(self.rollback_triggers),
            "benchmarks_missing_in_current": list(self.benchmarks_missing_in_current),
            "benchmarks_missing_in_super3": list(self.benchmarks_missing_in_super3),
            "reasons": list(self.reasons),
        }


def _group_by_category(
    registry_rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[str]]:
    """Return ``{category: [benchmark_id, ...]}`` from registry rows.

    Skips rows missing either ``category`` or ``benchmark_id`` to keep
    the gate resilient against partial input — the schema layer is the
    place to enforce shape, not the gate.
    """
    out: dict[str, list[str]] = {}
    for row in registry_rows:
        bid = row.get("benchmark_id")
        cat = row.get("category")
        if not bid or not cat:
            continue
        out.setdefault(cat, []).append(bid)
    return out


def _category_mean(
    benchmark_ids: Iterable[str], scores: Mapping[str, float]
) -> float | None:
    """Mean across benchmarks in a category, skipping missing entries.

    Returns ``None`` when no benchmark in the category has a score —
    callers treat None as "category not evaluated" rather than dragging
    the weighted mean toward zero.
    """
    values = [scores[bid] for bid in benchmark_ids if bid in scores]
    if not values:
        return None
    return sum(values) / len(values)


def evaluate_promotion_gate(
    current_results: Mapping[str, float],
    super3_baseline: Mapping[str, float],
    registry_rows: Iterable[Mapping[str, Any]],
    *,
    weighted_parity_threshold: float = DEFAULT_WEIGHTED_PARITY_THRESHOLD,
    category_regression_threshold: float = DEFAULT_CATEGORY_REGRESSION_THRESHOLD,
    rollback_regression_tolerance: float = DEFAULT_ROLLBACK_REGRESSION_TOLERANCE,
    rollback_categories: frozenset[str] = DEFAULT_ROLLBACK_CATEGORIES,
) -> PromotionDecision:
    """Apply the plan §5.7 promotion gate to one eval run.

    ``current_results`` and ``super3_baseline`` are flat ``{benchmark_id:
    score}`` maps. The gate handles missing entries on either side
    explicitly (a benchmark missing in Super3 cannot block promotion;
    a benchmark missing in current is *noted* but does not by itself
    flip the gate — the operator decides whether to hold for coverage).

    Order of severity: rollback > hold > promote. ``reasons`` lists
    every condition that contributed so the operator can see all the
    findings, not just the one that tipped the decision.
    """
    rows = list(registry_rows)
    category_to_benchmarks = _group_by_category(rows)
    benchmark_to_category: dict[str, str] = {}
    for row in rows:
        bid = row.get("benchmark_id")
        cat = row.get("category")
        if bid and cat:
            benchmark_to_category[bid] = cat

    all_registry_ids = set(benchmark_to_category)
    missing_in_current = tuple(sorted(all_registry_ids - set(current_results)))
    missing_in_super3 = tuple(sorted(all_registry_ids - set(super3_baseline)))

    # Per-category means + delta vs Super3
    category_deltas: dict[str, float] = {}
    for category, benchmark_ids in category_to_benchmarks.items():
        cur_mean = _category_mean(benchmark_ids, current_results)
        ref_mean = _category_mean(benchmark_ids, super3_baseline)
        if cur_mean is None or ref_mean is None:
            # Skip uncomputable categories; they contribute neither to
            # the weighted mean nor to the regression check.
            continue
        category_deltas[category] = cur_mean - ref_mean

    # Weighted parity: uniform across categories (each category counts once)
    if category_deltas:
        weighted_parity_delta: float | None = sum(category_deltas.values()) / len(category_deltas)
    else:
        weighted_parity_delta = None
    parity_within = (
        weighted_parity_delta is not None
        and abs(weighted_parity_delta) <= weighted_parity_threshold
    )

    # Categories regressed beyond the non-rollback threshold
    categories_in_regression = tuple(
        sorted(
            cat for cat, delta in category_deltas.items()
            if delta < -category_regression_threshold and cat not in rollback_categories
        )
    )

    # Rollback triggers: any rollback-category regressed beyond noise
    rollback_triggers = tuple(
        sorted(
            cat for cat, delta in category_deltas.items()
            if cat in rollback_categories and delta < -rollback_regression_tolerance
        )
    )

    reasons: list[str] = []
    if rollback_triggers:
        for cat in rollback_triggers:
            reasons.append(
                f"rollback: category {cat!r} regressed {category_deltas[cat]:+.4f} "
                f"(any drop in rollback categories is critical)"
            )
    if categories_in_regression:
        for cat in categories_in_regression:
            reasons.append(
                f"hold: category {cat!r} regressed {category_deltas[cat]:+.4f} "
                f"(threshold {category_regression_threshold:+.4f})"
            )
    if weighted_parity_delta is None:
        reasons.append("hold: no shared categories between current and Super3 baseline")
    elif not parity_within:
        reasons.append(
            f"hold: weighted parity delta {weighted_parity_delta:+.4f} "
            f"exceeds threshold ±{weighted_parity_threshold:.4f}"
        )

    if rollback_triggers:
        status = "rollback"
    elif categories_in_regression or weighted_parity_delta is None or not parity_within:
        status = "hold"
    else:
        status = "promote"
        reasons.append(
            f"promote: weighted parity {weighted_parity_delta:+.4f} within "
            f"±{weighted_parity_threshold:.4f}; no category regressed beyond "
            f"thresholds"
        )

    return PromotionDecision(
        status=status,
        weighted_parity_delta=weighted_parity_delta,
        weighted_parity_within_threshold=parity_within,
        category_deltas=dict(sorted(category_deltas.items())),
        categories_in_regression=categories_in_regression,
        rollback_triggers=rollback_triggers,
        benchmarks_missing_in_current=missing_in_current,
        benchmarks_missing_in_super3=missing_in_super3,
        reasons=tuple(reasons),
    )


_STATUS_MARKERS = {"promote": "✓", "hold": "⚠", "rollback": "✗"}


def format_gate_report(decision: PromotionDecision) -> str:
    """Render a promotion gate decision as markdown.

    Layout: headline status + reasons list + per-category delta table.
    Missing-benchmark lists are appended only when non-empty so a clean
    run produces a clean report.
    """
    marker = _STATUS_MARKERS.get(decision.status, "?")
    lines = [
        f"# Promotion gate decision: {marker} **{decision.status.upper()}**",
        "",
    ]

    if decision.weighted_parity_delta is None:
        lines.append("**Weighted parity vs Super3**: — (no shared categories)")
    else:
        lines.append(
            f"**Weighted parity vs Super3**: {decision.weighted_parity_delta:+.4f} "
            f"({'within' if decision.weighted_parity_within_threshold else 'outside'} threshold)"
        )
    lines.append("")

    if decision.reasons:
        lines.append("**Reasons**:")
        for reason in decision.reasons:
            lines.append(f"- {reason}")
        lines.append("")

    if decision.category_deltas:
        lines.append("| Category | Δ vs Super3 |")
        lines.append("|---|---|")
        for category, delta in decision.category_deltas.items():
            lines.append(f"| `{category}` | {delta:+.4f} |")
        lines.append("")

    if decision.benchmarks_missing_in_current:
        lines.append(
            "**Benchmarks missing in current run**: "
            + ", ".join(f"`{b}`" for b in decision.benchmarks_missing_in_current)
        )
        lines.append("")

    if decision.benchmarks_missing_in_super3:
        lines.append(
            "**Benchmarks missing in Super3 baseline**: "
            + ", ".join(f"`{b}`" for b in decision.benchmarks_missing_in_super3)
        )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "DEFAULT_CATEGORY_REGRESSION_THRESHOLD",
    "DEFAULT_ROLLBACK_CATEGORIES",
    "DEFAULT_ROLLBACK_REGRESSION_TOLERANCE",
    "DEFAULT_WEIGHTED_PARITY_THRESHOLD",
    "GATE_STATUSES",
    "PromotionDecision",
    "evaluate_promotion_gate",
    "format_gate_report",
]
