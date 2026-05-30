"""Static checks for NVIDIA stack Megatron-Core documentation link pins."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

NVIDIA_STACK_DOC = REPO_ROOT / "docs/nemotron/nvidia-stack.md"
MEGATRON_CORE_SHA = "6e0d14a68e8defd1e2b65826a1d689b98bfdc62a"
MUTABLE_MEGATRON_CORE_LINK = (
    "https://github.com/NVIDIA/Megatron-LM/tree/main/megatron/core"
)
PINNED_MEGATRON_CORE_LINK = (
    "https://github.com/NVIDIA/Megatron-LM/tree/"
    f"{MEGATRON_CORE_SHA}/megatron/core"
)


def test_nvidia_stack_megatron_core_link_is_revision_pinned() -> None:
    text = NVIDIA_STACK_DOC.read_text(encoding="utf-8")

    assert MUTABLE_MEGATRON_CORE_LINK not in text
    assert text.count(PINNED_MEGATRON_CORE_LINK) == 1
    assert f"[Megatron-Core GitHub]({PINNED_MEGATRON_CORE_LINK})" in text


def test_nvidia_stack_megatron_core_context_is_preserved() -> None:
    text = NVIDIA_STACK_DOC.read_text(encoding="utf-8")

    for expected_context in (
        "# NVIDIA AI Stack",
        "## Megatron-Core",
        "### Documentation",
        "Megatron-Core provides the foundational primitives",
        "[Megatron-Core](https://github.com/NVIDIA/Megatron-LM)",
    ):
        assert expected_context in text
