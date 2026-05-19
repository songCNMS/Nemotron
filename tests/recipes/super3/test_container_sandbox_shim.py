"""Tests for the ContainerSandbox runtime shim (task021 Session 5).

Three surfaces:

1. ``ContainerSandbox.build_argv`` — pure function, asserts the
   resolved argv shape for docker / podman / singularity flag dialects.
2. ``sandbox_for_env`` — pulls the registered image for an env via
   ``image_resolver`` and constructs a ContainerSandbox with defaults.
3. ``run_python_unit_tests`` integration — with ``container_runtime``
   set, the verifier wires through the shim; with ``container_runtime=None``
   it keeps the legacy in-process path (regression gate for the
   default case).

Subprocess invocations are monkeypatched throughout; running actual
docker / podman / singularity is task021 Session 4 cluster verify
territory.
"""

from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim import (  # noqa: E402
    KNOWN_CONTAINER_RUNTIMES,
    ContainerSandbox,
    sandbox_for_env,
)


# ---------- ContainerSandbox.build_argv ----------


def test_known_container_runtimes_are_docker_podman_singularity() -> None:
    assert KNOWN_CONTAINER_RUNTIMES == frozenset({"docker", "podman", "singularity"})


def test_constructor_rejects_unknown_runtime() -> None:
    with pytest.raises(ValueError, match="unknown container runtime"):
        ContainerSandbox(image="code_exec:v0.1.0", runtime="bogus")


def test_docker_argv_has_isolation_flags(tmp_path: Path) -> None:
    """Docker / podman argv must include --rm + --network=none +
    --mount bind + --workdir + --read-only + --tmpfs by default."""
    sandbox = ContainerSandbox(
        image="code_exec:v0.1.0",
        runtime="docker",
        cpu_limit="1",
        memory_limit="512m",
    )
    argv = sandbox.build_argv(
        host_workdir=tmp_path,
        command=["python", "-I", "/workspace/script.py"],
    )

    # Walk argv collecting flags to assert on the set.
    assert argv[0] == "docker"
    assert argv[1] == "run"
    assert "--rm" in argv
    assert "--network=none" in argv
    assert "--read-only" in argv
    assert "--cpus" in argv and argv[argv.index("--cpus") + 1] == "1"
    assert "--memory" in argv and argv[argv.index("--memory") + 1] == "512m"
    # mount + workdir share /workspace
    assert "--workdir" in argv
    assert argv[argv.index("--workdir") + 1] == "/workspace"
    mount_index = argv.index("--mount")
    mount_spec = argv[mount_index + 1]
    assert "type=bind" in mount_spec
    assert "target=/workspace" in mount_spec
    assert "readonly" in mount_spec
    # Tail must end with image + command (in that order).
    assert argv[-4:] == [
        "code_exec:v0.1.0",
        "python",
        "-I",
        "/workspace/script.py",
    ]


def test_podman_uses_same_flag_dialect_as_docker(tmp_path: Path) -> None:
    """Podman is a docker-compat CLI; the shim swaps the runtime
    binary but otherwise emits identical flags."""
    docker = ContainerSandbox(image="code_exec:v0.1.0", runtime="docker")
    podman = ContainerSandbox(image="code_exec:v0.1.0", runtime="podman")
    cmd = ["python", "-c", "print(0)"]
    docker_argv = docker.build_argv(host_workdir=tmp_path, command=cmd)
    podman_argv = podman.build_argv(host_workdir=tmp_path, command=cmd)
    # Identical except for the runtime binary at position 0.
    assert docker_argv[0] == "docker"
    assert podman_argv[0] == "podman"
    assert docker_argv[1:] == podman_argv[1:]


def test_singularity_uses_exec_dialect(tmp_path: Path) -> None:
    """Singularity wants ``exec`` + ``--containall`` + ``--bind`` +
    ``docker://`` URI — different vocabulary, same isolation intent."""
    sandbox = ContainerSandbox(
        image="code_exec:v0.1.0",
        runtime="singularity",
    )
    argv = sandbox.build_argv(
        host_workdir=tmp_path,
        command=["python", "-I", "/workspace/script.py"],
    )
    assert argv[0] == "singularity"
    assert argv[1] == "exec"
    assert "--containall" in argv
    assert "--no-net" in argv  # network="none" default → no-net
    assert "--bind" in argv
    bind_spec = argv[argv.index("--bind") + 1]
    assert bind_spec.endswith(":/workspace:ro")
    # docker:// URI passed to singularity for pulling from local cache
    image_arg = next(arg for arg in argv if arg.startswith("docker://"))
    assert image_arg == "docker://code_exec:v0.1.0"
    # Command at tail.
    assert argv[-3:] == ["python", "-I", "/workspace/script.py"]


def test_no_read_only_flag_when_disabled(tmp_path: Path) -> None:
    sandbox = ContainerSandbox(
        image="x:v1",
        runtime="docker",
        read_only=False,
    )
    argv = sandbox.build_argv(host_workdir=tmp_path, command=["true"])
    assert "--read-only" not in argv


def test_tmpfs_list_emits_one_flag_per_path(tmp_path: Path) -> None:
    sandbox = ContainerSandbox(
        image="x:v1",
        runtime="docker",
        tmpfs=("/tmp", "/var/tmp"),
    )
    argv = sandbox.build_argv(host_workdir=tmp_path, command=["true"])
    tmpfs_pairs = [
        argv[i + 1]
        for i, token in enumerate(argv)
        if token == "--tmpfs"
    ]
    assert tmpfs_pairs == ["/tmp", "/var/tmp"]


# ---------- sandbox_for_env (resolver glue) ----------


