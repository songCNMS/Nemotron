from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = REPO_ROOT / "usage-cookbook/Nemotron-3-Super/vllm_cookbook.ipynb"
PARSER_FILE = "super_v3_reasoning_parser.py"
EXPECTED_REVISIONS = {
    "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16": "d51eab0d1f979ebc26b546e634a04f450d99158e",
    "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8": "7d7e5797b8a3c7abbab54033b6004e93e8b6bc91",
    "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4": "4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6",
}
EXPECTED_URLS = [
    f"https://huggingface.co/{repo}/resolve/{revision}/{PARSER_FILE}"
    for repo, revision in EXPECTED_REVISIONS.items()
]


def _cookbook_text() -> str:
    notebook = json.loads(COOKBOOK.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )


def _reasoning_parser_wget_urls(text: str) -> list[str]:
    return re.findall(
        rf'wget\s+"(https://huggingface\.co/[^"]+/{PARSER_FILE})"',
        text,
    )


def test_vllm_cookbook_reasoning_parser_downloads_are_revision_pinned() -> None:
    urls = _reasoning_parser_wget_urls(_cookbook_text())

    assert urls == EXPECTED_URLS
    for url in urls:
        assert re.search(rf"/resolve/[0-9a-f]{{40}}/{PARSER_FILE}$", url)


def test_vllm_cookbook_reasoning_parser_downloads_have_no_floating_main_ref() -> None:
    text = _cookbook_text()

    assert f"/resolve/main/{PARSER_FILE}" not in text
    assert f"/raw/main/{PARSER_FILE}" not in text
    assert f"/main/{PARSER_FILE}" not in text


def test_vllm_cookbook_keeps_precision_sections_represented() -> None:
    text = _cookbook_text()

    expected_sections = (
        "#### BF16 (4x H100)",
        "#### FP8 (2x H100)",
        "#### NVFP4 (B200)",
    )
    for section in expected_sections:
        assert section in text
    for repo in EXPECTED_REVISIONS:
        assert f"vllm serve {repo}" in text
