from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = REPO_ROOT / "usage-cookbook/Nemotron-Nano2-VL/vllm_cookbook.ipynb"

VLLM_REPO = "https://github.com/vllm-project/vllm.git"
EXPECTED_REVISION = "38b864d81d8bc42d6d7d892a0931f4c4c2517735"
EXPECTED_INSTALL = f"git+{VLLM_REPO}@{EXPECTED_REVISION}"
FLOATING_INSTALL = f"git+{VLLM_REPO}@main"


def _notebook() -> dict[str, object]:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _cell_source(cell: dict[str, object]) -> str:
    source = cell.get("source", [])
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


def test_nano2_vl_vllm_install_uses_exact_revision() -> None:
    source = _notebook_source()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert source.count(EXPECTED_INSTALL) == 1
    assert FLOATING_INSTALL not in source


def test_nano2_vl_vllm_install_cell_keeps_expected_context() -> None:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)

    install_cells = [
        cell
        for cell in cells
        if isinstance(cell, dict) and EXPECTED_INSTALL in _cell_source(cell)
    ]
    assert len(install_cells) == 1

    install_cell = install_cells[0]
    install_source = _cell_source(install_cell)
    assert install_cell["cell_type"] == "code"
    assert install_cell.get("outputs") == []
    assert "!VLLM_USE_PRECOMPILED=1 pip install " in install_source
    assert install_source.strip().endswith(EXPECTED_INSTALL)

    full_source = _notebook_source()
    assert "# Running NVIDIA Nemotron Nano 2 VL with vLLM" in full_source
    assert "nvidia/Nemotron-Nano-12B-v2-VL-BF16" in full_source
    assert "vllm serve nvidia/Nemotron-Nano-12B-v2-VL-BF16" in full_source


def test_nano2_vl_vllm_notebook_has_no_floating_main_install_ref() -> None:
    raw_text = NOTEBOOK.read_text(encoding="utf-8")

    assert "vllm-project/vllm.git@main" not in raw_text
    assert re.search(
        r"vllm-project/vllm\.git@[0-9a-f]{40}",
        raw_text,
    )
