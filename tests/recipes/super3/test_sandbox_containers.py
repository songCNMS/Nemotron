"""Tests for the M1 sandbox container registry (task021 Session 3).

Three surfaces:

1. ``sandbox_image_registry.yaml`` — declarative table of three
   container images (code_exec / lean / terminal) with per-env
   routing.
2. ``image_resolver.py`` — Python helpers (loader + resolver +
   validate-on-disk).
3. ``build_sandbox_containers.sh`` — file-content lint only (bash
   syntax is checked at the command-line via ``bash -n`` during
   review; this file just confirms the script exists, is executable,
   and reads from the right registry path).

Actually building / running the images is task021 Session 4 territory
(needs Docker / Podman / Singularity at run time).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.sandbox_containers.image_resolver import (  # noqa: E402
    REGISTRY_PATH,
    envs_covered_by_registry,
    image_tag,
    load_sandbox_image_registry,
    resolve_dockerfile_path,
    resolve_image_for_env,
    validate_dockerfile_exists,
)


# ---------- Registry shape ----------


def test_registry_loads_four_declared_images() -> None:
    rows = load_sandbox_image_registry()
    image_ids = {row["image_id"] for row in rows}
    assert image_ids == {"code_exec", "lean", "terminal", "sql_sqlite"}


def test_registry_path_lives_in_sandbox_containers_dir() -> None:
    assert REGISTRY_PATH.is_file()
    assert REGISTRY_PATH.parent.name == "sandbox_containers"


def test_registry_rejects_duplicate_image_id(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M1
images:
  - image_id: dup
    version_tag: v0.1
    dockerfile_path: a.Dockerfile
    target_envs: [env_a]
  - image_id: dup
    version_tag: v0.1
    dockerfile_path: b.Dockerfile
    target_envs: [env_b]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate image_id"):
        load_sandbox_image_registry(bad)


def test_registry_rejects_missing_required_fields(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M1
images:
  - image_id: stub
    version_tag: v0.1
    # missing dockerfile_path + target_envs
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required field"):
        load_sandbox_image_registry(bad)


def test_registry_rejects_empty_target_envs(tmp_path: Path) -> None:
    bad = tmp_path / "registry.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M1
images:
  - image_id: stub
    version_tag: v0.1
    dockerfile_path: a.Dockerfile
    target_envs: []
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="target_envs must be a non-empty list"):
        load_sandbox_image_registry(bad)


# ---------- Dockerfile resolution + on-disk check ----------


def test_every_dockerfile_exists_on_disk() -> None:
    """Every registered image must have its Dockerfile present —
    catches typos in `dockerfile_path` before a build attempt fails."""
    for row in load_sandbox_image_registry():
        path = resolve_dockerfile_path(row)
        assert path.is_file(), f"{row['image_id']}: missing Dockerfile at {path}"
        assert validate_dockerfile_exists(row)


def test_image_tag_is_image_id_colon_version() -> None:
    rows = load_sandbox_image_registry()
    by_id = {row["image_id"]: row for row in rows}
    assert image_tag(by_id["code_exec"]) == "code_exec:v0.1.0"
    assert image_tag(by_id["lean"]) == "lean:v0.1.0"
    assert image_tag(by_id["sql_sqlite"]) == "sql_sqlite:v0.1.0"


# ---------- Per-env resolution ----------


def test_resolve_image_for_known_env_returns_correct_tag() -> None:
    assert resolve_image_for_env("code_execution_python") == "code_exec:v0.1.0"
    assert resolve_image_for_env("math_formal_lean") == "lean:v0.1.0"
    assert resolve_image_for_env("terminal_basic_shell") == "terminal:v0.1.0"
    assert resolve_image_for_env("sql_text_to_query") == "sql_sqlite:v0.1.0"


def test_resolve_image_for_unsandboxed_env_returns_none() -> None:
    """Envs that don't need a sandbox (e.g., search_grounded_qa runs no
    untrusted code; M1 verifier just substring-matches) return None.
    The future ContainerSandbox shim treats None as 'run in process'."""
    assert resolve_image_for_env("search_grounded_qa") is None
    assert resolve_image_for_env("math_reasoning_numeric") is None


def test_envs_covered_by_registry_matches_target_envs_union() -> None:
    covered = envs_covered_by_registry()
    # The three known-today envs all show up.
    assert "code_execution_python" in covered
    assert "math_formal_lean" in covered
    assert "terminal_basic_shell" in covered
    assert "sql_text_to_query" in covered


# ---------- Dockerfile content lint ----------


_DOCKERFILE_NAMES = (
    "code_exec.Dockerfile",
    "lean.Dockerfile",
    "terminal.Dockerfile",
    "sql_sqlite.Dockerfile",
)


def _dockerfile_path(name: str) -> Path:
    return REGISTRY_PATH.parent / name


@pytest.mark.parametrize("name", _DOCKERFILE_NAMES)
def test_dockerfile_starts_with_from_directive(name: str) -> None:
    body = _dockerfile_path(name).read_text(encoding="utf-8")
    # Skip leading comments + blank lines; first non-comment instruction
    # must be a FROM.
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        assert stripped.startswith("FROM "), f"{name}: first non-comment line is {stripped!r}"
        break
    else:
        pytest.fail(f"{name}: no non-comment lines")


@pytest.mark.parametrize("name", _DOCKERFILE_NAMES)
def test_dockerfile_drops_to_non_root_user(name: str) -> None:
    """Every sandbox image must drop privileges via ``USER <non-root>``.
    Catches the obvious mistake of forgetting the USER directive entirely
    or shipping with ``USER root``."""
    body = _dockerfile_path(name).read_text(encoding="utf-8")
    user_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip().startswith("USER ")
    ]
    assert user_lines, f"{name}: no USER directive — image would run as root"
    # The last USER directive wins. Must not be root / UID 0.
    final = user_lines[-1].removeprefix("USER ").strip()
    assert final not in ("root", "0"), f"{name}: final USER directive is {final!r}"


@pytest.mark.parametrize("name", _DOCKERFILE_NAMES)
def test_dockerfile_no_unbounded_latest_or_master(name: str) -> None:
    """Catch obvious version-drift hazards: ``FROM something:latest`` or
    ``branch=master`` URLs in RUN commands. (Pinned tagged URLs are fine
    — the Lean Dockerfile uses ``/v3.1.1/`` for elan, which is a
    versioned ref.)"""
    body = _dockerfile_path(name).read_text(encoding="utf-8")
    assert ":latest" not in body, f"{name}: ':latest' tag found — pin a version"
    # Allow `master`/`main` as words inside comments + paths like
    # `coreai_dlalgo_*`, only flag explicit branch refs in URLs.
    drift_pattern = re.compile(
        r"https?://[^ \t\n]*?[?&]ref=(master|main)\b"
        r"|github\.com/[^/]+/[^/]+/(blob|tree|raw)/(master|main)/",
        re.IGNORECASE,
    )
    assert not drift_pattern.search(body), (
        f"{name}: unpinned branch reference found in URL"
    )


# ---------- build_sandbox_containers.sh shape ----------


def test_build_script_is_executable() -> None:
    script = REGISTRY_PATH.parent / "build_sandbox_containers.sh"
    assert script.is_file()
    assert os.access(script, os.X_OK), "build_sandbox_containers.sh is not executable"


def test_build_script_starts_with_correct_shebang() -> None:
    script = REGISTRY_PATH.parent / "build_sandbox_containers.sh"
    first_line = script.read_text(encoding="utf-8").splitlines()[0]
    assert first_line == "#!/usr/bin/env bash"


def test_build_script_references_sandbox_image_registry_yaml() -> None:
    """File-content lint: the build script should point at the registry
    YAML by its expected basename so renaming one without the other
    surfaces here."""
    script = REGISTRY_PATH.parent / "build_sandbox_containers.sh"
    body = script.read_text(encoding="utf-8")
    assert "sandbox_image_registry.yaml" in body


# ---------- Cross-registry: unified index awareness ----------


def test_unified_index_includes_sandbox_image_registry() -> None:
    """task030 Session 1 unified index must catalog the new sandbox
    image registry. Adding a new registry kind to the pipeline is a
    one-row addition in unified_index.yaml + one schema entry."""
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        load_unified_index,
    )

    rows = load_unified_index()
    sandbox_rows = [r for r in rows if r["kind"] == "sandbox_image_registry"]
    assert sandbox_rows, "unified_index.yaml missing sandbox_image_registry entry"
    assert sandbox_rows[0]["id"] == "m1_sandbox_images"


def test_unified_index_validates_clean_after_sandbox_registry_addition() -> None:
    """Live validation must remain clean — schema layer covers the
    new kind."""
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        validate_unified_index,
    )

    issues = validate_unified_index()
    assert issues == [], (
        "live unified index has schema drift after sandbox_image_registry addition:\n"
        + "\n".join(issues)
    )


def test_known_kinds_includes_sandbox_image_registry() -> None:
    from nemotron.recipes.super3.milestones.data_registries.schema import KNOWN_KINDS

    assert "sandbox_image_registry" in KNOWN_KINDS
