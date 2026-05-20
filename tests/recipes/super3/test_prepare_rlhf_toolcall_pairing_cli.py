"""Tests for the RLHF tool-call pairing CLI (task068 Session 3).

Covers:

- `prepare()` end-to-end against synthetic JSONL inputs writes
  `paired.jsonl` + `manifest.json` with lineage
- Output rows use M0 env name `rlhf_toolcall_paired` (not the NeMo-Gym
  env name) — so the M1 RLHF bridge picks them up via its env_map
- Manifest counts: helpsteer2_rows / hermes_rows / paired_rows
- `--eval-prompts-jsonl` optional; absent → empty set, no contamination
  filter
- CLI subprocess: exit 0 on success / exit 1 on missing input / exit 2
  on malformed JSONL
- rlhf_env_registry.yaml's tool-call row is now `active` with
  `m0_env_id: rlhf_toolcall_paired` (Session 3 flip)
- environment_registry.yaml carries the new `rlhf_toolcall_paired` env
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]
CLI_PATH = REPO_ROOT / "scripts" / "prepare_rlhf_toolcall_pairing.py"
RLHF_ENV_REGISTRY = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_rlhf/rlhf_env_registry.yaml"
)
M0_ENV_REGISTRY = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml"
)


def _write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8",
    )
    return path


def _helpsteer_row(prompt: str, row_id: str = "hs_1") -> dict:
    return {"id": row_id, "prompt": prompt}


def _hermes_row(function_name: str, arguments: dict, source_id: str) -> dict:
    return {
        "id": source_id,
        "expected_answer": {
            "tool_calls": [
                {"function": {"name": function_name, "arguments": arguments}}
            ]
        },
        "responses_create_params": {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "description": f"Mock {function_name}",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
        },
    }


# ---------- prepare() function ----------


def test_prepare_writes_paired_jsonl_and_manifest(tmp_path: Path) -> None:
    helpsteer_path = _write_jsonl(
        tmp_path / "helpsteer.jsonl",
        [
            _helpsteer_row("Look up the weather in Tokyo.", row_id="hs_1"),
            _helpsteer_row("Compose a haiku.", row_id="hs_2"),  # drops on relevance
        ],
    )
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [
            _hermes_row("get_weather", {"location": "X"}, source_id="h_1"),
        ],
    )
    output_dir = tmp_path / "out"

    from scripts.prepare_rlhf_toolcall_pairing import prepare

    args = SimpleNamespace(
        helpsteer2_jsonl=helpsteer_path,
        hermes_jsonl=hermes_path,
        eval_prompts_jsonl=None,
        output_dir=output_dir,
    )
    manifest = prepare(args)

    assert (output_dir / "paired.jsonl").is_file()
    assert (output_dir / "manifest.json").is_file()
    assert manifest["counts"]["helpsteer2_rows"] == 2
    assert manifest["counts"]["hermes_rows"] == 1
    assert manifest["counts"]["paired_rows"] == 1  # 1 dropped on relevance


def test_prepare_paired_rows_use_m0_env_name(tmp_path: Path) -> None:
    """Output rows must carry `environment: rlhf_toolcall_paired` so
    the M1 RLHF bridge maps them to the NeMo-Gym
    single_step_tool_use_with_argument_comparison via its env_map."""
    helpsteer_path = _write_jsonl(
        tmp_path / "helpsteer.jsonl",
        [_helpsteer_row("Look up the weather in Tokyo.")],
    )
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [_hermes_row("get_weather", {"location": "Tokyo"}, source_id="h_1")],
    )
    output_dir = tmp_path / "out"

    from scripts.prepare_rlhf_toolcall_pairing import prepare

    args = SimpleNamespace(
        helpsteer2_jsonl=helpsteer_path,
        hermes_jsonl=hermes_path,
        eval_prompts_jsonl=None,
        output_dir=output_dir,
    )
    prepare(args)

    rows = [
        json.loads(line)
        for line in (output_dir / "paired.jsonl").read_text().splitlines()
        if line
    ]
    assert len(rows) == 1
    assert rows[0]["environment"] == "rlhf_toolcall_paired"


def test_prepare_manifest_carries_lineage_block(tmp_path: Path) -> None:
    """Lineage block must declare both M0 manifests as inputs and the
    paired.jsonl as output — required for task030 audit + task069
    publisher to walk the chain."""
    helpsteer_path = _write_jsonl(
        tmp_path / "hs_split" / "train-split.jsonl",
        [_helpsteer_row("Look up the weather.")],
    )
    hermes_path = _write_jsonl(
        tmp_path / "hermes_split" / "train-split.jsonl",
        [_hermes_row("get_weather", {"location": "X"}, source_id="h_1")],
    )

    from scripts.prepare_rlhf_toolcall_pairing import prepare

    args = SimpleNamespace(
        helpsteer2_jsonl=helpsteer_path,
        hermes_jsonl=hermes_path,
        eval_prompts_jsonl=None,
        output_dir=tmp_path / "out",
    )
    manifest = prepare(args)

    lineage = manifest["lineage"]
    assert lineage["artifact_type"] == "RawDataArtifact"
    assert lineage["produced_by"] == "prepare_rlhf_toolcall_pairing.py"
    input_kinds = {inp["kind"] for inp in lineage["inputs"]}
    assert "manifest" in input_kinds
    # Both M0 manifests referenced
    assert len(lineage["inputs"]) == 2
    output_kinds = {out["kind"] for out in lineage["outputs"]}
    assert "rlhf_toolcall_paired_jsonl" in output_kinds


def test_prepare_optional_eval_prompts_jsonl(tmp_path: Path) -> None:
    """Operator provides eval-prompts JSONL → contamination filter
    activates. Provide a prompt that should be caught."""
    helpsteer_path = _write_jsonl(
        tmp_path / "helpsteer.jsonl",
        [_helpsteer_row("Translate the following passenger announcement now.")],
    )
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [_hermes_row("translate", {"text": "x"}, source_id="h_1")],
    )
    eval_prompts_path = _write_jsonl(
        tmp_path / "eval_prompts.jsonl",
        [{"prompt": "Please translate the following passenger announcement to Spanish."}],
    )

    from scripts.prepare_rlhf_toolcall_pairing import prepare

    args = SimpleNamespace(
        helpsteer2_jsonl=helpsteer_path,
        hermes_jsonl=hermes_path,
        eval_prompts_jsonl=eval_prompts_path,
        output_dir=tmp_path / "out",
    )
    manifest = prepare(args)
    assert manifest["counts"]["paired_rows"] == 0
    assert manifest["counts"]["eval_prompt_5grams"] > 0


def test_prepare_with_no_eval_prompts_skips_contamination_filter(tmp_path: Path) -> None:
    """No --eval-prompts-jsonl → empty set → contamination filter does
    nothing → prompt passes through."""
    helpsteer_path = _write_jsonl(
        tmp_path / "helpsteer.jsonl",
        [_helpsteer_row("Translate the following passenger announcement.")],
    )
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [_hermes_row("translate", {"text": "x"}, source_id="h_1")],
    )

    from scripts.prepare_rlhf_toolcall_pairing import prepare

    args = SimpleNamespace(
        helpsteer2_jsonl=helpsteer_path,
        hermes_jsonl=hermes_path,
        eval_prompts_jsonl=None,
        output_dir=tmp_path / "out",
    )
    manifest = prepare(args)
    assert manifest["counts"]["paired_rows"] == 1
    assert manifest["counts"]["eval_prompt_5grams"] == 0


# ---------- CLI subprocess ----------


def test_cli_subprocess_smoke_roundtrip(tmp_path: Path) -> None:
    helpsteer_path = _write_jsonl(
        tmp_path / "helpsteer.jsonl",
        [_helpsteer_row("Look up the weather.")],
    )
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [_hermes_row("get_weather", {"location": "X"}, source_id="h_1")],
    )
    output_dir = tmp_path / "out"

    proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--helpsteer2-jsonl",
            str(helpsteer_path),
            "--hermes-jsonl",
            str(hermes_path),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr}\nstdout: {proc.stdout}"
    assert (output_dir / "paired.jsonl").is_file()
    assert (output_dir / "manifest.json").is_file()


def test_cli_exits_1_on_missing_helpsteer_input(tmp_path: Path) -> None:
    """Missing input file → exit 1 (FileNotFoundError)."""
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [_hermes_row("get_weather", {"location": "X"}, source_id="h_1")],
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--helpsteer2-jsonl",
            str(tmp_path / "does_not_exist.jsonl"),
            "--hermes-jsonl",
            str(hermes_path),
            "--output-dir",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 1


def test_cli_exits_2_on_malformed_jsonl(tmp_path: Path) -> None:
    helpsteer_path = tmp_path / "helpsteer.jsonl"
    helpsteer_path.write_text("not valid JSON {", encoding="utf-8")
    hermes_path = _write_jsonl(
        tmp_path / "hermes.jsonl",
        [_hermes_row("get_weather", {"location": "X"}, source_id="h_1")],
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--helpsteer2-jsonl",
            str(helpsteer_path),
            "--hermes-jsonl",
            str(hermes_path),
            "--output-dir",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 2
    assert "malformed JSONL" in proc.stderr


# ---------- Registry integration ----------


def test_rlhf_env_registry_tool_call_row_now_active() -> None:
    """task068 Session 3 flips the row. Lock the new state so a future
    regression can't quietly flip it back."""
    data = yaml.safe_load(RLHF_ENV_REGISTRY.read_text(encoding="utf-8"))
    rows = [
        e for e in data["envs"]
        if e["nemo_gym_env"] == "single_step_tool_use_with_argument_comparison"
        and e["mix"] == "rlhf"
    ]
    assert len(rows) == 1
    row = rows[0]
    assert row["status"] == "active"
    assert row["m0_env_id"] == "rlhf_toolcall_paired"
    assert row["m0_verifier"] == "argument_match"


def test_m0_env_registry_carries_rlhf_toolcall_paired() -> None:
    data = yaml.safe_load(M0_ENV_REGISTRY.read_text(encoding="utf-8"))
    env = next(
        (e for e in data["environments"] if e["id"] == "rlhf_toolcall_paired"),
        None,
    )
    assert env is not None
    assert env["reward"]["verifier"] == "argument_match"
    assert env["family"] == "rlhf_preference"
    assert env["resources"]["max_turns"] == 1


def test_rlhf_bridge_env_map_picks_up_new_active_row() -> None:
    """`prepare_m1_rlhf_jsonl.RLHF_ENV_MAP` is derived from the
    registry at import time. After the flip, it must include the new
    active mapping."""
    from nemotron.recipes.super3.milestones.m1_rlhf.prepare_m1_rlhf_jsonl import (
        RLHF_ENV_MAP,
    )
    assert RLHF_ENV_MAP.get("rlhf_toolcall_paired") == (
        "single_step_tool_use_with_argument_comparison"
    )
