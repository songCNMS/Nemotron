"""Static checks for long-document SDG self-repo doc link pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

LONG_DOCUMENT_DOC = REPO_ROOT / "docs/nemotron/data/sdg/long-document.md"
NEMOTRON_SHA = "306b2f1217e000b5972155c1f2b1ba6660c994bd"
RECIPE_PATH = "src/nemotron/recipes/data/sdg/long-document"
MUTABLE_PREFIX = f"https://github.com/NVIDIA/nemotron/tree/main/{RECIPE_PATH}"
PINNED_PREFIX = f"https://github.com/NVIDIA/nemotron/tree/{NEMOTRON_SHA}/{RECIPE_PATH}"
SCOPED_URL_RE = re.compile(
    r"https://github\.com/NVIDIA/nemotron/tree/([^/\s]+)/"
    + re.escape(RECIPE_PATH)
    + r"(/deployment)?"
)


def test_sdg_long_document_self_repo_links_are_pinned() -> None:
    text = LONG_DOCUMENT_DOC.read_text(encoding="utf-8")

    assert MUTABLE_PREFIX not in text
    assert text.count(PINNED_PREFIX) == 3

    matches = SCOPED_URL_RE.findall(text)
    assert len(matches) == 3
    assert {revision for revision, _ in matches} == {NEMOTRON_SHA}
    assert [suffix for _, suffix in matches].count("") == 2
    assert [suffix for _, suffix in matches].count("/deployment") == 1

    for expected_context in (
        "# Long-Document SDG",
        "long-document SDG recipe",
        "nemotron data sdg long-document",
        "Recipe README",
        "Deployment config schema",
        "MMLongBench-Doc",
    ):
        assert expected_context in text
