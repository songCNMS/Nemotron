from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_REVISION = "98ba11c0a77e177a903cd3756570684437a08e8d"
EXPECTED_BRANCH = "nano-v3-omni"
NEMO_RL_REPO = "https://github.com/NVIDIA-NeMo/RL"
NOTEBOOKS = {
    "grpo": REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/grpo/grpo_training_cookbook.ipynb",
    "grpo_nemo_gym": REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/grpo_nemo_gym/grpo_nemo_gym_training_cookbook.ipynb",
}


def _notebook(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _cell_source(cell: dict[str, object]) -> str:
    value = cell.get("source", [])
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value)


def _notebook_source(path: Path) -> str:
    notebook = _notebook(path)
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return "\n".join(
        _cell_source(cell) for cell in cells if isinstance(cell, dict)
    )


def _nemo_rl_setup_cells(path: Path) -> list[dict[str, object]]:
    notebook = _notebook(path)
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [
        cell
        for cell in cells
        if isinstance(cell, dict)
        and NEMO_RL_REPO in _cell_source(cell)
        and "git clone" in _cell_source(cell)
    ]


def test_nano_omni_grpo_notebooks_pin_nemo_rl_checkout_revision() -> None:
    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)

    for path in NOTEBOOKS.values():
        setup_cells = _nemo_rl_setup_cells(path)
        assert len(setup_cells) == 1
        source = _cell_source(setup_cells[0])

        assert f"NEMO_RL_REVISION={EXPECTED_REVISION}" in source
        assert f"-b {EXPECTED_BRANCH} {NEMO_RL_REPO}" in source
        assert 'git checkout "$NEMO_RL_REVISION"' in source
        assert 'test "$(git rev-parse HEAD)" = "$NEMO_RL_REVISION"' in source
        assert "git submodule update --init --recursive" in source


def test_nano_omni_grpo_notebooks_have_no_unguarded_branch_only_clone() -> None:
    for path in NOTEBOOKS.values():
        for setup_cell in _nemo_rl_setup_cells(path):
            source = _cell_source(setup_cell)
            branch_only_clone = f"git clone --recursive -b {EXPECTED_BRANCH} {NEMO_RL_REPO}"

            assert branch_only_clone in source
            assert EXPECTED_REVISION in source
            assert 'git checkout "$NEMO_RL_REVISION"' in source
            assert 'test "$(git rev-parse HEAD)" = "$NEMO_RL_REVISION"' in source


def test_nano_omni_grpo_nemo_rl_setup_cells_have_cleared_outputs() -> None:
    for path in NOTEBOOKS.values():
        setup_cell = _nemo_rl_setup_cells(path)[0]

        assert setup_cell["cell_type"] == "code"
        assert setup_cell.get("outputs") == []
        assert setup_cell.get("execution_count") is None


def test_nano_omni_grpo_notebook_context_is_preserved() -> None:
    grpo_source = _notebook_source(NOTEBOOKS["grpo"])
    gym_source = _notebook_source(NOTEBOOKS["grpo_nemo_gym"])

    assert "# Nemotron Nano Omni V3 GRPO Training with NemoRL" in grpo_source
    assert "OpenGVLab/MMPR-Tiny" in grpo_source
    assert "vlm_grpo_nanov3omni_mmpr_tiny_1node.yaml" in grpo_source
    assert "# Nemotron Nano Omni V3 GRPO Training via NeMo Gym" in gym_source
    assert "OpenGVLab/MMPR-Tiny" in gym_source
    assert "grpo_mmpr_tiny_nanov3omni_gym.yaml" in gym_source
