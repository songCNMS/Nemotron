from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MEGATRON_BRIDGE_REPO = "https://github.com/NVIDIA-NeMo/Megatron-Bridge.git"
NEMO_RL_REPO = "https://github.com/NVIDIA-NeMo/RL.git"
AUTOMODEL_REPO = "https://github.com/NVIDIA-NeMo/Automodel.git"

SUPER_V3_SHA = "f570c0529c81b57cb2ae909bd31a19408c7f4583"
NANO_V3_SHA = "1cedb0a9c5f79d2cd2b5226a86b794b9f0e048a8"
NEMO_RL_SUPER_V3_SHA = "bb0a7d43931950a74522e159f7117543a87b580b"
AUTOMODEL_NEMOTRON_OMNI_SHA = "7dfec6130ddf675cc9721d1619945dcc743f0095"

SUPER3_MEGATRON_BRIDGE_DOCS = (
    REPO_ROOT / "docs/nemotron/super3/pretrain.md",
    REPO_ROOT / "docs/nemotron/super3/sft.md",
    REPO_ROOT / "docs/nemotron/super3/quantization.md",
)
NANO3_MEGATRON_BRIDGE_DOCS = (
    REPO_ROOT / "docs/nemotron/nano3/pretrain.md",
    REPO_ROOT / "docs/nemotron/nano3/sft.md",
)
SUPER3_RL_DOC = REPO_ROOT / "docs/nemotron/super3/rl/index.md"
AUTOMODEL_COOKBOOK = (
    REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/automodel/automodel_training_cookbook.md"
)
SUPER3_UPSTREAM_DOC_LINK_SCOPE = (
    REPO_ROOT / "docs/nemotron/super3/README.md",
    REPO_ROOT / "docs/nemotron/super3/pretrain.md",
    REPO_ROOT / "docs/nemotron/super3/sft.md",
    REPO_ROOT / "docs/nemotron/super3/quantization.md",
    REPO_ROOT / "docs/nemotron/super3/rl/index.md",
    REPO_ROOT / "docs/nemotron/super3/rl/rlvr.md",
    REPO_ROOT / "docs/nemotron/super3/rl/rlhf.md",
    REPO_ROOT / "docs/nemotron/super3/rl/swe.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/README.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/README.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage2_swe2/README.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/README.md",
)

MUTABLE_SUPER3_UPSTREAM_LINKS = (
    "https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/super-v3/",
    "https://github.com/NVIDIA-NeMo/RL/blob/super-v3/",
)
PINNED_SUPER3_MEGATRON_BRIDGE_DOC_LINK = (
    "https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/"
    f"{SUPER_V3_SHA}/docs/models/llm/nemotron3-super.md"
)
PINNED_SUPER3_NEMO_RL_EXAMPLES_LINK = (
    "https://github.com/NVIDIA-NeMo/RL/blob/"
    f"{NEMO_RL_SUPER_V3_SHA}/examples/nemotron_3_super/README.md"
)
PINNED_SUPER3_NEMO_RL_GUIDE_LINK = (
    "https://github.com/NVIDIA-NeMo/RL/blob/"
    f"{NEMO_RL_SUPER_V3_SHA}/docs/guides/nemotron-3-super.md"
)

SUPER3_MEGATRON_BRIDGE_LINK_DOCS = (
    REPO_ROOT / "docs/nemotron/super3/README.md",
    REPO_ROOT / "docs/nemotron/super3/pretrain.md",
    REPO_ROOT / "docs/nemotron/super3/sft.md",
    REPO_ROOT / "docs/nemotron/super3/quantization.md",
)
SUPER3_NEMO_RL_EXAMPLES_LINK_DOCS = (
    REPO_ROOT / "docs/nemotron/super3/rl/index.md",
    REPO_ROOT / "docs/nemotron/super3/rl/rlvr.md",
    REPO_ROOT / "docs/nemotron/super3/rl/rlhf.md",
    REPO_ROOT / "docs/nemotron/super3/rl/swe.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/README.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/README.md",
)
SUPER3_NEMO_RL_GUIDE_LINK_DOCS = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/README.md",
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage2_swe2/README.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_lower_sha(value: str) -> None:
    assert re.fullmatch(r"[0-9a-f]{40}", value)


