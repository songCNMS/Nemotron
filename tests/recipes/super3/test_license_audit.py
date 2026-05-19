"""Tests for the share-alike license cascade audit (task058 Session 2).

Converts the ``docs/m0-dataset-expansion-plan.md`` §6 Q1 prose policy
into machine-checkable assertions. Covers:

- ``is_share_alike`` predicate (CC-BY-SA / GPL / AGPL / LGPL / ODBL
  families recognised; permissive licenses + empty / None inputs not)
- ``find_share_alike_sources`` walks the live m0_data / pref_data
  registries and surfaces HotpotQA (CC-BY-SA-4.0) today
- ``license_cascade`` traces source → m0 env → bridge mappings + flags
  live vs latent chains
- ``format_cascade_report`` text rendering for CLI consumption
- ``scripts/validate_data_registries.py --license-cascade`` end-to-end
  exit-zero + stdout content
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.data_registries.license_audit import (  # noqa: E402
    SHARE_ALIKE_LICENSE_PREFIXES,
    find_share_alike_sources,
    format_cascade_report,
    is_share_alike,
    license_cascade,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_data_registries.py"


# ---------- is_share_alike predicate ----------


@pytest.mark.parametrize(
    "license_str",
    [
        "cc-by-sa-4.0",
        "CC-BY-SA-4.0",
        "  cc-by-sa-3.0 ",
        "gpl-3.0",
        "AGPL-3.0",
        "lgpl-2.1",
        "odbl-1.0",
    ],
)
def test_share_alike_predicate_recognises_known_share_alike_licenses(license_str: str) -> None:
    assert is_share_alike(license_str)


@pytest.mark.parametrize(
    "license_str",
    [
        "cc-by-4.0",
        "cc-by-3.0",
        "apache-2.0",
        "mit",
        "bsd-3-clause",
        "license-pending-legal-review",
        "source-repository-specific",
        "",
        None,
        42,
    ],
)
def test_share_alike_predicate_rejects_permissive_and_invalid_inputs(license_str) -> None:
    assert not is_share_alike(license_str)


def test_share_alike_prefixes_carries_known_families() -> None:
    """Sanity check on the prefix table — adding a new family should
    require an explicit code change + test update."""
    assert "cc-by-sa" in SHARE_ALIKE_LICENSE_PREFIXES
    assert "gpl" in SHARE_ALIKE_LICENSE_PREFIXES
    assert "agpl" in SHARE_ALIKE_LICENSE_PREFIXES
    assert "odbl" in SHARE_ALIKE_LICENSE_PREFIXES


# ---------- find_share_alike_sources (live registries) ----------


def test_find_share_alike_sources_surfaces_hotpotqa_today() -> None:
    """HotpotQA ships in m0_data_registry.yaml as cc-by-sa-4.0. Once
    a permissive replacement is sourced (or HotpotQA is removed), this
    test flags the change so docs/m0-dataset-expansion-plan.md §6 Q1
    stays in sync."""
    matches = find_share_alike_sources()
    by_row_id = {row["row_id"]: row for row in matches}
    assert "m0_search_hotpotqa" in by_row_id, (
        f"expected HotpotQA flagged; got {sorted(by_row_id)}"
    )
    hotpot = by_row_id["m0_search_hotpotqa"]
    assert hotpot["license"] == "cc-by-sa-4.0"
    assert hotpot["kind"] == "m0_data_registry"
    assert hotpot["environment"] == "search_grounded_qa"
    assert hotpot["hf_dataset"] == "hotpotqa/hotpot_qa"


def test_find_share_alike_sources_skips_permissive_rows() -> None:
    """Sanity: rows like MBPP (cc-by-4.0) / GSM8K (mit) must NOT appear
    in the share-alike sweep."""
    matches = find_share_alike_sources()
    row_ids = {row["row_id"] for row in matches}
    # MBPP / GSM8K / NuminaMath / Hermes — none should be flagged.
    assert "m0_coding_mbpp" not in row_ids
    assert "m0_reasoning_gsm8k" not in row_ids
    assert "m0_math_numinamath" not in row_ids
    assert "m0_tool_calling_hermes" not in row_ids


# ---------- license_cascade walk ----------


def test_license_cascade_for_hotpotqa_is_latent_today() -> None:
    """task015 Session 1 audit removed the misnamed `search_grounded_qa`
    NeMo-Gym mapping, so no bridge row references HotpotQA's M0 env as
    `m0_env_id`. The cascade exists in source license but has zero live
    bridge chains — the audit must reflect that."""
    cascade = license_cascade()
    assert "m0_search_hotpotqa" in cascade
    hotpot_chain = cascade["m0_search_hotpotqa"]
    assert hotpot_chain["license"] == "cc-by-sa-4.0"
    assert hotpot_chain["m0_env_id"] == "search_grounded_qa"
    # Today: no bridge_env_registry row references search_grounded_qa
    # as m0_env_id (post-task015 audit), so the cascade is latent.
    assert hotpot_chain["live_chains"] == 0
    # bridge_mappings list is empty → no row references this M0 env.
    assert hotpot_chain["bridge_mappings"] == []


def test_license_cascade_distinguishes_live_from_latent(tmp_path: Path) -> None:
    """Synthetic fixture: one share-alike source with one *active* bridge
    mapping pointing at its M0 env → must report ``live_chains=1`` so
    operators can prioritise the share-alike review."""
    data_reg = tmp_path / "data_registry.yaml"
    data_reg.write_text(
        """schema_version: 1
