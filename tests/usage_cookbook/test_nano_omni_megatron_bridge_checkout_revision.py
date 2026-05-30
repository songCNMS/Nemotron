from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = (
    REPO_ROOT
    / "usage-cookbook"
    / "Nemotron-3-Nano-Omni/Megatron-bridge/mbridge_lora_cord_v2_cookbook.ipynb"
)

MEGATRON_BRIDGE_REPO = "https://github.com/NVIDIA-NeMo/Megatron-Bridge.git"
EXPECTED_BRANCH = "nemotron_3_omni"
STALE_BRANCH = "nemotron-3-omni"
EXPECTED_REVISION = "648756cb99eed872d9e577243495840b9395a6f7"
EXPECTED_EXAMPLES_URL = (
    "https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/"
    f"{EXPECTED_REVISION}/examples/models/vlm/nemotron_3_omni"
)
STALE_EXAMPLES_URL = (
    "https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/"
    f"{EXPECTED_BRANCH}/examples/models/vlm/nemotron_3_omni"
)


def _notebook() -> dict[str, object]:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _cell_text(cell: dict[str, object], key: str) -> str:
    value = cell.get(key, [])
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value)


def _notebook_source() -> str:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return "\n".join(
        _cell_text(cell, "source") for cell in cells if isinstance(cell, dict)
    )


def _megatron_bridge_setup_cells() -> list[dict[str, object]]:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [
        cell
        for cell in cells
        if isinstance(cell, dict)
        and MEGATRON_BRIDGE_REPO in _cell_text(cell, "source")
    ]


def _cells_containing(marker: str) -> list[dict[str, object]]:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [
        cell
        for cell in cells
        if isinstance(cell, dict) and marker in _cell_text(cell, "source")
    ]


def test_nano_omni_megatron_bridge_setup_uses_exact_revision() -> None:
    setup_cells = _megatron_bridge_setup_cells()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert len(setup_cells) == 1
    setup_source = _cell_text(setup_cells[0], "source")
    assert EXPECTED_REVISION in setup_source
    assert "MEGATRON_BRIDGE_REVISION" in setup_source
    assert 'git checkout "${MEGATRON_BRIDGE_REVISION}"' in setup_source
    assert 'test "$(git rev-parse HEAD)" = "${MEGATRON_BRIDGE_REVISION}"' in setup_source


def test_nano_omni_megatron_bridge_branch_context_is_corrected() -> None:
    source = _notebook_source()
    setup_source = _cell_text(_megatron_bridge_setup_cells()[0], "source")

    assert EXPECTED_BRANCH in source
    assert f"`{EXPECTED_BRANCH}` branch context" in source
    assert EXPECTED_EXAMPLES_URL in source
    assert f'git clone -b "${{MEGATRON_BRIDGE_BRANCH}}" {MEGATRON_BRIDGE_REPO}' in setup_source
    assert f"MEGATRON_BRIDGE_BRANCH={EXPECTED_BRANCH}" in setup_source
    assert STALE_BRANCH not in source


def test_nano_omni_megatron_bridge_examples_link_is_pinned() -> None:
    source = _notebook_source()

    assert EXPECTED_EXAMPLES_URL in source
    assert STALE_EXAMPLES_URL not in source


def test_nano_omni_megatron_bridge_examples_link_cell_is_clear() -> None:
    cells = _cells_containing(EXPECTED_EXAMPLES_URL)

    assert len(cells) == 1
    cell = cells[0]
    assert cell["cell_type"] == "markdown"
    assert cell.get("execution_count") is None
    assert cell.get("outputs", []) == []


def test_nano_omni_megatron_bridge_setup_cell_is_guarded_and_outputs_clear() -> None:
    setup_cells = _megatron_bridge_setup_cells()

    assert len(setup_cells) == 1
    setup_cell = setup_cells[0]
    setup_source = _cell_text(setup_cell, "source")
    assert setup_cell["cell_type"] == "code"
    assert setup_cell.get("outputs") == []
    assert "git fetch origin" in setup_source
    assert "git rev-parse HEAD" in setup_source
    assert "git submodule update --init --recursive --depth 1" in setup_source


def test_nano_omni_megatron_bridge_context_is_preserved() -> None:
    source = _notebook_source()

    expected_context = (
        "# Nemotron-3 Omni LoRA Fine-Tuning on CORD-v2 with Megatron Bridge",
        "Setup — Clone and Install Megatron-Bridge",
        "**CORD-v2** receipt-parsing dataset",
        "LoRA PEFT fine-tuning",
        "## Step 4 — Launch Training",
    )
    for marker in expected_context:
        assert marker in source
