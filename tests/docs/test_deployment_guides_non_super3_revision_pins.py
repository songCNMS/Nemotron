"""Static checks for non-Super3 deployment-guide self-repo doc link pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DEPLOYMENT_GUIDES_DOC = REPO_ROOT / "docs/deployment-guides.md"
NEMOTRON_SHA = "a2adec564cace06edf9f1cd91ba174f4aa2429ec"
SCOPED_COOKBOOK_PATHS = {
    "Nemotron-3-Ultra-Base",
    "Nemotron-Nano2-VL",
    "Nemotron-Parse-v1.1",
}
MUTABLE_LINKS = {
    f"https://github.com/NVIDIA-NeMo/nemotron/tree/main/usage-cookbook/{path}"
    for path in SCOPED_COOKBOOK_PATHS
}
PINNED_LINKS = {
    f"https://github.com/NVIDIA-NeMo/nemotron/tree/{NEMOTRON_SHA}/usage-cookbook/{path}"
    for path in SCOPED_COOKBOOK_PATHS
}
SCOPED_URL_RE = re.compile(
    r"https://github\.com/NVIDIA-NeMo/nemotron/tree/([^/\s]+)/usage-cookbook/"
    r"(Nemotron-3-Ultra-Base|Nemotron-Nano2-VL|Nemotron-Parse-v1\.1)"
)


def test_deployment_guides_pin_non_super3_cookbook_links() -> None:
    text = DEPLOYMENT_GUIDES_DOC.read_text(encoding="utf-8")

    for mutable_link in MUTABLE_LINKS:
        assert mutable_link not in text
    for pinned_link in PINNED_LINKS:
        assert pinned_link in text

    matches = SCOPED_URL_RE.findall(text)
    assert len(matches) == len(SCOPED_COOKBOOK_PATHS)
    assert {revision for revision, _ in matches} == {NEMOTRON_SHA}
    assert {path for _, path in matches} == SCOPED_COOKBOOK_PATHS

    for expected_context in (
        "# Deployment Guides",
        "Nemotron 3 Ultra Base",
        "Nemotron Nano 2 VL",
        "Nemotron Parse v1.1",
        "Deployment guides, fine-tuning recipes, and agentic usage examples",
    ):
        assert expected_context in text
