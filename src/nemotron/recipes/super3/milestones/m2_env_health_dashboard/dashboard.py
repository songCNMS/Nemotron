"""Build panel-ready dashboard data from a recorded M0 health report.

This module intentionally consumes a local ``health_baseline_report.json``-style
artifact. It does not talk to Grafana, W&B, cluster services, or auth-backed
telemetry streams.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

JsonDict = dict[str, Any]

DEFAULT_SLOW_LATENCY_MS = 1000.0
RUNTIME_SIGNAL_TERMS = (
    "cluster",
    "container",
    "deferred",
    "execution",
    "runtime",
    "simulator",
    "timeout",
)


def load_health_report(path: Path) -> JsonDict:
    """Load a recorded health-baseline report from disk."""

    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, Mapping):
        raise ValueError(f"health report must be a JSON object: {path}")
    return dict(data)


def build_dashboard_model(
    report: Mapping[str, Any],
    *,
    slow_latency_ms: float = DEFAULT_SLOW_LATENCY_MS,
) -> JsonDict:
    """Convert a health-baseline report into stable dashboard panels.

    The returned shape is designed for tests, Markdown reports, and future UI
    adapters. It is deliberately plain JSON: no live metrics backend and no
    external service dependencies.
    """

    health_envs = _mapping_at(report, "health", "environments")
    baseline_envs = _mapping_at(report, "baselines", "environments")
    env_ids = sorted(set(health_envs) | set(baseline_envs))

    panels: JsonDict = {
        "environment_status": [],
        "reward_quality": [],
        "latency": [],
        "telemetry_keys": [],
        "telemetry_gaps": [],
        "deferred_runtime_signals": [],
    }

    for env_id in env_ids:
        health_summary = _as_mapping(health_envs.get(env_id))
        baseline_summary = _as_mapping(baseline_envs.get(env_id))

        panels["environment_status"].append(
            _environment_status_row(env_id, health_summary, baseline_summary)
        )

        aggregates = _as_mapping(baseline_summary.get("aggregate"))
        for policy, metrics_value in sorted(aggregates.items()):
            metrics = _as_mapping(metrics_value)
            panels["reward_quality"].append(_reward_row(env_id, policy, metrics))
            panels["latency"].extend(
                _latency_rows(
                    env_id,
                    policy,
                    _as_mapping(metrics.get("telemetry")),
                    slow_latency_ms=slow_latency_ms,
                )
            )
            panels["telemetry_keys"].extend(
                _telemetry_key_rows(env_id, policy, _as_mapping(metrics.get("telemetry")))
            )
            panels["telemetry_gaps"].extend(_telemetry_gap_rows(env_id, policy, metrics))
            panels["deferred_runtime_signals"].extend(
                _runtime_signal_rows(
                    env_id,
                    policy,
                    metrics,
                    slow_latency_ms=slow_latency_ms,
                )
            )

    summary = {
        "source_schema_version": report.get("schema_version"),
        "source_status": report.get("status", "unknown"),
        "environment_count": len(env_ids),
        "failing_environments": [
            row["environment"]
            for row in panels["environment_status"]
            if row["health_status"] == "fail"
        ],
        "reward_failure_count": sum(
            1 for row in panels["reward_quality"] if row["reward_status"] == "fail"
        ),
        "telemetry_gap_count": len(panels["telemetry_gaps"]),
        "slow_latency_count": sum(1 for row in panels["latency"] if row["status"] == "slow"),
        "deferred_runtime_signal_count": len(panels["deferred_runtime_signals"]),
    }

    return {
        "schema_version": 1,
        "kind": "env_health_dashboard",
        "source_report": {
            "generated_at_utc": report.get("generated_at_utc"),
            "input_dir": report.get("input_dir"),
            "environment_registry": report.get("environment_registry"),
            "status": report.get("status", "unknown"),
            "code_execution": report.get("code_execution"),
            "rollout_policy": report.get("rollout_policy"),
        },
        "thresholds": {"slow_latency_ms": slow_latency_ms},
        "summary": summary,
        "panels": panels,
    }


def render_dashboard_markdown(model: Mapping[str, Any]) -> str:
    """Render the dashboard model as a compact Markdown report."""

    source = _as_mapping(model.get("source_report"))
    summary = _as_mapping(model.get("summary"))
    panels = _as_mapping(model.get("panels"))

    lines = [
        "# Environment Health Dashboard",
        "",
        f"- Source status: `{source.get('status', 'unknown')}`",
        f"- Source generated: `{source.get('generated_at_utc') or '-'}`",
        f"- Environments: `{summary.get('environment_count', 0)}`",
        f"- Reward failures: `{summary.get('reward_failure_count', 0)}`",
        f"- Telemetry gaps: `{summary.get('telemetry_gap_count', 0)}`",
        f"- Deferred/runtime signals: `{summary.get('deferred_runtime_signal_count', 0)}`",
        "",
        "## Environment Status",
        "",
        "| Environment | Health | Rows | Splits | Policies |",
        "|---|---|---:|---|---|",
    ]
    for row in panels.get("environment_status", []):
        item = _as_mapping(row)
        split_status = ", ".join(
            f"{name}:{status}" for name, status in sorted(_as_mapping(item.get("split_status")).items())
        )
        policies = ", ".join(str(policy) for policy in item.get("baseline_policies", []))
        lines.append(
            "| {env} | {status} | {rows} | {splits} | {policies} |".format(
                env=_md_cell(item.get("environment")),
                status=_md_cell(item.get("health_status")),
                rows=item.get("rows", 0),
                splits=_md_cell(split_status or "-"),
                policies=_md_cell(policies or "-"),
            )
        )

    lines.extend(
        [
            "",
            "## Reward Quality",
            "",
            "| Environment | Policy | Status | Rows | Scored | Skipped | pass@1 | mean score@1 | Failures |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in panels.get("reward_quality", []):
        item = _as_mapping(row)
        lines.append(
            "| {env} | {policy} | {status} | {rows} | {scored} | {skipped} | {pass_at_1} | {mean} | {failures} |".format(
                env=_md_cell(item.get("environment")),
                policy=_md_cell(item.get("policy")),
                status=_md_cell(item.get("reward_status")),
                rows=item.get("rows", 0),
                scored=item.get("scored_rows", 0),
                skipped=item.get("skipped_rows", 0),
                pass_at_1=_format_float(item.get("pass_at_1")),
                mean=_format_float(item.get("mean_score_at_1")),
                failures=item.get("failure_count", 0),
            )
        )

    lines.extend(
        [
            "",
            "## Latency",
            "",
            "| Environment | Policy | Key | Status | Mean ms | Max ms | Rows |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    latency_rows = panels.get("latency", [])
    if latency_rows:
        for row in latency_rows:
            item = _as_mapping(row)
            lines.append(
                "| {env} | {policy} | {key} | {status} | {mean} | {max_ms} | {rows} |".format(
                    env=_md_cell(item.get("environment")),
                    policy=_md_cell(item.get("policy")),
                    key=_md_cell(item.get("key")),
                    status=_md_cell(item.get("status")),
                    mean=_format_float(item.get("mean_ms")),
                    max_ms=_format_float(item.get("max_ms")),
                    rows=item.get("rows", 0),
                )
            )
    else:
        lines.append("| - | - | - | - | - | - | 0 |")

    lines.extend(
        [
            "",
            "## Telemetry Gaps",
            "",
            "| Environment | Policy | Missing Key |",
            "|---|---|---|",
        ]
    )
    gap_rows = panels.get("telemetry_gaps", [])
    if gap_rows:
        for row in gap_rows:
            item = _as_mapping(row)
            lines.append(
                "| {env} | {policy} | {key} |".format(
                    env=_md_cell(item.get("environment")),
                    policy=_md_cell(item.get("policy")),
                    key=_md_cell(item.get("missing_key")),
                )
            )
    else:
        lines.append("| - | - | - |")

    lines.extend(
        [
            "",
            "## Deferred Runtime Signals",
            "",
            "| Environment | Policy | Signal | Detail |",
            "|---|---|---|---|",
        ]
    )
    signal_rows = panels.get("deferred_runtime_signals", [])
    if signal_rows:
        for row in signal_rows:
            item = _as_mapping(row)
            lines.append(
                "| {env} | {policy} | {signal} | {detail} |".format(
                    env=_md_cell(item.get("environment")),
                    policy=_md_cell(item.get("policy")),
                    signal=_md_cell(item.get("signal")),
                    detail=_md_cell(item.get("detail")),
                )
            )
    else:
        lines.append("| - | - | - | - |")

    return "\n".join(lines) + "\n"


def write_dashboard_outputs(
    model: Mapping[str, Any],
    *,
    output_json: Path | None = None,
    output_markdown: Path | None = None,
) -> None:
    """Write selected dashboard outputs."""

    if output_json is not None:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(model, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
    if output_markdown is not None:
        output_markdown.parent.mkdir(parents=True, exist_ok=True)
        output_markdown.write_text(render_dashboard_markdown(model), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-report", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-markdown", type=Path, default=None)
    parser.add_argument("--slow-latency-ms", type=float, default=DEFAULT_SLOW_LATENCY_MS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = load_health_report(args.input_report)
    model = build_dashboard_model(report, slow_latency_ms=args.slow_latency_ms)
    if args.output_json is None and args.output_markdown is None:
        print(json.dumps(model, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        write_dashboard_outputs(
            model,
            output_json=args.output_json,
            output_markdown=args.output_markdown,
        )
    return 0


def _environment_status_row(
    env_id: str,
    health_summary: Mapping[str, Any],
    baseline_summary: Mapping[str, Any],
) -> JsonDict:
    splits = _as_mapping(health_summary.get("splits"))
    split_status = {}
    split_rows: JsonDict = {}
    total_rows = 0
    for split, summary_value in sorted(splits.items()):
        split_summary = _as_mapping(summary_value)
        split_status[split] = split_summary.get("status", "unknown")
        rows = _as_int(split_summary.get("rows"))
        split_rows[split] = rows
        total_rows += rows

    aggregates = _as_mapping(baseline_summary.get("aggregate"))
    return {
        "environment": env_id,
        "health_status": health_summary.get("status", "unknown"),
        "rows": total_rows,
        "split_rows": split_rows,
        "split_status": split_status,
        "baseline_policies": sorted(aggregates.keys()),
    }


def _reward_row(env_id: str, policy: str, metrics: Mapping[str, Any]) -> JsonDict:
    pass_at_1 = _as_float(metrics.get("pass_at_1"))
    scored_rows = _as_int(metrics.get("scored_rows", metrics.get("rows", 0)))
    failure_count = _as_int(metrics.get("failure_count"))
    reward_status = "pass"
    status_reason = "pass_at_1 is 1.0 with no failures"
    if scored_rows == 0:
        reward_status = "fail"
        status_reason = "no scored rows"
    elif pass_at_1 is None:
        reward_status = "unknown"
        status_reason = "pass_at_1 missing"
    elif pass_at_1 < 1.0 or failure_count:
        reward_status = "fail"
        status_reason = "pass_at_1 below 1.0 or failures present"

    best_metric_name, best_metric_value = _first_metric(metrics, prefix="best_at_")
    return {
        "environment": env_id,
        "policy": policy,
        "reward_status": reward_status,
        "status_reason": status_reason,
        "rows": _as_int(metrics.get("rows")),
        "scored_rows": scored_rows,
        "skipped_rows": _as_int(metrics.get("skipped_rows")),
        "pass_at_1": pass_at_1,
        "mean_score_at_1": _as_float(metrics.get("mean_score_at_1")),
        "best_metric": best_metric_name,
        "best_metric_value": best_metric_value,
        "failure_count": failure_count,
    }


def _latency_rows(
    env_id: str,
    policy: str,
    telemetry: Mapping[str, Any],
    *,
    slow_latency_ms: float,
) -> list[JsonDict]:
    rows = []
    for key, summary_value in sorted(telemetry.items()):
        summary = _as_mapping(summary_value)
        if summary.get("kind") != "numeric" or not key.endswith("_ms"):
            continue
        mean_ms = _as_float(summary.get("mean"))
        max_ms = _as_float(summary.get("max"))
        status = "slow" if mean_ms is not None and mean_ms >= slow_latency_ms else "ok"
        rows.append(
            {
                "environment": env_id,
                "policy": policy,
                "key": key,
                "status": status,
                "threshold_ms": slow_latency_ms,
                "min_ms": _as_float(summary.get("min")),
                "mean_ms": mean_ms,
                "max_ms": max_ms,
                "rows": _as_int(summary.get("rows")),
            }
        )
    return rows


def _telemetry_key_rows(env_id: str, policy: str, telemetry: Mapping[str, Any]) -> list[JsonDict]:
    rows = []
    for key, summary_value in sorted(telemetry.items()):
        summary = _as_mapping(summary_value)
        rows.append(
            {
                "environment": env_id,
                "policy": policy,
                "key": key,
                "kind": summary.get("kind", "unknown"),
                "rows": _as_int(summary.get("rows")),
                "summary": dict(summary),
            }
        )
    return rows


def _telemetry_gap_rows(env_id: str, policy: str, metrics: Mapping[str, Any]) -> list[JsonDict]:
    return [
        {"environment": env_id, "policy": policy, "missing_key": str(name)}
        for name in metrics.get("telemetry_gap", []) or []
    ]


def _runtime_signal_rows(
    env_id: str,
    policy: str,
    metrics: Mapping[str, Any],
    *,
    slow_latency_ms: float,
) -> list[JsonDict]:
    rows: list[JsonDict] = []
    telemetry = _as_mapping(metrics.get("telemetry"))
    declared = [str(name) for name in metrics.get("declared_telemetry", []) or []]
    emitted_keys = set(telemetry.keys())

    for key in sorted(set(declared) | emitted_keys):
        if _looks_runtime_related(key):
            rows.append(
                {
                    "environment": env_id,
                    "policy": policy,
                    "signal": key,
                    "detail": "declared" if key in declared else "emitted",
                }
            )

    for gap in metrics.get("telemetry_gap", []) or []:
        gap_name = str(gap)
        if _looks_runtime_related(gap_name):
            rows.append(
                {
                    "environment": env_id,
                    "policy": policy,
                    "signal": gap_name,
                    "detail": "declared but not emitted",
                }
            )

    for latency in _latency_rows(
        env_id,
        policy,
        telemetry,
        slow_latency_ms=slow_latency_ms,
    ):
        if latency["status"] == "slow":
            rows.append(
                {
                    "environment": env_id,
                    "policy": policy,
                    "signal": latency["key"],
                    "detail": f"mean {latency['mean_ms']} ms >= threshold {slow_latency_ms} ms",
                }
            )

    if _as_int(metrics.get("skipped_rows")):
        rows.append(
            {
                "environment": env_id,
                "policy": policy,
                "signal": "skipped_rows",
                "detail": f"{_as_int(metrics.get('skipped_rows'))} baseline rows skipped",
            }
        )

    return _dedupe_signal_rows(rows)


def _dedupe_signal_rows(rows: Sequence[Mapping[str, Any]]) -> list[JsonDict]:
    out: list[JsonDict] = []
    seen: set[tuple[str, str, str, str]] = set()
    for row in rows:
        key = (
            str(row.get("environment", "")),
            str(row.get("policy", "")),
            str(row.get("signal", "")),
            str(row.get("detail", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(row))
    return out


def _looks_runtime_related(name: str) -> bool:
    lowered = name.lower()
    return any(term in lowered for term in RUNTIME_SIGNAL_TERMS)


def _mapping_at(data: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    current: Any = data
    for key in keys:
        current = _as_mapping(current).get(key)
    return _as_mapping(current)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_metric(metrics: Mapping[str, Any], *, prefix: str) -> tuple[str | None, float | None]:
    for name in sorted(metrics):
        if name.startswith(prefix):
            return name, _as_float(metrics.get(name))
    return None, None


def _format_float(value: Any) -> str:
    number = _as_float(value)
    return "-" if number is None else f"{number:.3f}"


def _md_cell(value: Any) -> str:
    text = "-" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
