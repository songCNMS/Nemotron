"""Tests for the schema-enforcement CLI (task030 Session 2).

The script wraps ``validate_unified_index()`` so that pre-commit hooks
and CI workflows can catch registry shape drift at commit time. These
tests run the script as a subprocess to cover the actual CLI surface
(exit codes, --quiet, --paths-only) plus a unit test on the in-process
``main()`` entry point for fast feedback.

Real subprocess invocation is needed for the pre-commit hook path —
the hook entry is ``bash -c 'python3 scripts/validate_data_registries.py
--quiet'`` and silent-on-clean / verbose-on-failure behavior is part
of the contract.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_data_registries.py"


def _run_script(*extra_args: str, env_override: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run validate_data_registries.py as a subprocess and capture I/O.

    We pass ``PYTHONPATH=src`` explicitly so the script can find the
    ``nemotron`` package without the parent venv needing an editable
    install — matches the pre-commit hook invocation.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if env_override:
        env.update(env_override)
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


# ---------- Script file shape ----------


def test_script_exists_and_is_executable() -> None:
    assert SCRIPT_PATH.is_file()
    assert os.access(SCRIPT_PATH, os.X_OK)


def test_script_starts_with_python_shebang() -> None:
    first_line = SCRIPT_PATH.read_text(encoding="utf-8").splitlines()[0]
    assert first_line == "#!/usr/bin/env python3"


# ---------- Clean-main behavior ----------


def test_clean_main_exits_zero_with_success_line() -> None:
    """Live unified index validates clean → exit 0, single status line on stdout."""
    result = _run_script()
    assert result.returncode == 0, result.stderr or result.stdout
    assert "all registries clean" in result.stdout
    assert result.stderr == ""


def test_clean_main_with_quiet_emits_no_stdout() -> None:
    """--quiet is for pre-commit consumption — silent on clean so the
    hook doesn't spam the commit log."""
    result = _run_script("--quiet")
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


# ---------- Broken-index behavior ----------


def _write_broken_index(tmp_path: Path) -> Path:
    """Build a tiny broken unified index next to a valid registry that
    declares a missing required field."""
    registry = tmp_path / "broken_registry.yaml"
    registry.write_text(
        # bridge_env_registry rows must carry status; this one doesn't.
        """schema_version: 1
milestone: M1
envs:
  - nemo_gym_env: stub
    mix: rlhf
    # status missing on purpose
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: broken_test_registry
    kind: bridge_env_registry
    path: {registry.name}
    summary: test fixture
""",
        encoding="utf-8",
    )
    return index


def test_broken_index_exits_one_with_issues_on_stderr(tmp_path: Path) -> None:
    index = _write_broken_index(tmp_path)
    result = _run_script("--index-path", str(index))
    assert result.returncode == 1
    # Issue count + per-issue bullet land on stderr (machine-friendly
    # log format).
    assert "issue(s) across the unified index" in result.stderr
    assert "broken_test_registry" in result.stderr
    assert "missing required field 'status'" in result.stderr


def test_paths_flag_lists_only_offending_registry_ids(tmp_path: Path) -> None:
    """--paths returns one registry-id per line on stdout — easy to
    pipe into other tools (``xargs git restore``, jq, etc.)."""
    index = _write_broken_index(tmp_path)
    result = _run_script("--paths", "--index-path", str(index))
    assert result.returncode == 1
    # Exactly one offending registry in the synthetic fixture.
    assert result.stdout.strip() == "broken_test_registry"
    # No verbose issue dump when --paths is set.
    assert "issue(s) across" not in result.stderr


def test_missing_index_exits_two(tmp_path: Path) -> None:
    """Validator setup failures (missing file etc.) exit code 2, not 1.
    Distinguishes 'CI infrastructure broken' from 'schema drift found'."""
    missing = tmp_path / "does_not_exist.yaml"
    result = _run_script("--index-path", str(missing))
    assert result.returncode == 2
    assert "validator raised" in result.stderr or "cannot import" in result.stderr


# ---------- In-process main() for fast unit feedback ----------


def test_main_returns_zero_on_clean_main() -> None:
    """Importable ``main()`` mirrors the subprocess path — useful for
    other Python callers (e.g., a custom CI runner)."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import validate_data_registries  # type: ignore
    finally:
        sys.path.pop(0)
    assert validate_data_registries.main(["--quiet"]) == 0


def test_main_returns_one_on_broken_index(tmp_path: Path) -> None:
    index = _write_broken_index(tmp_path)
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import validate_data_registries  # type: ignore
    finally:
        sys.path.pop(0)
    assert validate_data_registries.main(["--quiet", "--index-path", str(index)]) == 1


# ---------- Pre-commit hook config ----------


def test_precommit_config_declares_validate_data_registries_hook() -> None:
    """The pre-commit local hook must reference the script and trigger
    on registry yaml / loader / schema changes."""
    cfg_path = REPO_ROOT / ".pre-commit-config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    local_repos = [r for r in cfg["repos"] if r.get("repo") == "local"]
    assert local_repos, "expected at least one local repo block"
    hook_ids = {
        hook["id"]
        for repo in local_repos
        for hook in repo.get("hooks", [])
    }
    assert "validate-data-registries" in hook_ids, f"got {hook_ids}"


def test_precommit_hook_runs_the_script_under_pythonpath_src() -> None:
    """The entry must invoke the actual script (path-based, not just
    by name) and set PYTHONPATH=src so the import works pre-install."""
    cfg_path = REPO_ROOT / ".pre-commit-config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    hook = next(
        h
        for r in cfg["repos"]
        if r.get("repo") == "local"
        for h in r.get("hooks", [])
        if h["id"] == "validate-data-registries"
    )
    entry = hook["entry"]
    assert "scripts/validate_data_registries.py" in entry
    assert "PYTHONPATH=src" in entry
    assert "--quiet" in entry
