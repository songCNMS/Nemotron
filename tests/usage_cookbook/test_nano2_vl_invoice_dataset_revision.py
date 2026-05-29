from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = REPO_ROOT / "usage-cookbook/Nemotron-Nano2-VL/build_general_usage_cookbook.ipynb"

DATASET_REPO = "katanaml-org/invoices-donut-data-v1"
EXPECTED_REVISION = "d2cde298e79c94fb05bc320999deb4b7889b0464"
PARQUET_FILENAME = "test-00000-of-00001-56af6bd5ff7eb34d.parquet"
EXPECTED_URL = (
    f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/"
    f"{EXPECTED_REVISION}/data/{PARQUET_FILENAME}"
)
FLOATING_URL = (
    f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/data/"
    f"{PARQUET_FILENAME}"
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


def _output_text(cell: dict[str, object]) -> str:
    chunks: list[str] = []
    outputs = cell.get("outputs", [])
    assert isinstance(outputs, list)
    for output in outputs:
        assert isinstance(output, dict)
        chunks.append(_cell_text(output, "text"))
        chunks.append(str(output.get("data", "")))
    return "".join(chunks)


def test_nano2_vl_invoice_parquet_url_is_revision_pinned() -> None:
    raw_text = NOTEBOOK.read_text(encoding="utf-8")

    assert raw_text.count(EXPECTED_URL) == 1
    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert FLOATING_URL not in raw_text


def test_nano2_vl_invoice_notebook_has_no_floating_main_invoice_urls() -> None:
    raw_text = NOTEBOOK.read_text(encoding="utf-8")
    invoice_urls = re.findall(
        rf"https://huggingface\.co/datasets/{re.escape(DATASET_REPO)}/"
        rf"(?:resolve|raw)/[^\\s\"']+/data/{re.escape(PARQUET_FILENAME)}",
        raw_text,
    )

    assert invoice_urls == [EXPECTED_URL]
    for url in invoice_urls:
        assert "/resolve/main/" not in url
        assert "/raw/main/" not in url
        assert "/main/" not in url


def test_nano2_vl_invoice_cell_is_present_and_outputs_are_cleared() -> None:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)

    invoice_cells = [
        cell
        for cell in cells
        if isinstance(cell, dict) and EXPECTED_URL in _cell_text(cell, "source")
    ]
    assert len(invoice_cells) == 1

    invoice_cell = invoice_cells[0]
    source = _cell_text(invoice_cell, "source")
    assert invoice_cell["cell_type"] == "code"
    assert invoice_cell.get("outputs") == []
    assert f"!wget {EXPECTED_URL}" in source
    assert f'pq.read_table("{PARQUET_FILENAME}")' in source
    assert "import pyarrow.parquet as pq" in source

    all_source = "".join(
        _cell_text(cell, "source") for cell in cells if isinstance(cell, dict)
    )
    assert "### Invoice Understanding" in all_source
    assert "Loading Invoices from hugging face dataset" in all_source


def test_nano2_vl_invoice_notebook_outputs_do_not_contain_stale_download_text() -> None:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    output_text = "".join(
        _output_text(cell) for cell in cells if isinstance(cell, dict)
    )

    assert FLOATING_URL not in output_text
    assert PARQUET_FILENAME not in output_text
    assert "cas-bridge.xethub.hf.co" not in output_text
