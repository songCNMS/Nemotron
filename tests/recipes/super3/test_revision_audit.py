"""Tests for the HuggingFace revision-pin audit (task030 Session 6 /
task058 follow-up).

Coverage:

- ``is_pinned`` predicate (40-char SHAs accepted; floating refs +
  empty + None + non-string rejected)
- ``find_unpinned_revisions`` walks live registries — today: zero
  blockers and zero informational findings (M0 rows and required RLHF
  pref candidates carry revision pins)
- Synthetic broken fixtures (missing field / floating ref) trigger
  blockers + exit 1
- CLI ``--check-revision-pins`` end-to-end behavior + exit codes
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.data_registries.revision_audit import (  # noqa: E402
    FLOATING_REVISION_REFS,
    PLACEHOLDER_REVISION_REFS,
    find_unpinned_revisions,
    format_revision_audit_report,
    is_pinned,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_data_registries.py"


# ---------- is_pinned predicate ----------


@pytest.mark.parametrize(
    "hf_revision",
    [
        "1908d6afbbead072334abe2965f91bd2709910ab",  # HotpotQA's live pin
        "4bb6404fdc6cacfda99d4ac4205087b89d32030c",  # MBPP's live pin
        "abc123",  # short SHA — still pinned (predicate is "not floating")
        "v1.0.0",  # tag-style — pinned, not floating
        "release-2026",
    ],
)
def test_is_pinned_accepts_concrete_references(hf_revision: str) -> None:
    assert is_pinned(hf_revision)


@pytest.mark.parametrize(
    "hf_revision",
    [
        "main",
        "MAIN",
        "Main",
        "master",
        "head",
        "HEAD",
        "latest",
        "TBD",
        "todo",
        "pending",
        "unknown",
        "",
        "   ",
        None,
        42,
    ],
)
def test_is_pinned_rejects_floating_refs_and_invalid_inputs(hf_revision) -> None:
    assert not is_pinned(hf_revision)


def test_floating_refs_table_covers_known_unsafe_refs() -> None:
    """Sanity check the registry — adding a new floating ref family
    should require an explicit code change plus a test update."""
    assert "main" in FLOATING_REVISION_REFS
    assert "master" in FLOATING_REVISION_REFS
    assert "head" in FLOATING_REVISION_REFS
    assert "latest" in FLOATING_REVISION_REFS
    assert "" in FLOATING_REVISION_REFS
    assert "tbd" in PLACEHOLDER_REVISION_REFS


# ---------- find_unpinned_revisions on live registries ----------


def test_find_unpinned_revisions_live_has_zero_blockers() -> None:
    """The live m0_data_registry today pins every row to a SHA.
    Adding an unpinned row will trip this test."""
    audit = find_unpinned_revisions()
    assert audit["blockers"] == [], (
        "live m0_data_registry has unpinned rows — pin a hf_revision SHA "
        "before this PR merges:\n" + str(audit["blockers"])
    )


def test_find_unpinned_revisions_live_has_no_pref_informational_findings() -> None:
    """Live RLHF pref candidates requiring revision pins are now pinned."""
    audit = find_unpinned_revisions()
    assert audit["informational"] == []


# ---------- Synthetic broken fixtures ----------


def _write_minimal_index_with_broken_m0(
    tmp_path: Path,
    *,
    hf_revision_value: str | None,
) -> Path:
    """Build a minimal unified index + m0_data_registry where the sole
    row has the specified ``hf_revision`` value (None means omit the
    field entirely)."""
    data_reg = tmp_path / "data_registry.yaml"
    if hf_revision_value is None:
        body = """schema_version: 1
milestone: M0
datasets:
  - id: stub_unpinned
    environment: stub_env
    hf_dataset: stub/dataset
    hf_split: train
    license: cc-by-4.0
    contamination_against: ["nothing"]
    converter: stub
    use_stage: ["M0 data_env_foundation"]
"""
    else:
        body = f"""schema_version: 1
milestone: M0
datasets:
  - id: stub_unpinned
    environment: stub_env
    hf_dataset: stub/dataset
    hf_split: train
    hf_revision: {hf_revision_value}
    license: cc-by-4.0
    contamination_against: ["nothing"]
    converter: stub
    use_stage: ["M0 data_env_foundation"]
"""
    data_reg.write_text(body, encoding="utf-8")
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: stub_m0_data
    kind: m0_data_registry
    path: {data_reg.name}
    summary: stub
""",
        encoding="utf-8",
    )
    return index


def test_missing_hf_revision_field_is_a_blocker(tmp_path: Path) -> None:
    """``hf_revision`` field absent entirely → blocker."""
    index = _write_minimal_index_with_broken_m0(tmp_path, hf_revision_value=None)
    audit = find_unpinned_revisions(index)
    assert len(audit["blockers"]) == 1
    blocker = audit["blockers"][0]
    assert blocker["row_id"] == "stub_unpinned"
    assert blocker["hf_revision"] is None


