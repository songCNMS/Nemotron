from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = (
    REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/doc-intelligence-with-parse/"
    / "doc_intelligence_cookbook.ipynb"
)

DATASET_REPO = "yubo2333/MMLongBench-Doc"
EXPECTED_REVISION = "2ff6aa9237fc777b6627dc57a486e9225ac5fb86"
EXPECTED_ROOT = (
    f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/"
    f"{EXPECTED_REVISION}/documents"
)
FLOATING_ROOT = (
    f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/documents"
)
EXPECTED_PDFS = {
    "05-03-18-political-release.pdf",
    "measuringsuccessonfacebooktwitterlinkedin-160317142140_95.pdf",
    "GPL-Graduate-Studies-Professional-Learning-Brochure-Jul-2021.pdf",
}


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


def test_doc_intelligence_mmlongbench_pdf_root_is_revision_pinned() -> None:
    source = _notebook_source()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert source.count(EXPECTED_ROOT) == 1
    assert FLOATING_ROOT not in source
    assert "MMLongBench-Doc/resolve/main/documents" not in source


def test_doc_intelligence_demo_pdf_registry_is_preserved() -> None:
    source = _notebook_source()

    for pdf_name in EXPECTED_PDFS:
        assert pdf_name in source
    assert 'name: f"{_HF_DOC_ROOT}/{name}" for name in {' in source
    assert "DEMO_DOCS" in source
    assert "_PDF_SOURCES" in source
    assert "def _ensure_pdf(pdf: Path) -> None:" in source
    assert "if pdf.exists():" in source


def test_doc_intelligence_pdf_setup_cell_outputs_are_cleared() -> None:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)

    setup_cells = [
        cell
        for cell in cells
        if isinstance(cell, dict) and EXPECTED_ROOT in _cell_source(cell)
    ]
    assert len(setup_cells) == 1

    setup_cell = setup_cells[0]
    assert setup_cell["cell_type"] == "code"
    assert setup_cell.get("execution_count") is None
    assert setup_cell.get("outputs") == []


def test_doc_intelligence_notebook_keeps_parse_and_nano_omni_context() -> None:
    source = _notebook_source()

    assert "# All-Modality Document AI with Nemotron Parse + Nemotron 3 Nano Omni" in source
    assert "nvidia/nemotron-parse" in source
    assert "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning" in source
    assert "page-cited, phrase-quoted answers" in source