milestone: M0
datasets:
  - id: stub_share_alike
    environment: stub_env
    hf_dataset: stub/dataset
    hf_split: train
    hf_revision: deadbeef
    license: cc-by-sa-4.0
    contamination_against: ["nothing"]
    converter: stub
    use_stage: ["M0 data_env_foundation"]
""",
        encoding="utf-8",
    )
    env_reg = tmp_path / "environment_registry.yaml"
    env_reg.write_text(
        """schema_version: 1
milestone: M0
environments:
  - id: stub_env
    family: stub
    stage: M0 data_env_foundation
    input_schema: nemo_gym_jsonl
    reward: {verifier: stub, range: [0, 1]}
    telemetry: [reward]
    health_check: {min_rows_per_split: 1}
""",
        encoding="utf-8",
    )
    bridge_reg = tmp_path / "rlvr_env_registry.yaml"
    bridge_reg.write_text(
        """schema_version: 1
milestone: M1
envs:
  - nemo_gym_env: stub_target
    mix: rlvr1
    m0_env_id: stub_env
    status: active
""",
        encoding="utf-8",
    )
    index = tmp_path / "unified_index.yaml"
    index.write_text(
        f"""schema_version: 1
milestone: M1
registries:
  - id: stub_m0_data
    kind: m0_data_registry
    path: {data_reg.name}
    summary: stub
  - id: stub_m0_env
    kind: m0_environment_registry
    path: {env_reg.name}
    summary: stub
  - id: stub_bridge
    kind: bridge_env_registry
    path: {bridge_reg.name}
    summary: stub
""",
        encoding="utf-8",
    )

    cascade = license_cascade(index)
    assert "stub_share_alike" in cascade
    chain = cascade["stub_share_alike"]
    assert chain["live_chains"] == 1
    assert len(chain["bridge_mappings"]) == 1
    mapping = chain["bridge_mappings"][0]
    assert mapping["status"] == "active"
    assert mapping["mix"] == "rlvr1"
    assert mapping["nemo_gym_env"] == "stub_target"


# ---------- format_cascade_report text rendering ----------


def test_format_cascade_report_empty_input_returns_clean_marker() -> None:
    text = format_cascade_report({})
    assert "no share-alike sources found" in text
    assert "✓" in text


def test_format_cascade_report_includes_license_and_chain_count() -> None:
    cascade = {
        "stub_source": {
            "registry_id": "stub_reg",
            "kind": "m0_data_registry",
            "license": "cc-by-sa-4.0",
            "hf_dataset": "stub/dataset",
            "m0_env_id": "stub_env",
            "bridge_mappings": [
                {
                    "registry_id": "m1_rlvr_envs",
                    "mix": "rlvr1",
                    "status": "active",
                    "nemo_gym_env": "stub_target",
                },
            ],
            "live_chains": 1,
        }
    }
    text = format_cascade_report(cascade)
    assert "stub_source" in text
    assert "cc-by-sa-4.0" in text
    assert "LIVE" in text  # live_chains > 0 → marked LIVE
    assert "1 active bridge mapping" in text
    assert "stub_target" in text


def test_format_cascade_report_marks_zero_live_as_latent() -> None:
    cascade = {
        "stub_source": {
            "registry_id": "stub_reg",
            "kind": "m0_data_registry",
            "license": "gpl-3.0",
            "hf_dataset": "stub/d",
            "m0_env_id": None,
            "bridge_mappings": [],
            "live_chains": 0,
        }
    }
    text = format_cascade_report(cascade)
    assert "latent" in text
    assert "no bridge references" in text


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


def test_license_cascade_cli_exits_zero_with_audit_on_stdout() -> None:
    """``--license-cascade`` is informational — exit 0 even when
    findings exist; report on stdout (so it pipes cleanly to less / file)."""
    result = _run_script("--license-cascade")
    assert result.returncode == 0, result.stderr
    assert "license-cascade audit" in result.stdout
    # HotpotQA is the live share-alike row today.
    assert "m0_search_hotpotqa" in result.stdout
    assert "cc-by-sa-4.0" in result.stdout
    # Stderr should stay clean — the audit shouldn't emit warnings on
    # a successful run.
    assert result.stderr == ""


def test_license_cascade_cli_short_circuits_validation() -> None:
    """When ``--license-cascade`` is set, the script must NOT run the
    schema validator pass (avoids redundant work + makes the audit
    output the only thing on stdout)."""
    result = _run_script("--license-cascade")
    assert result.returncode == 0
    # 验证 success line from the default validation path isn't present.
    assert "all registries clean" not in result.stdout
