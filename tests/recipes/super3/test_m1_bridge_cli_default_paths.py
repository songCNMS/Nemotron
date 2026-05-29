"""Static/import checks for M1 bridge CLI default output path portability."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_CASES = (
    (
        "nemotron.recipes.super3.milestones.m1_rlhf.prepare_m1_rlhf_jsonl",
        "src/nemotron/recipes/super3/milestones/m1_rlhf/prepare_m1_rlhf_jsonl.py",
        {"output_dir": Path("output/super3/m1_rlhf")},
    ),
    (
        "nemotron.recipes.super3.milestones.m1_rlvr.prepare_m1_rlvr_jsonl",
        "src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py",
        {"output_dir": Path("output/super3/m1_rlvr")},
    ),
    (
        "nemotron.recipes.super3.milestones.m1_swe1.prepare_m1_swe1_jsonl",
        "src/nemotron/recipes/super3/milestones/m1_swe1/prepare_m1_swe1_jsonl.py",
        {"output_dir": Path("output/super3/m1_swe1")},
    ),
    (
        "nemotron.recipes.super3.milestones.m1_swe2.prepare_m1_swe2_jsonl",
        "src/nemotron/recipes/super3/milestones/m1_swe2/prepare_m1_swe2_jsonl.py",
        {"output_dir": Path("output/super3/m1_swe2")},
    ),
    (
        "nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft",
        "src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py",
        {"output_dir": Path("output/super3/m1_agentic_sft_v0")},
    ),
    (
        "nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training",
        "src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py",
        {
            "output_dir": Path("output/super3/m1_agentic_sft_v0/train-plans"),
            "save_dir": Path("output/super3/m1_agentic_sft_v0/checkpoints"),
        },
    ),
)


def _reload_module(module_name: str):
    module = importlib.import_module(module_name)
    return importlib.reload(module)


@pytest.mark.parametrize(("module_name", "_source_path", "expected"), DEFAULT_CASES)
def test_m1_bridge_cli_defaults_use_nemo_run_dir_at_import(
    module_name: str,
    _source_path: str,
    expected: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("NEMO_RUN_DIR", str(tmp_path))
    module = _reload_module(module_name)

    if "output_dir" in expected:
        assert module.DEFAULT_OUTPUT_DIR == tmp_path / expected["output_dir"]
    if "save_dir" in expected:
        assert module.DEFAULT_SAVE_DIR == tmp_path / expected["save_dir"]


@pytest.mark.parametrize(("module_name", "_source_path", "expected"), DEFAULT_CASES)
def test_m1_bridge_cli_parser_defaults_use_nemo_run_dir_and_overrides_win(
    module_name: str,
    _source_path: str,
    expected: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("NEMO_RUN_DIR", str(tmp_path))
    module = _reload_module(module_name)
    parser = module.build_parser()

    args = parser.parse_args([])
    if "output_dir" in expected:
        assert args.output_dir == tmp_path / expected["output_dir"]
        override = tmp_path / "custom-output"
        override_args = parser.parse_args(["--output-dir", str(override)])
        assert override_args.output_dir == override
    if "save_dir" in expected:
        assert args.save_dir == tmp_path / expected["save_dir"]
        override = tmp_path / "custom-save"
        override_args = parser.parse_args(["--save-dir", str(override)])
        assert override_args.save_dir == override


@pytest.mark.parametrize(("_module_name", "source_path", "_expected"), DEFAULT_CASES)
def test_m1_bridge_cli_sources_do_not_keep_cwd_relative_output_defaults(
    _module_name: str,
    source_path: str,
    _expected: dict[str, Path],
) -> None:
    text = (REPO_ROOT / source_path).read_text(encoding="utf-8")

    assert 'DEFAULT_OUTPUT_DIR = Path("../output/super3/' not in text
    assert 'DEFAULT_SAVE_DIR = Path("../output/super3/' not in text
