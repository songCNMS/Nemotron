"""Static guards for pinned Embed pre-generated dataset README examples."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
README_PATHS = (
    REPO_ROOT / "docs/nemotron/embed/README.md",
    REPO_ROOT / "src/nemotron/recipes/embed/README.md",
)
DEFAULT_CONFIG = REPO_ROOT / "src/nemotron/recipes/embed/stage0_sdg/config/default.yaml"
DATASET_ID = "nvidia/Retrieval-Synthetic-NVDocs-v1"
UNPINNED_EXAMPLE = "load_dataset('nvidia/Retrieval-Synthetic-NVDocs-v1', split='train')"


def _default_corpus_revision() -> str:
    config = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    corpus_dir = config["corpus_dir"]
    match = re.fullmatch(
        rf"hf://{re.escape(DATASET_ID)}@(?P<revision>[0-9a-f]{{40}})"
        r"/sample_corpus/nv_pp_random",
        corpus_dir,
    )
    assert match, f"default corpus_dir is not a pinned {DATASET_ID} URI"
    return match.group("revision")


def test_embed_readmes_pin_pregenerated_dataset_revision_from_default_config() -> None:
    revision = _default_corpus_revision()
    pinned_call = re.compile(
        rf"load_dataset\(\s*"
        rf"['\"]{re.escape(DATASET_ID)}['\"],\s*"
        r"split\s*=\s*['\"]train['\"],\s*"
        rf"revision\s*=\s*['\"]{revision}['\"],\s*"
        r"\)",
        flags=re.DOTALL,
    )

    for readme_path in README_PATHS:
        text = readme_path.read_text(encoding="utf-8")
        assert UNPINNED_EXAMPLE not in text, f"{readme_path} has an unpinned example"
        assert pinned_call.search(text), (
            f"{readme_path} does not pin {DATASET_ID} to default config revision "
            f"{revision}"
        )