@pytest.mark.parametrize("floating", ["main", "master", "HEAD", "latest"])
def test_floating_ref_hf_revision_is_a_blocker(tmp_path: Path, floating: str) -> None:
    """``hf_revision: main`` (or other floating refs) → blocker.
    HF resolves these at fetch time so the dataset can drift overnight."""
    index = _write_minimal_index_with_broken_m0(tmp_path, hf_revision_value=floating)
    audit = find_unpinned_revisions(index)
    assert len(audit["blockers"]) == 1
    assert audit["blockers"][0]["hf_revision"] == floating


def test_pref_data_without_pin_required_flag_is_not_flagged(tmp_path: Path) -> None:
    """Pref candidate rows without ``hf_revision_pin_required: true``
    are exploratory; the audit doesn't flag them. Catches a regression
    that would spam the audit with exploration-phase pref rows."""
    pref_reg = tmp_path / "pref_data.yaml"
    pref_reg.write_text(
        """schema_version: 1
milestone: M1
datasets:
  - id: stub_exploration
    hf_dataset: stub/exploration
    license: apache-2.0
    # no hf_revision_pin_required flag, no hf_revision — exploration
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: stub_pref
    kind: pref_data_registry
    path: {pref_reg.name}
    summary: stub
""",
        encoding="utf-8",
    )
    audit = find_unpinned_revisions(index)
    assert audit["blockers"] == []
    assert audit["informational"] == []


def test_pref_data_with_pin_required_but_missing_revision_is_informational(
    tmp_path: Path,
) -> None:
    """Synthetic required pref candidates without pins remain visible as
    informational findings instead of blockers."""
    pref_reg = tmp_path / "pref_data.yaml"
    pref_reg.write_text(
        """schema_version: 1
milestone: M1
datasets:
  - id: stub_required_pref
    hf_dataset: stub/required-pref
    license: apache-2.0
    hf_revision_pin_required: true
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: stub_pref
    kind: pref_data_registry
    path: {pref_reg.name}
    summary: stub
""",
        encoding="utf-8",
    )

    audit = find_unpinned_revisions(index)
    assert audit["blockers"] == []
    assert audit["informational"] == [
        {
            "registry_id": "stub_pref",
            "kind": "pref_data_registry",
            "row_id": "stub_required_pref",
            "hf_dataset": "stub/required-pref",
            "hf_revision": None,
        }
    ]


# ---------- format_revision_audit_report ----------


def test_format_clean_audit_returns_check_marker() -> None:
    text = format_revision_audit_report({"blockers": [], "informational": []})
    assert "all production data registry rows pinned" in text
    assert "✓" in text


def test_format_audit_with_blockers_highlights_them() -> None:
    text = format_revision_audit_report(
        {
            "blockers": [
                {
                    "registry_id": "stub_m0",
                    "kind": "m0_data_registry",
                    "row_id": "stub_unpinned",
                    "hf_dataset": "stub/dataset",
                    "hf_revision": "main",
                }
            ],
            "informational": [],
        }
    )
    assert "BLOCKER" in text
    assert "stub_unpinned" in text
    assert "'main'" in text
    assert "⚠" in text


def test_format_audit_with_only_informational_says_no_blockers() -> None:
    text = format_revision_audit_report(
        {
            "blockers": [],
            "informational": [
                {
                    "registry_id": "m1_rlhf_pref_data",
                    "kind": "pref_data_registry",
                    "row_id": "helpsteer2",
                    "hf_dataset": "nvidia/HelpSteer2",
                    "hf_revision": None,
                }
            ],
        }
    )
    assert "informational" in text
    assert "BLOCKER" not in text
    assert "no blockers" in text


# ---------- CLI ----------


def _run_script(*extra_args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_check_revision_pins_cli_clean_main_exits_zero() -> None:
    """Live main has zero blockers and zero informational findings."""
    result = _run_script("--check-revision-pins")
    assert result.returncode == 0, result.stderr
    assert "all production data registry rows pinned" in result.stdout
    assert "informational" not in result.stdout
    assert "helpsteer2" not in result.stdout
    # No blockers → no "BLOCKER" header in the report.
    assert "BLOCKER" not in result.stdout


def test_check_revision_pins_cli_with_broken_index_exits_one(tmp_path: Path) -> None:
    """A synthetic m0_data_registry row missing hf_revision → exit 1
    and stderr summary names the count."""
    index = _write_minimal_index_with_broken_m0(tmp_path, hf_revision_value=None)
    result = _run_script("--check-revision-pins", "--index-path", str(index))
    assert result.returncode == 1
    assert "BLOCKER" in result.stdout
    assert "stub_unpinned" in result.stdout
    assert "1 unpinned production data row" in result.stderr


def test_check_revision_pins_cli_short_circuits_validation() -> None:
    """When ``--check-revision-pins`` is set, the script must NOT run
    the schema validator pass (avoids redundant work)."""
    result = _run_script("--check-revision-pins")
    assert result.returncode == 0
    # The default validation success line should not be present.
    assert "all registries clean" not in result.stdout