def _assert_checkout_pinned(path: Path, *, repo: str, branch: str, sha: str) -> None:
    text = _read(path)

    assert repo in text, f"{path} missing repo {repo}"
    assert branch in text, f"{path} missing branch context {branch}"
    assert sha in text, f"{path} missing pinned SHA {sha}"
    _assert_lower_sha(sha)
    assert re.search(rf"^git checkout {re.escape(sha)}(?:\s+#\s*{re.escape(branch)})?$", text, re.MULTILINE), (
        f"{path} does not checkout pinned {branch} SHA {sha}"
    )


def test_super3_megatron_bridge_docs_pin_super_v3_revision() -> None:
    for path in SUPER3_MEGATRON_BRIDGE_DOCS:
        _assert_checkout_pinned(
            path,
            repo=MEGATRON_BRIDGE_REPO,
            branch="super-v3",
            sha=SUPER_V3_SHA,
        )
        assert "git checkout super-v3" not in _read(path)


def test_super3_upstream_doc_links_pin_super_v3_revisions() -> None:
    _assert_lower_sha(SUPER_V3_SHA)
    _assert_lower_sha(NEMO_RL_SUPER_V3_SHA)
    scoped_text = "\n".join(_read(path) for path in SUPER3_UPSTREAM_DOC_LINK_SCOPE)

    assert "super-v3" in scoped_text

    for path in SUPER3_UPSTREAM_DOC_LINK_SCOPE:
        text = _read(path)
        for mutable_link in MUTABLE_SUPER3_UPSTREAM_LINKS:
            assert mutable_link not in text, f"{path} still uses {mutable_link}"

    for path in SUPER3_MEGATRON_BRIDGE_LINK_DOCS:
        assert PINNED_SUPER3_MEGATRON_BRIDGE_DOC_LINK in _read(path), path

    for path in SUPER3_NEMO_RL_EXAMPLES_LINK_DOCS:
        assert PINNED_SUPER3_NEMO_RL_EXAMPLES_LINK in _read(path), path

    for path in SUPER3_NEMO_RL_GUIDE_LINK_DOCS:
        assert PINNED_SUPER3_NEMO_RL_GUIDE_LINK in _read(path), path


def test_nano3_megatron_bridge_docs_pin_nano_v3_revision() -> None:
    for path in NANO3_MEGATRON_BRIDGE_DOCS:
        _assert_checkout_pinned(
            path,
            repo=MEGATRON_BRIDGE_REPO,
            branch="nano-v3",
            sha=NANO_V3_SHA,
        )
        assert "git checkout nano-v3" not in _read(path)


def test_super3_rl_doc_pins_nemo_rl_super_v3_revision() -> None:
    text = _read(SUPER3_RL_DOC)

    _assert_checkout_pinned(
        SUPER3_RL_DOC,
        repo=NEMO_RL_REPO,
        branch="super-v3",
        sha=NEMO_RL_SUPER_V3_SHA,
    )
    assert "git clone --recursive -b super-v3" in text
    assert "git submodule update --init --recursive" in text


def test_automodel_cookbook_pins_nemotron_omni_revision() -> None:
    text = _read(AUTOMODEL_COOKBOOK)

    _assert_checkout_pinned(
        AUTOMODEL_COOKBOOK,
        repo=AUTOMODEL_REPO,
        branch="nemotron-omni",
        sha=AUTOMODEL_NEMOTRON_OMNI_SHA,
    )
    assert "git clone -b nemotron-omni" in text
    assert "gitlab-master.nvidia.com" not in text
