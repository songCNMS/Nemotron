from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = (
    REPO_ROOT
    / "usage-cookbook/Llama-3.1-Nemotron-Safety-Guard-V3/nim_cookbook.ipynb"
)

EXPECTED_REVISION = "a6fc06f7c3d28b84f3b5c2759ce2366dc8fac5de"
PINNED_LINK = (
    "https://github.com/NVIDIA-NeMo/Guardrails/blob/"
    f"{EXPECTED_REVISION}/docs/getting-started/installation-guide.md"
)
MUTABLE_LINK = (
    "https://github.com/NVIDIA-NeMo/Guardrails/blob/develop/"
    "docs/getting-started/installation-guide.md"
)


def _notebook() -> dict[str, object]:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _cell_source(cell: dict[str, object]) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def _notebook_source() -> str:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return "\n".join(
        _cell_source(cell) for cell in cells if isinstance(cell, dict)
    )


def test_safety_guard_v3_guardrails_install_link_is_revision_pinned() -> None:
    source = _notebook_source()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert source.count(PINNED_LINK) == 1
    assert MUTABLE_LINK not in source


def test_safety_guard_v3_guardrails_context_is_preserved() -> None:
    source = _notebook_source()

    expected_context = (
        "Deploy Nemotron Safety Guard Model and Integrate it with NeMo Guardrails",
        "Llama 3.1 Nemotron Safety Guard 8B V3",
        "NIM",
        "NeMo Guardrails",
        "## Prerequisites",
        "You [installed NeMo Guardrails]",
    )
    for marker in expected_context:
        assert marker in source


def test_safety_guard_v3_guardrails_link_cell_is_clear_markdown() -> None:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    matching_cells = [
        cell
        for cell in cells
        if isinstance(cell, dict) and PINNED_LINK in _cell_source(cell)
    ]

    assert len(matching_cells) == 1
    cell = matching_cells[0]
    assert cell["cell_type"] == "markdown"
    assert cell.get("execution_count") is None
    assert cell.get("outputs", []) == []