def test_sandbox_for_env_returns_configured_sandbox_for_known_env() -> None:
    sandbox = sandbox_for_env("code_execution_python")
    assert sandbox is not None
    assert sandbox.image == "code_exec:v0.1.0"
    assert sandbox.runtime == "docker"


def test_sandbox_for_env_returns_none_for_unsandboxed_env() -> None:
    """Envs not in the registry — e.g., search_grounded_qa — return
    None. The verifier-side wiring treats that as "fall back to
    in-process and flag the gap in diagnostics"."""
    assert sandbox_for_env("search_grounded_qa") is None


def test_sandbox_for_env_honors_runtime_kwarg() -> None:
    sandbox = sandbox_for_env("math_formal_lean", runtime="podman")
    assert sandbox is not None
    assert sandbox.runtime == "podman"
    assert sandbox.image == "lean:v0.1.0"


# ---------- run_python_unit_tests integration ----------


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


def test_run_python_unit_tests_default_path_is_in_process() -> None:
    """``container_runtime=None`` (the default) must keep the legacy
    in-process ``sys.executable -I`` invocation — task021 Session 5
    is opt-in, no behavior change for existing callers."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = list(argv)
        captured["kwargs"] = kwargs
        return types.SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    orig = run_m0_health_baseline.subprocess.run
    run_m0_health_baseline.subprocess.run = fake_run
    try:
        score, diag = run_m0_health_baseline.run_python_unit_tests(
            _mbpp_record()["expected_answer"],
            _mbpp_record(),
            timeout_s=5,
            # container_runtime defaults to None
        )
    finally:
        run_m0_health_baseline.subprocess.run = orig

    assert score == 1.0
    # Legacy in-process invocation uses sys.executable + "-I" flag.
    assert captured["argv"][0] == sys.executable
    assert "-I" in captured["argv"]
    # Diagnostics must NOT carry container_runtime when not requested.
    assert "container_runtime" not in diag
    assert "container_fallback" not in diag


def test_run_python_unit_tests_container_path_resolves_argv(monkeypatch) -> None:
    """``container_runtime='docker'`` must route through ContainerSandbox.
    Argv starts with ``docker run …`` and ends with the image tag +
    ``python -I /workspace/<script>``."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = list(argv)
        captured["kwargs"] = kwargs
        return types.SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    # The shim calls subprocess.run from its own module, not from
    # run_m0_health_baseline. Patch both for safety.
    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim.subprocess.run",
        fake_run,
    )
    monkeypatch.setattr(run_m0_health_baseline.subprocess, "run", fake_run)

    score, diag = run_m0_health_baseline.run_python_unit_tests(
        _mbpp_record()["expected_answer"],
        _mbpp_record(),
        timeout_s=5,
        container_runtime="docker",
    )

    assert score == 1.0
    assert captured["argv"][0] == "docker"
    assert captured["argv"][1] == "run"
    assert "--network=none" in captured["argv"]
    assert "code_exec:v0.1.0" in captured["argv"]
    # Script path inside the container must be under /workspace.
    assert any(arg.startswith("/workspace/") and arg.endswith(".py") for arg in captured["argv"])
    # Diagnostics surface the container runtime + the no-fallback flag.
    assert diag["container_runtime"] == "docker"
    assert diag["container_fallback"] is False


def test_run_python_unit_tests_container_fallback_when_env_unmapped(monkeypatch) -> None:
    """Envs without a registered sandbox image fall back to in-process
    execution and surface ``container_fallback=True`` in diagnostics so
    coverage walks see the gap. Catches the realistic "task057 adds an
    env but forgets to register its sandbox image" case."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: dict[str, Any] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = list(argv)
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(run_m0_health_baseline.subprocess, "run", fake_run)

    record = _mbpp_record(env="not_a_registered_sandbox_env")
    score, diag = run_m0_health_baseline.run_python_unit_tests(
        record["expected_answer"],
        record,
        timeout_s=5,
        container_runtime="docker",
    )

    assert score == 1.0
    # Argv reverts to sys.executable path.
    assert captured["argv"][0] == sys.executable
    assert diag["container_runtime"] == "docker"
    assert diag["container_fallback"] is True


def test_run_python_unit_tests_container_timeout_surfaces_runtime(monkeypatch) -> None:
    """When the container hangs and subprocess.run raises
    TimeoutExpired, diagnostics still carry the container_runtime hint
    so operators know which path timed out."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    def fake_run(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, timeout=kwargs.get("timeout", 1))

    monkeypatch.setattr(
        "nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim.subprocess.run",
        fake_run,
    )

    record = _mbpp_record()
    score, diag = run_m0_health_baseline.run_python_unit_tests(
        record["expected_answer"],
        record,
        timeout_s=1,
        container_runtime="docker",
    )
    assert score == 0.0
    assert diag["error"] == "timeout"
    assert diag["container_runtime"] == "docker"


# ---------- score_record + score_rows plumbing ----------


def test_score_record_plumbs_container_runtime_into_run_python_unit_tests(monkeypatch) -> None:
    """score_record must thread container_runtime through to
    run_python_unit_tests so the CLI flag actually takes effect end-to-end."""
    from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline

    captured: dict[str, Any] = {}

    def fake_runner(candidate, record, timeout_s, *, container_runtime=None):
        captured["container_runtime"] = container_runtime
        return 1.0, {"returncode": 0}

    monkeypatch.setattr(run_m0_health_baseline, "run_python_unit_tests", fake_runner)

    run_m0_health_baseline.score_record(
        "def add(a, b): return a + b",
        _mbpp_record(),
        run_code=True,
        container_runtime="podman",
    )
    assert captured["container_runtime"] == "podman"
