"""Static checks for Omni3 self-repository documentation link pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NEMOTRON_REVISION = "89a6da531c4c693da585a7cc9ac96c51492bffa4"
NEMOTRON_REPO = "https://github.com/NVIDIA-NeMo/Nemotron"

SCOPED_OMNI3_DOCS = (
    REPO_ROOT / "docs/nemotron/omni3/README.md",
    REPO_ROOT / "docs/nemotron/omni3/sft.md",
    REPO_ROOT / "docs/nemotron/omni3/rl.md",
    REPO_ROOT / "docs/nemotron/omni3/architecture.md",
)

MUTABLE_SELF_REPO_PREFIXES = (
    f"{NEMOTRON_REPO}/tree/main/",
    f"{NEMOTRON_REPO}/blob/main/",
)
PINNED_SELF_REPO_URLS = {
    f"{NEMOTRON_REPO}/tree/{NEMOTRON_REVISION}/src/nemotron/recipes/data/sdg/long-document",
    f"{NEMOTRON_REPO}/blob/{NEMOTRON_REVISION}/designs/long-document-sdg-pipeline.md",
    f"{NEMOTRON_REPO}/tree/{NEMOTRON_REVISION}/src/nemotron/recipes/omni3/stage0_sft",
    f"{NEMOTRON_REPO}/blob/{NEMOTRON_REVISION}/src/nemotron/recipes/omni3/stage0_sft/README.md",
    f"{NEMOTRON_REPO}/tree/{NEMOTRON_REVISION}/src/nemotron/recipes/omni3/stage1_rl",
    f"{NEMOTRON_REPO}/blob/{NEMOTRON_REVISION}/src/nemotron/recipes/omni3/stage1_rl/README.md",
}

SELF_REPO_URL_RE = re.compile(
    r"https://github\.com/NVIDIA-NeMo/Nemotron/(tree|blob)/([^\s)#]+)"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_omni3_self_repo_doc_links_are_revision_pinned() -> None:
    assert re.fullmatch(r"[0-9a-f]{40}", NEMOTRON_REVISION)
    combined = "\n".join(_read(path) for path in SCOPED_OMNI3_DOCS)

    for mutable in MUTABLE_SELF_REPO_PREFIXES:
        assert mutable not in combined

    for expected_url in PINNED_SELF_REPO_URLS:
        assert expected_url in combined, expected_url

    for path in SCOPED_OMNI3_DOCS:
        rel_path = path.relative_to(REPO_ROOT)
        for _, revision_and_path in SELF_REPO_URL_RE.findall(_read(path)):
            assert revision_and_path.startswith(NEMOTRON_REVISION), rel_path


def test_omni3_self_repo_doc_links_preserve_context() -> None:
    readme = _read(REPO_ROOT / "docs/nemotron/omni3/README.md")
    architecture = _read(REPO_ROOT / "docs/nemotron/omni3/architecture.md")
    sft = _read(REPO_ROOT / "docs/nemotron/omni3/sft.md")
    rl = _read(REPO_ROOT / "docs/nemotron/omni3/rl.md")

    assert "[Long-document SDG guide](../data/sdg/long-document.md)" in readme
    assert "[guide](../data/sdg/long-document.md)" in architecture
    assert "[Architecture deep-dive](./architecture.md)" in sft
    assert "[RL data prep deep-dive](./rl/data-prep.md)" in rl
    assert "Long-document SDG" in readme
    assert "Recipe source" in sft
    assert "Recipe source" in rl
