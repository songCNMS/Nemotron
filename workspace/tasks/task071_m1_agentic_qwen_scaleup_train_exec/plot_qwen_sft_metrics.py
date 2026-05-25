#!/usr/bin/env python3
# ruff: noqa: E402,I001

"""Parse Qwen SFT train logs and write metric curves plus a health summary."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?"
TRAIN_RE = re.compile(
    rf"\[(?P<timestamp>[^\]]+)\]\s+iteration\s+(?P<iteration>\d+)/\s*(?P<total_iterations>\d+)"
    rf"\s+\|\s+consumed samples:\s+(?P<consumed_samples>\d+)"
    rf"\s+\|\s+elapsed time per iteration \(ms\):\s+(?P<elapsed_ms>{FLOAT})"
    rf"\s+\|\s+learning rate:\s+(?P<learning_rate>{FLOAT})"
    rf"\s+\|\s+global batch size:\s+(?P<global_batch_size>\d+)"
    rf"\s+\|\s+lm loss:\s+(?P<lm_loss>{FLOAT})"
    rf"\s+\|\s+load_balancing_loss:\s+(?P<load_balancing_loss>{FLOAT})"
    rf"\s+\|\s+loss scale:\s+(?P<loss_scale>{FLOAT})"
    rf"\s+\|\s+grad norm:\s+(?P<grad_norm>{FLOAT})"
    rf"\s+\|\s+number of skipped iterations:\s+(?P<skipped_iterations>\d+)"
    rf"\s+\|\s+number of nan iterations:\s+(?P<nan_iterations>\d+)"
)
VALID_RE = re.compile(
    rf"validation loss at iteration\s+(?P<iteration>\d+)"
    rf"\s+\|\s+lm loss value:\s+(?P<lm_loss>{FLOAT})"
    rf"\s+\|\s+lm loss PPL:\s+(?P<ppl>{FLOAT})"
)


@dataclass(frozen=True)
class TrainPoint:
    timestamp: str
    iteration: int
    total_iterations: int
    consumed_samples: int
    elapsed_ms: float
    learning_rate: float
    global_batch_size: int
    lm_loss: float
    load_balancing_loss: float
    loss_scale: float
    grad_norm: float
    skipped_iterations: int
    nan_iterations: int


@dataclass(frozen=True)
class ValidationPoint:
    iteration: int
    lm_loss: float
    ppl: float


def _float(value: str) -> float:
    return float(value)


def parse_log(path: Path) -> tuple[list[TrainPoint], list[ValidationPoint]]:
    train: list[TrainPoint] = []
    validation: list[ValidationPoint] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if match := TRAIN_RE.search(line):
                gd = match.groupdict()
                train.append(
                    TrainPoint(
                        timestamp=gd["timestamp"],
                        iteration=int(gd["iteration"]),
                        total_iterations=int(gd["total_iterations"]),
                        consumed_samples=int(gd["consumed_samples"]),
                        elapsed_ms=_float(gd["elapsed_ms"]),
                        learning_rate=_float(gd["learning_rate"]),
                        global_batch_size=int(gd["global_batch_size"]),
                        lm_loss=_float(gd["lm_loss"]),
                        load_balancing_loss=_float(gd["load_balancing_loss"]),
                        loss_scale=_float(gd["loss_scale"]),
                        grad_norm=_float(gd["grad_norm"]),
                        skipped_iterations=int(gd["skipped_iterations"]),
                        nan_iterations=int(gd["nan_iterations"]),
                    )
                )
                continue
            if match := VALID_RE.search(line):
                gd = match.groupdict()
                validation.append(
                    ValidationPoint(
                        iteration=int(gd["iteration"]),
                        lm_loss=_float(gd["lm_loss"]),
                        ppl=_float(gd["ppl"]),
                    )
                )
    return train, validation


def write_csv(path: Path, rows: list[TrainPoint] | list[ValidationPoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _recent_stats(points: list[TrainPoint], n: int = 50) -> dict[str, float] | None:
    if not points:
        return None
    values = [p.lm_loss for p in points[-n:]]
    return {
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
    }


def _validation_trend(validation: list[ValidationPoint]) -> str:
    if len(validation) < 2:
        return "not-enough-validation-points"
    if validation[-1].lm_loss < validation[-2].lm_loss:
        return "latest-validation-improved-vs-previous"
    if validation[-1].lm_loss > validation[-2].lm_loss:
        return "latest-validation-regressed-vs-previous"
    return "latest-validation-unchanged-vs-previous"


def build_summary(run_name: str, log_path: Path, train: list[TrainPoint], validation: list[ValidationPoint]) -> dict:
    latest = train[-1] if train else None
    recent = _recent_stats(train)
    best_validation = min(validation, key=lambda p: p.lm_loss) if validation else None
    summary = {
        "run_name": run_name,
        "log_path": str(log_path),
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "training_points": len(train),
        "validation_points": len(validation),
        "latest_iteration": latest.iteration if latest else None,
        "total_iterations": latest.total_iterations if latest else None,
        "progress_pct": round(latest.iteration / latest.total_iterations * 100, 2) if latest else None,
        "latest_lm_loss": latest.lm_loss if latest else None,
        "latest_lr": latest.learning_rate if latest else None,
        "latest_grad_norm": latest.grad_norm if latest else None,
        "latest_load_balancing_loss": latest.load_balancing_loss if latest else None,
        "latest_skipped_iterations": latest.skipped_iterations if latest else None,
        "latest_nan_iterations": latest.nan_iterations if latest else None,
        "max_skipped_iterations_reported": max((p.skipped_iterations for p in train), default=0),
        "max_nan_iterations_reported": max((p.nan_iterations for p in train), default=0),
        "recent_50_lm_loss": recent,
        "latest_validation": asdict(validation[-1]) if validation else None,
        "previous_validation": asdict(validation[-2]) if len(validation) >= 2 else None,
        "best_validation": asdict(best_validation) if best_validation else None,
        "validation_trend": _validation_trend(validation),
    }
    return summary


def _load_validation_csv(path: Path) -> dict[int, ValidationPoint]:
    if not path.is_file():
        return {}
    rows: dict[int, ValidationPoint] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[int(row["iteration"])] = ValidationPoint(
                iteration=int(row["iteration"]),
                lm_loss=float(row.get("lm_loss") or row.get("val_lm_loss")),
                ppl=float(row.get("ppl") or row.get("val_ppl")),
            )
    return rows


def build_comparison(
    *,
    current: list[ValidationPoint],
    baseline_validation_csv: Path | None,
    baseline_name: str,
) -> list[dict[str, float | int]]:
    if baseline_validation_csv is None:
        return []
    baseline = _load_validation_csv(baseline_validation_csv)
    rows = []
    for point in current:
        if point.iteration not in baseline:
            continue
        base = baseline[point.iteration]
        rows.append(
            {
                "iteration": point.iteration,
                "current_lm_loss": point.lm_loss,
                f"{baseline_name}_lm_loss": base.lm_loss,
                "current_minus_baseline_lm_loss": point.lm_loss - base.lm_loss,
                "current_ppl": point.ppl,
                f"{baseline_name}_ppl": base.ppl,
                "current_minus_baseline_ppl": point.ppl - base.ppl,
            }
        )
    return rows


def write_comparison_md(path: Path, run_name: str, baseline_name: str, rows: list[dict[str, float | int]]) -> None:
    lines = [
        f"# {run_name} Early Validation Comparison",
        "",
        f"Baseline: `{baseline_name}`",
        "",
    ]
    if not rows:
        lines.append("No common validation checkpoints were available.")
    else:
        lines.extend(
            [
                "| Iteration | Current loss | Baseline loss | Delta loss | Current PPL | Baseline PPL | Delta PPL |",
                "|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in rows:
            lines.append(
                "| {iteration} | {current_lm_loss:.7f} | {baseline_lm_loss:.7f} | "
                "{delta_lm_loss:+.7f} | {current_ppl:.6f} | {baseline_ppl:.6f} | {delta_ppl:+.6f} |".format(
                    iteration=row["iteration"],
                    current_lm_loss=row["current_lm_loss"],
                    baseline_lm_loss=row[f"{baseline_name}_lm_loss"],
                    delta_lm_loss=row["current_minus_baseline_lm_loss"],
                    current_ppl=row["current_ppl"],
                    baseline_ppl=row[f"{baseline_name}_ppl"],
                    delta_ppl=row["current_minus_baseline_ppl"],
                )
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_metrics(path: Path, run_name: str, train: list[TrainPoint], validation: list[ValidationPoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.suptitle(run_name)

    iterations = [p.iteration for p in train]
    axes[0, 0].plot(iterations, [p.lm_loss for p in train], linewidth=1.2)
    axes[0, 0].set_title("Train LM Loss")
    axes[0, 0].set_xlabel("Iteration")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].grid(True, alpha=0.3)

    if validation:
        val_iters = [p.iteration for p in validation]
        axes[0, 1].plot(val_iters, [p.lm_loss for p in validation], marker="o", label="validation loss")
        axes_ppl = axes[0, 1].twinx()
        axes_ppl.plot(val_iters, [p.ppl for p in validation], color="tab:orange", marker="s", label="validation PPL")
        axes[0, 1].set_ylabel("Loss")
        axes_ppl.set_ylabel("PPL")
    axes[0, 1].set_title("Validation")
    axes[0, 1].set_xlabel("Iteration")
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(iterations, [p.learning_rate for p in train], linewidth=1.2)
    axes[1, 0].set_title("Learning Rate")
    axes[1, 0].set_xlabel("Iteration")
    axes[1, 0].set_ylabel("LR")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(iterations, [p.grad_norm for p in train], label="grad norm", linewidth=1.0)
    axes[1, 1].plot(iterations, [p.load_balancing_loss for p in train], label="load balancing loss", linewidth=1.0)
    max_bad = max([p.skipped_iterations + p.nan_iterations for p in train], default=0)
    if max_bad > 0:
        axes[1, 1].plot(iterations, [p.skipped_iterations for p in train], label="skipped", linewidth=1.0)
        axes[1, 1].plot(iterations, [p.nan_iterations for p in train], label="nan", linewidth=1.0)
    axes[1, 1].set_title("Optimizer / Health")
    axes[1, 1].set_xlabel("Iteration")
    axes[1, 1].legend(loc="best")
    axes[1, 1].grid(True, alpha=0.3)

    for ax in axes.flat:
        ax.set_xlim(left=0, right=max(iterations) if iterations else 1)
        if not ax.lines:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--baseline-validation-csv", type=Path, default=None)
    parser.add_argument("--baseline-name", default="baseline")
    args = parser.parse_args()

    train, validation = parse_log(args.log)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "train_loss_points.csv", train)
    write_csv(args.out_dir / "validation_points.csv", validation)
    summary = build_summary(args.run_name, args.log, train, validation)

    comparison = build_comparison(
        current=validation,
        baseline_validation_csv=args.baseline_validation_csv,
        baseline_name=args.baseline_name,
    )
    if comparison:
        summary["comparison"] = comparison
        write_comparison_md(
            args.out_dir / f"early_comparison_vs_{args.baseline_name}.md",
            args.run_name,
            args.baseline_name,
            comparison,
        )
    (args.out_dir / "health_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    plot_metrics(args.out_dir / "metric_curves.png", args.run_name, train, validation)

    if not train:
        raise ValueError(f"no train points parsed from {args.log}")
    if not validation:
        raise ValueError(f"no validation points parsed from {args.log}")
    if any(math.isnan(p.lm_loss) for p in train):
        raise ValueError("parsed NaN train loss")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
