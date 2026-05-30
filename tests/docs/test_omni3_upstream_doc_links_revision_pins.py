"""Static checks for Omni3 upstream documentation link revision pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MEGATRON_BRIDGE_SHA = "648756cb99eed872d9e577243495840b9395a6f7"
NEMO_RL_SHA = "98ba11c0a77e177a903cd3756570684437a08e8d"

SCOPED_DOCS = (
    REPO_ROOT / "docs/nemotron/omni3/README.md",
    REPO_ROOT / "docs/nemotron/omni3/architecture.md",
    REPO_ROOT / "docs/nemotron/omni3/sft.md",
    REPO_ROOT / "docs/nemotron/omni3/rl.md",
    REPO_ROOT / "src/nemotron/recipes/omni3/stage0_sft/README.md",
    REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/README.md",
)

MUTABLE_LINK_PATTERNS = (
    "https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/nemotron_3_omni/",
    "https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/nemotron_3_omni",
    "https://github.com/NVIDIA-NeMo/RL/blob/nano-v3-omni/",
    "https://github.com/NVIDIA-NeMo/RL/tree/nano-v3-omni",
)

PINNED_LINK_PATTERNS = {
    "megatron_bridge_blob": (
        "https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/"
        f"{MEGATRON_BRIDGE_SHA}/"
    ),
    "megatron_bridge_tree": (
        "https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/"
        f"{MEGATRON_BRIDGE_SHA}"
    ),
    "nemo_rl_blob": (
        "https://github.com/NVIDIA-NeMo/RL/blob/"
        f"{NEMO_RL_SHA}/"
    ),
    "nemo_rl_tree": (
        "https://github.com/NVIDIA-NeMo/RL/tree/"
        f"{NEMO_RL_SHA}"
    ),
}

URL_RE = re.compile(r"https://github\.com/NVIDIA-NeMo/(Megatron-Bridge|RL)/(blob|tree)/([^\s)#]+)")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_scoped_omni3_docs_pin_upstream_github_links() -> None:
    combined = "\n".join(_read(path) for path in SCOPED_DOCS)

    for mutable in MUTABLE_LINK_PATTERNS:
        assert mutable not in combined

    for name, pinned in PINNED_LINK_PATTERNS.items():
        assert pinned in combined, f"missing {name}: {pinned}"

    assert "nemotron_3_omni" in combined
    assert "nano-v3-omni" in combined

    for path in SCOPED_DOCS:
        text = _read(path)
        rel_path = path.relative_to(REPO_ROOT)
        for repo, link_type, revision in URL_RE.findall(text):
            if repo == "Megatron-Bridge" and link_type in {"blob", "tree"}:
                assert revision.startswith(MEGATRON_BRIDGE_SHA), rel_path
            if repo == "RL" and link_type in {"blob", "tree"}:
                assert revision.startswith(NEMO_RL_SHA), rel_path
