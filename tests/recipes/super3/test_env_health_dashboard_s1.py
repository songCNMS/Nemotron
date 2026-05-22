import json
from argparse import Namespace
from pathlib import Path

from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (
    build_report,
    summarize_baselines,
    summarize_health,
)
from nemotron.recipes.super3.milestones.m2_env_health_dashboard.dashboard import (
    build_dashboard_model,
    load_health_report,
    main,
    render_dashboard_markdown,
)


def test_dashboard_panels_cover_status_reward_latency_gaps_and_runtime_signals() -> None:
    report = {
        "schema_version": 1,
        "generated_at_utc": "2026-05-21T00:00:00+00:00",
        "input_dir": "recorded/m0",
        "environment_registry": "environment_registry.yaml",
        "code_execution": False,
        "rollout_policy": "oracle",
        "status": "fail",
        "health": {
            "environments": {
                "math_reasoning_numeric": {
                    "status": "pass",
                    "splits": {
                        "train": {
                            "rows": 2,
                            "min_rows": 1,
                            "spec_min_rows": 25,
                            "row_count_ok": True,
                            "missing_required_fields": {},
                            "status": "pass",
                        }
                    },
                },
                "browser_qa": {
                    "status": "fail",
                    "splits": {
                        "train": {
                            "rows": 0,
                            "min_rows": 1,
                            "spec_min_rows": 25,
                            "row_count_ok": False,
                            "missing_required_fields": {},
                            "status": "fail",
                        }
                    },
                },
            },
            "unknown_environments": [],
        },
        "baselines": {
            "best_k": 2,
            "policies": ["oracle"],
            "environments": {
                "math_reasoning_numeric": {
                    "splits": {},
                    "aggregate": {
                        "oracle": {
                            "policy": "oracle",
                            "rows": 2,
                            "scored_rows": 2,
                            "skipped_rows": 0,
                            "pass_at_1": 1.0,
                            "best_at_2": 1.0,
                            "mean_score_at_1": 1.0,
                            "mean_best_score_at_2": 1.0,
                            "failure_count": 0,
                            "failures": [],
                            "declared_telemetry": [
                                "reward",
                                "latency_ms",
                                "runtime_deferred",
                                "cluster_runtime_ms",
                            ],
                            "telemetry": {
                                "latency_ms": {
                                    "kind": "numeric",
                                    "min": 1200.0,
                                    "mean": 1500.0,
                                    "max": 1800.0,
                                    "rows": 2,
                                },
                                "normalized_answer": {
                                    "kind": "other",
                                    "distinct_count": 2,
                                    "rows": 2,
                                },
                                "runtime_deferred": {
                                    "kind": "bool",
                                    "true_count": 1,
                                    "false_count": 1,
                                    "rows": 2,
                                },
                            },
                            "telemetry_gap": ["cluster_runtime_ms"],
                        }
                    },
                },
                "browser_qa": {
                    "splits": {},
                    "aggregate": {
                        "oracle": {
                            "policy": "oracle",
                            "rows": 1,
                            "scored_rows": 0,
                            "skipped_rows": 1,
                            "pass_at_1": 0.0,
                            "best_at_2": 0.0,
                            "mean_score_at_1": 0.0,
                            "mean_best_score_at_2": 0.0,
                            "failure_count": 0,
                            "failures": [],
                            "declared_telemetry": ["reward"],
                            "telemetry": {},
                            "telemetry_gap": [],
                        }
                    },
                },
            },
        },
    }

    model = build_dashboard_model(report, slow_latency_ms=1000.0)
    panels = model["panels"]

    assert model["summary"]["source_status"] == "fail"
    assert model["summary"]["failing_environments"] == ["browser_qa"]
    assert model["summary"]["telemetry_gap_count"] == 1
    assert any(row["health_status"] == "pass" for row in panels["environment_status"])

    math_reward = next(
        row
        for row in panels["reward_quality"]
        if row["environment"] == "math_reasoning_numeric"
    )
    assert math_reward["reward_status"] == "pass"

    browser_reward = next(row for row in panels["reward_quality"] if row["environment"] == "browser_qa")
    assert browser_reward["reward_status"] == "fail"
    assert browser_reward["status_reason"] == "no scored rows"

    assert panels["latency"] == [
        {
            "environment": "math_reasoning_numeric",
            "policy": "oracle",
            "key": "latency_ms",
            "status": "slow",
            "threshold_ms": 1000.0,
            "min_ms": 1200.0,
            "mean_ms": 1500.0,
            "max_ms": 1800.0,
            "rows": 2,
        }
    ]
    assert {
        "environment": "math_reasoning_numeric",
        "policy": "oracle",
        "missing_key": "cluster_runtime_ms",
    } in panels["telemetry_gaps"]
    assert any(row["signal"] == "runtime_deferred" for row in panels["deferred_runtime_signals"])
    assert any(row["signal"] == "skipped_rows" for row in panels["deferred_runtime_signals"])


