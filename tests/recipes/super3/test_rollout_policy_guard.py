"""Tests for the task021 Session 6 rollout-policy guard rail.

Verifies the policy → recommended-runtime mapping, the guard rail
that prevents adversarial candidates from running in-process, and
that the kwarg threads cleanly through ``score_record`` /
``score_rows`` / CLI.

The guard is a forward-looking safety net: no in-repo caller passes
``rollout_policy="adversarial"`` today, but any future M1+ rollout
that forgets ``container_runtime`` will hit the RuntimeError instead
of silently running untrusted code on the host.
"""

from __future__ import annotations

import sys
import types
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim import (  # noqa: E402
    KNOWN_ROLLOUT_POLICIES,
    ROLLOUT_POLICY_ADVERSARIAL,
    ROLLOUT_POLICY_ORACLE,
    recommended_container_runtime,
)


# ---------- Policy constants + recommended runtime ----------


def test_known_rollout_policies_carry_oracle_and_adversarial() -> None:
    assert KNOWN_ROLLOUT_POLICIES == frozenset({"oracle", "adversarial"})


def test_oracle_constant_is_string_oracle() -> None:
    assert ROLLOUT_POLICY_ORACLE == "oracle"
    assert ROLLOUT_POLICY_ADVERSARIAL == "adversarial"


def test_recommended_runtime_oracle_is_none() -> None:
    """Oracle candidates trusted — no isolation needed."""
    assert recommended_container_runtime("oracle") is None


def test_recommended_runtime_adversarial_is_docker() -> None:
    """Adversarial candidates default to docker; operators can override
    to podman / singularity via the CLI flag."""
    assert recommended_container_runtime("adversarial") == "docker"


def test_recommended_runtime_rejects_unknown_policy() -> None:
    with pytest.raises(ValueError, match="unknown rollout policy"):
        recommended_container_runtime("bogus")


# ---------- The guard rail in run_python_unit_tests ----------


def _mbpp_record(env: str = "code_execution_python") -> dict[str, Any]:
    return {
        "environment": env,
        "expected_answer": "def add(a, b): return a + b",
        "reward_config": {"verifier": "python_unit_tests", "timeout_s": 5},
        "extra_env_info": {
            "test_list": ["assert add(1, 2) == 3"],
            "test_imports": [],
        },
    }


def test_adversarial_with_no_container_runtime_raises_runtime_error() -> None:
    """The whole point of Session 6 — adversarial + container_runtime=None
    must NOT silently run untrusted code on the host."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    with pytest.raises(RuntimeError, match="adversarial rollout policy requires"):
        run_m0_health_baseline.run_python_unit_tests(
            _mbpp_record()["expected_answer"],
            _mbpp_record(),
            timeout_s=5,
            container_runtime=None,
            rollout_policy="adversarial",
        )


def test_adversarial_with_container_runtime_does_not_raise(monkeypatch) -> None:
    """Adversarial + container_runtime=docker is the supported safe path;
    the function should proceed normally."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    def fake_run(argv, **kwargs):
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim.subprocess.run",
        fake_run,
    )

    score, diag = run_m0_health_baseline.run_python_unit_tests(
        _mbpp_record()["expected_answer"],
        _mbpp_record(),
        timeout_s=5,
        container_runtime="docker",
        rollout_policy="adversarial",
    )
    assert score == 1.0
    # rollout_policy lands in diagnostics for audit, only when != oracle.
    assert diag["rollout_policy"] == "adversarial"


def test_oracle_default_keeps_in_process_path_unchanged(monkeypatch) -> None:
    """The Session 5 default (in-process via sys.executable -I) must
    stay the active path when neither rollout_policy nor container_runtime
    is set — pre-Session-6 behavior identical."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = list(argv)
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(run_m0_health_baseline.subprocess, "run", fake_run)

    score, diag = run_m0_health_baseline.run_python_unit_tests(
        _mbpp_record()["expected_answer"],
        _mbpp_record(),
        timeout_s=5,
        # rollout_policy defaults to "oracle"
        # container_runtime defaults to None
    )
    assert score == 1.0
    assert captured["argv"][0] == sys.executable
    assert "-I" in captured["argv"]
    # When rollout_policy=oracle (default), don't pollute diagnostics
    # with a redundant field. Pre-task021-Session-6 callers see the
    # exact same diagnostics dict shape.
    assert "rollout_policy" not in diag


def test_rejects_unknown_rollout_policy_value() -> None:
    """Typo in `rollout_policy` value must raise at the verifier
    entry point — typos shouldn't silently downgrade to oracle."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    with pytest.raises(ValueError, match="unknown rollout_policy"):
        run_m0_health_baseline.run_python_unit_tests(
            _mbpp_record()["expected_answer"],
            _mbpp_record(),
            timeout_s=5,
            rollout_policy="adversairal",  # typo
        )


# ---------- Plumbing: score_record / score_rows ----------


def test_score_record_threads_rollout_policy_into_runner(monkeypatch) -> None:
    """The guard rail only works if score_record forwards the kwarg —
    catch the threading mistake at score_record's level."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: dict[str, Any] = {}

    def fake_runner(candidate, record, timeout_s, *, container_runtime=None, rollout_policy="oracle"):
        captured["rollout_policy"] = rollout_policy
        captured["container_runtime"] = container_runtime
        return 1.0, {"returncode": 0}

    monkeypatch.setattr(run_m0_health_baseline, "run_python_unit_tests", fake_runner)

    run_m0_health_baseline.score_record(
        "def add(a, b): return a + b",
        _mbpp_record(),
        run_code=True,
        container_runtime="podman",
        rollout_policy="adversarial",
    )
    assert captured["rollout_policy"] == "adversarial"
    assert captured["container_runtime"] == "podman"


def test_score_rows_threads_rollout_policy(monkeypatch) -> None:
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: list[str] = []

    def fake_score_record(candidate, record, *, run_code, container_runtime, rollout_policy):
        captured.append(rollout_policy)
        return 1.0, {"returncode": 0}

    monkeypatch.setattr(run_m0_health_baseline, "score_record", fake_score_record)

    run_m0_health_baseline.score_rows(
        [_mbpp_record()],
        policy="oracle",
        best_k=1,
        run_code=True,
        container_runtime="docker",
        rollout_policy="adversarial",
    )
    assert captured == ["adversarial"]
