"""Static checks for application-example self-repo doc link pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

APPLICATION_EXAMPLES_DOC = REPO_ROOT / "docs/application-examples.md"
NEMOTRON_SHA = "89a6da531c4c693da585a7cc9ac96c51492bffa4"
MUTABLE_USE_CASE_PREFIX = "https://github.com/NVIDIA-NeMo/nemotron/tree/main/use-case-examples/"
PINNED_USE_CASE_PREFIX = (
    "https://github.com/NVIDIA-NeMo/nemotron/tree/"
    f"{NEMOTRON_SHA}/use-case-examples/"
)
USE_CASE_URL_RE = re.compile(
    r"https://github\.com/NVIDIA-NeMo/nemotron/tree/([^/\s]+)/use-case-examples/([^\s]+)"
)

EXPECTED_EXAMPLE_PATHS = {
    "Nemotron-3-Super-Getting-Started-Guide",
    "sql-lora-finetuning-and-deployment",
    "Intelligent%20Document%20Processing%20with%20Nemotron%20RAG",
    "nemotron-voice-rag-agent-example",
    "Simple%20Nemotron-3-Nano%20Usage%20Example",
    "Data%20Science%20ML%20Agent",
    "RAG%20Agent%20with%20Nemotron%20RAG%20Models",
}


def test_application_examples_pin_use_case_links_to_repo_revision() -> None:
    text = APPLICATION_EXAMPLES_DOC.read_text(encoding="utf-8")

    assert MUTABLE_USE_CASE_PREFIX not in text
    matches = USE_CASE_URL_RE.findall(text)
    assert len(matches) == len(EXPECTED_EXAMPLE_PATHS)
    assert {revision for revision, _ in matches} == {NEMOTRON_SHA}
    assert {path for _, path in matches} == EXPECTED_EXAMPLE_PATHS
    assert text.count(PINNED_USE_CASE_PREFIX) == len(EXPECTED_EXAMPLE_PATHS)

    for expected_context in (
        "# Application Examples",
        "Nemotron 3 Super Getting Started Guide",
        "SQL LoRA Fine-tuning and Deployment",
        "Intelligent Document Processing",
        "Voice RAG Agent",
        "Simple Nemotron 3 Nano Usage",
        "Data Science ML Agent",
        "RAG Agent",
    ):
        assert expected_context in text