def test_dashboard_consumes_representative_health_baseline_helpers_shape() -> None:
    rows_by_env = {
        "math_reasoning_numeric": {
            "train": [
                {
                    "environment": "math_reasoning_numeric",
                    "milestone": "M0",
                    "use_stage": ["M0 data_env_foundation"],
                    "question": "1+1?",
                    "expected_answer": "2",
                    "responses_create_params": {"input": [{"role": "user", "content": "1+1?"}]},
                    "reward_config": {"verifier": "normalized_numeric_exact_match"},
                    "metadata": {
                        "source_dataset": "synthetic",
                        "license": "mit",
                        "data_stage": "M0",
                    },
                }
            ]
        }
    }
    env_specs = {
        "math_reasoning_numeric": {
            "health_check": {
                "min_rows_per_split": 1,
                "required_fields": [
                    "question",
                    "expected_answer",
                    "responses_create_params.input",
                ],
            },
            "telemetry": [
                "reward",
                "latency_ms",
                "normalized_answer",
                "malformed_final_answer",
                "simulator_runtime_ms",
            ],
        }
    }
    report = {
        "schema_version": 1,
        "generated_at_utc": "2026-05-21T00:00:00+00:00",
        "input_dir": "synthetic",
        "environment_registry": "synthetic-registry",
        "code_execution": False,
        "rollout_policy": "oracle",
        "requested_rows": {},
        "health": summarize_health(rows_by_env, env_specs),
        "baselines": summarize_baselines(
            rows_by_env,
            policies=["oracle"],
            best_k=2,
            run_code=False,
            env_specs=env_specs,
        ),
        "status": "pass",
    }

    model = build_dashboard_model(report)

    assert model["summary"]["environment_count"] == 1
    assert model["panels"]["environment_status"][0]["rows"] == 1
    assert model["panels"]["reward_quality"][0]["pass_at_1"] == 1.0
    telemetry_keys = {row["key"] for row in model["panels"]["telemetry_keys"]}
    assert {"latency_ms", "normalized_answer", "malformed_final_answer"}.issubset(telemetry_keys)
    assert model["panels"]["telemetry_gaps"] == [
        {
            "environment": "math_reasoning_numeric",
            "policy": "oracle",
            "missing_key": "simulator_runtime_ms",
        }
    ]


def test_dashboard_cli_writes_json_and_markdown_from_recorded_report(tmp_path: Path) -> None:
    input_dir = tmp_path / "m0_assets"
    train_dir = input_dir / "math_reasoning_numeric"
    train_dir.mkdir(parents=True)
    record = {
        "environment": "math_reasoning_numeric",
        "milestone": "M0",
        "use_stage": ["M0 data_env_foundation"],
        "question": "1+1?",
        "expected_answer": "2",
        "responses_create_params": {"input": [{"role": "user", "content": "1+1?"}]},
        "reward_config": {"verifier": "normalized_numeric_exact_match"},
        "metadata": {"source_dataset": "synthetic", "license": "mit", "data_stage": "M0"},
    }
    (train_dir / "train-split.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

    env_registry = tmp_path / "environment_registry.yaml"
    env_registry.write_text(
        "\n".join(
            [
                "environments:",
                "  - id: math_reasoning_numeric",
                "    telemetry:",
                "      - reward",
                "      - latency_ms",
                "      - normalized_answer",
                "      - malformed_final_answer",
                "    health_check:",
                "      min_rows_per_split: 1",
                "      required_fields:",
                "        - question",
                "        - expected_answer",
                "        - responses_create_params.input",
                "",
            ]
        ),
        encoding="utf-8",
    )
    args = Namespace(
        input_dir=input_dir,
        environment_registry=env_registry,
        policy=["oracle"],
        best_k=2,
        skip_code_execution=True,
        container_runtime=None,
        rollout_policy="oracle",
    )
    health_report = build_report(args)
    report_path = tmp_path / "health_baseline_report.json"
    report_path.write_text(json.dumps(health_report), encoding="utf-8")

    output_json = tmp_path / "dashboard.json"
    output_md = tmp_path / "dashboard.md"

    assert main(
        [
            "--input-report",
            str(report_path),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_md),
        ]
    ) == 0

    model = load_health_report(output_json)
    markdown = output_md.read_text(encoding="utf-8")
    rendered = render_dashboard_markdown(model)

    assert model["kind"] == "env_health_dashboard"
    assert model["summary"]["environment_count"] == 1
    assert "Environment Health Dashboard" in markdown
    assert rendered == markdown
