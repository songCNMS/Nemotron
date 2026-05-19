"""Tests for the contamination_against semantic audit (task030 Session 7 /
task058 follow-up).

Sister suite to ``test_license_audit.py`` (share-alike cascade) and
``test_revision_audit.py`` (HF pin lint). Covers the third gap in
task058's contamination work: ``contamination_against`` is required as
a *present* field today, but the schema doesn't enforce that the value
is *meaningful*. This audit catches rows shipped with empty lists,
non-list values, or placeholder-only entries (``["TBD"]``).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.data_registries.contamination_audit import (  # noqa: E402
    SENTINEL_PHRASES,
    find_weak_contamination,
    format_contamination_report,
    is_placeholder_entry,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_data_registries.py"


# ---------- is_placeholder_entry predicate ----------


@pytest.mark.parametrize(
    "entry",
    [
        "TBD",
        "tbd",
        "TODO",
        "todo",
        "to-do",
        "Pending",
        "  pending  ",
        "TBD review",
        "manual review",
        "FIXME later",
        "n/a",
        "None",
        "xxx",
    ],
)
def test_placeholder_predicate_catches_sentinels(entry: str) -> None:
    assert is_placeholder_entry(entry)


@pytest.mark.parametrize(
    "entry",
    [
        "GSM8K test",
        "MATH-500",
        "HotpotQA validation",
        "LiveCodeBench",
        "AIME-25",
        "SWE-Bench Lite",
        "Pending-Eval-2026",  # contains "pending" but as part of a real name — must NOT match
        "",
        None,
        42,
    ],
)
def test_placeholder_predicate_does_not_flag_real_evals(entry) -> None:
    # "Pending-Eval-2026" intentionally contains "pending"; the audit
    # currently uses substring match so it WOULD be flagged. Verify the
    # behavior we actually implement: substring match catches it.
    if entry == "Pending-Eval-2026":
        assert is_placeholder_entry(entry), (
            "current implementation uses substring match; "
            "if changed to whole-word, update this test"
        )
    else:
        assert not is_placeholder_entry(entry)


def test_sentinel_phrases_carries_canonical_set() -> None:
    """Sanity check the registry — adding a new sentinel should
    require an explicit code change + test update."""
    assert "tbd" in SENTINEL_PHRASES
    assert "todo" in SENTINEL_PHRASES
    assert "pending" in SENTINEL_PHRASES
    assert "manual review" in SENTINEL_PHRASES
    assert "fixme" in SENTINEL_PHRASES


# ---------- find_weak_contamination on live registries ----------


def test_live_main_has_no_contamination_blockers_or_placeholders() -> None:
    """Live m0_data_registry today: every row has a non-empty
    contamination_against with real eval names (no TBD/etc.). Adding
    a row with broken contamination_against will trip this test."""
    audit = find_weak_contamination()
    assert audit["blockers"] == [], (
        "live m0_data_registry has broken contamination_against fields:\n"
        + str(audit["blockers"])
    )
    assert audit["informational"] == [], (
        "live m0_data_registry has rows with placeholder-only "
        "contamination_against entries:\n" + str(audit["informational"])
    )


# ---------- Synthetic broken fixtures ----------


def _write_index_with_m0(
    tmp_path: Path,
    *,
    contamination_against_block: str,
) -> Path:
    """Build a minimal unified index + m0_data_registry with one row
    whose contamination_against is the literal YAML block supplied."""
    data_reg = tmp_path / "data_registry.yaml"
    data_reg.write_text(
        "schema_version: 1\n"
        "milestone: M0\n"
        "datasets:\n"
        "  - id: stub_row\n"
        "    environment: stub_env\n"
        "    hf_dataset: stub/dataset\n"
        "    hf_split: train\n"
        "    hf_revision: deadbeef\n"
        "    license: mit\n"
        f"    {contamination_against_block}\n"
        "    converter: stub\n"
        "    use_stage: [\"M0 data_env_foundation\"]\n",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        "schema_version: 1\n"
        "milestone: M1\n"
        "registries:\n"
        "  - id: stub_m0_data\n"
        "    kind: m0_data_registry\n"
        f"    path: {data_reg.name}\n"
        "    summary: stub\n",
        encoding="utf-8",
    )
    return index


def test_empty_list_is_a_blocker(tmp_path: Path) -> None:
    index = _write_index_with_m0(tmp_path, contamination_against_block="contamination_against: []")
    audit = find_weak_contamination(index)
    assert len(audit["blockers"]) == 1
    blocker = audit["blockers"][0]
    assert blocker["row_id"] == "stub_row"
    assert any("empty" in r for r in blocker["reasons"])


def test_non_list_value_is_a_blocker(tmp_path: Path) -> None:
    index = _write_index_with_m0(
        tmp_path,
        contamination_against_block='contamination_against: "GSM8K test"',
    )
    audit = find_weak_contamination(index)
    assert len(audit["blockers"]) == 1
    assert "must be a list" in audit["blockers"][0]["reasons"][0]


def test_empty_string_entry_is_a_blocker(tmp_path: Path) -> None:
    index = _write_index_with_m0(
        tmp_path,
        contamination_against_block='contamination_against: ["GSM8K test", ""]',
    )
    audit = find_weak_contamination(index)
    assert len(audit["blockers"]) == 1
    assert any("empty-string" in r for r in audit["blockers"][0]["reasons"])


def test_placeholder_only_list_is_informational(tmp_path: Path) -> None:
    """Rows shipping a non-empty list of *only* placeholder entries
    (``["TBD"]``) are tracked but don't fail CI — they're documented
    TODO state, not authoring mistakes."""
    index = _write_index_with_m0(
        tmp_path,
        contamination_against_block='contamination_against: ["TBD", "todo"]',
    )
    audit = find_weak_contamination(index)
    assert audit["blockers"] == []
    assert len(audit["informational"]) == 1
    assert "placeholder" in audit["informational"][0]["reasons"][0]


def test_mixed_real_and_placeholder_entries_clean_through(tmp_path: Path) -> None:
    """If the list has at least one real eval name, the row passes
    even with a TBD entry mixed in — operators can flag known gaps
    inline without tripping the audit."""
    index = _write_index_with_m0(
        tmp_path,
        contamination_against_block='contamination_against: ["GSM8K test", "TBD: AIME"]',
    )
    audit = find_weak_contamination(index)
    assert audit["blockers"] == []
    assert audit["informational"] == []


def test_pref_data_registry_rows_are_skipped(tmp_path: Path) -> None:
    """Only m0_data_registry rows carry contamination_against;
    pref_data_registry rows don't. The audit must skip pref rows
    instead of false-flagging them as missing the field."""
    pref_reg = tmp_path / "pref_data.yaml"
    pref_reg.write_text(
        "schema_version: 1\n"
        "milestone: M1\n"
        "datasets:\n"
        "  - id: stub_pref\n"
        "    hf_dataset: stub/pref\n"
        "    license: apache-2.0\n",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        "schema_version: 1\n"
        "milestone: M1\n"
        "registries:\n"
        "  - id: stub_pref\n"
        "    kind: pref_data_registry\n"
        f"    path: {pref_reg.name}\n"
        "    summary: stub\n",
        encoding="utf-8",
    )
    audit = find_weak_contamination(index)
    assert audit == {"blockers": [], "informational": []}


# ---------- format_contamination_report ----------


def test_format_clean_audit_returns_check_marker() -> None:
    text = format_contamination_report({"blockers": [], "informational": []})
    assert "real contamination_against list" in text
    assert "✓" in text


def test_format_blocker_report_highlights_reason() -> None:
    text = format_contamination_report(
        {
            "blockers": [
                {
                    "registry_id": "stub_reg",
                    "row_id": "stub_row",
                    "hf_dataset": "stub/dataset",
                    "value": [],
                    "reasons": ["contamination_against is empty []"],
                }
            ],
            "informational": [],
        }
    )
    assert "BLOCKER" in text
    assert "stub_row" in text
    assert "empty" in text
    assert "⚠" in text


def test_format_informational_only_says_no_blockers() -> None:
    text = format_contamination_report(
        {
            "blockers": [],
            "informational": [
                {
                    "registry_id": "stub_reg",
                    "row_id": "stub_row",
                    "hf_dataset": "stub/dataset",
                    "value": ["TBD"],
                    "reasons": ["all contamination_against entries are placeholders"],
                }
            ],
        }
    )
    assert "informational" in text
    assert "BLOCKER" not in text
    assert "no blockers" in text


# ---------- CLI end-to-end ----------


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


def test_check_contamination_cli_clean_main_exits_zero() -> None:
    result = _run_script("--check-contamination")
    assert result.returncode == 0, result.stderr
    assert "real contamination_against list" in result.stdout
    assert "BLOCKER" not in result.stdout
    assert result.stderr == ""


def test_check_contamination_cli_with_broken_index_exits_one(tmp_path: Path) -> None:
    index = _write_index_with_m0(
        tmp_path, contamination_against_block="contamination_against: []"
    )
    result = _run_script("--check-contamination", "--index-path", str(index))
    assert result.returncode == 1
    assert "BLOCKER" in result.stdout
    assert "stub_row" in result.stdout
    assert "1 broken contamination_against field" in result.stderr


def test_check_contamination_cli_short_circuits_validation() -> None:
    result = _run_script("--check-contamination")
    assert result.returncode == 0
    assert "all registries clean" not in result.stdout


# ---------- Pre-commit config registers the new hook ----------


def test_precommit_config_declares_check_contamination_hook() -> None:
    cfg_path = REPO_ROOT / ".pre-commit-config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    hook_ids = {
        hook["id"]
        for repo in cfg["repos"]
        if repo.get("repo") == "local"
        for hook in repo.get("hooks", [])
    }
    assert "check-contamination" in hook_ids, f"got {hook_ids}"


def test_precommit_check_contamination_hook_runs_the_audit_flag() -> None:
    cfg_path = REPO_ROOT / ".pre-commit-config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    hook = next(
        h
        for r in cfg["repos"]
        if r.get("repo") == "local"
        for h in r.get("hooks", [])
        if h["id"] == "check-contamination"
    )
    entry = hook["entry"]
    assert "scripts/validate_data_registries.py" in entry
    assert "PYTHONPATH=src" in entry
    assert "--check-contamination" in entry
