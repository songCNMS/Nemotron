from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_REVISION = "89a6da531c4c693da585a7cc9ac96c51492bffa4"
SUPER3_README = REPO_ROOT / "usage-cookbook/Nemotron-3-Super/README.md"
DEPLOYMENT_GUIDES = REPO_ROOT / "docs/deployment-guides.md"

README_PINNED_LINKS = (
    "https://github.com/NVIDIA-NeMo/Nemotron/blob/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/SparkDeploymentGuide/README.md",
    "https://github.com/NVIDIA-NeMo/Nemotron/blob/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/grpo-dapo/README.md",
    "https://github.com/NVIDIA-NeMo/Nemotron/blob/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/lora-text2sql/README.md",
    "https://github.com/NVIDIA-NeMo/Nemotron/blob/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/OpenScaffoldingResources/README.md",
)

DEPLOYMENT_GUIDE_PINNED_LINKS = (
    "https://github.com/NVIDIA-NeMo/nemotron/tree/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super",
    "https://github.com/NVIDIA-NeMo/nemotron/tree/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/lora-text2sql",
    "https://github.com/NVIDIA-NeMo/nemotron/tree/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/SparkDeploymentGuide",
    "https://github.com/NVIDIA-NeMo/nemotron/tree/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/grpo-dapo",
    "https://github.com/NVIDIA-NeMo/nemotron/tree/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/OpenScaffoldingResources",
)

SCOPED_MUTABLE_MAIN_RE = re.compile(
    r"https://github\.com/NVIDIA-NeMo/[Nn]emotron/(?:blob|tree)/main/"
    r"usage-cookbook/Nemotron-3-Super(?:[^\s)]+)?"
)
SCOPED_PINNED_URL_RE = re.compile(
    rf"https://github\.com/NVIDIA-NeMo/[Nn]emotron/(?:blob|tree)/{EXPECTED_REVISION}/"
    r"usage-cookbook/Nemotron-3-Super(?:[^\s)]+)?"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_super3_cookbook_index_self_repo_links_are_pinned() -> None:
    text = _read(SUPER3_README)

    for pinned_link in README_PINNED_LINKS:
        assert pinned_link in text

    assert not SCOPED_MUTABLE_MAIN_RE.findall(text)
    assert len(SCOPED_PINNED_URL_RE.findall(text)) == len(README_PINNED_LINKS)


def test_deployment_guides_super3_self_repo_links_are_pinned() -> None:
    text = _read(DEPLOYMENT_GUIDES)

    for pinned_link in DEPLOYMENT_GUIDE_PINNED_LINKS:
        assert f":link: {pinned_link}" in text

    assert not SCOPED_MUTABLE_MAIN_RE.findall(text)
    assert len(SCOPED_PINNED_URL_RE.findall(text)) == len(DEPLOYMENT_GUIDE_PINNED_LINKS)


def test_super3_cookbook_doc_link_context_is_preserved() -> None:
    combined = _read(SUPER3_README) + "\n" + _read(DEPLOYMENT_GUIDES)

    expected_context = (
        "Nemotron-3-Super Notebooks",
        "SparkDeploymentGuide",
        "grpo-dapo",
        "lora-text2sql",
        "OpenScaffoldingResources",
        "Nemotron 3 Super on DGX Spark",
        "Nemotron 3 Super on GRPO/DAPO RL Training",
        "Nemotron 3 Super on Agentic Coding",
    )
    for marker in expected_context:
        assert marker in combined


def test_non_super3_deployment_guide_links_remain_unscoped() -> None:
    text = _read(DEPLOYMENT_GUIDES)

    unscoped_links = (
        "https://github.com/NVIDIA-NeMo/nemotron/tree/main/usage-cookbook/Nemotron-3-Ultra-Base",
        "https://github.com/NVIDIA-NeMo/nemotron/tree/main/usage-cookbook/Nemotron-Nano2-VL",
        "https://github.com/NVIDIA-NeMo/nemotron/tree/main/usage-cookbook/Nemotron-Parse-v1.1",
    )
    for link in unscoped_links:
        assert link in text
